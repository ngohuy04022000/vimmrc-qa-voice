"""Suy luận Matcha-TTS tiếng Việt (Mehta et al., "Matcha-TTS: A fast TTS architecture with conditional
flow matching", ICASSP 2024).

- Mô hình: checkpoints/matcha_vi.pt, xuất từ notebooks/train_matcha.ipynb (đã kèm bộ token trong file).
- Vocoder: checkpoints/matcha_vi_hifigan.pt (HiFi-GAN fine-tune theo mô hình) nếu có, ngược lại
  HiFi-GAN Universal (tự tải về checkpoints/hifigan_universal.pt).
- Văn bản được sinh theo từng cụm dấu câu rồi ghép với khoảng lặng để có nhịp ngắt nghỉ tự nhiên.
"""

import os
import re
import sys
import time
from typing import List, Optional, Tuple

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

import numpy as np
import soundfile as sf
import torch

# Đảm bảo import được Matcha-TTS từ thư mục con
_current_dir = os.path.dirname(os.path.abspath(__file__))
_root_dir = os.path.dirname(_current_dir)
_matcha_dir = os.path.join(_root_dir, "Matcha-TTS")
if _matcha_dir not in sys.path and os.path.exists(_matcha_dir):
    sys.path.insert(0, _matcha_dir)

try:
    from .normalizer import normalize_vietnamese_text
    from .vi_tokenizer import text_to_tokens, tokens_to_ids
except ImportError:
    from normalizer import normalize_vietnamese_text
    from vi_tokenizer import text_to_tokens, tokens_to_ids


CHECKPOINT_DIR = os.path.join(_root_dir, "checkpoints")
DEFAULT_CHECKPOINT = os.path.join(CHECKPOINT_DIR, "matcha_vi.pt")
UNIVERSAL_VOCODER = os.path.join(CHECKPOINT_DIR, "hifigan_universal.pt")
# Khoảng lặng (giây) chèn sau cụm, theo dấu câu kết thúc cụm
PHRASE_PAUSES = {",": 0.15, ";": 0.25, ":": 0.25, ".": 0.4, "!": 0.4, "?": 0.4, "…": 0.4, "\n": 0.45}


class MatchaTTSEngine:
    """Engine Matcha-TTS: nạp mô hình ở lần tổng hợp đầu tiên rồi dùng lại."""

    HIFIGAN_UNIV_URL = "https://github.com/shivammehta25/Matcha-TTS-checkpoints/releases/download/v1.0/g_02500000"

    def __init__(
        self,
        checkpoint_path: Optional[str] = None,
        vocoder_path: Optional[str] = None,
        device: Optional[str] = None,
    ):
        """Khai báo đường dẫn tài nguyên; mô hình chỉ được nạp ở lần tổng hợp đầu tiên.

        Args:
            checkpoint_path: File .pt của Matcha-TTS. None: checkpoints/matcha_vi.pt.
            vocoder_path: Trọng số HiFi-GAN. None: `<checkpoint>_hifigan.pt` nếu có, ngược lại bản Universal.
            device: 'cuda' hoặc 'cpu'. None: tự chọn.
        """
        self.device = device if device else ("cuda" if torch.cuda.is_available() else "cpu")
        self.sample_rate = 22050
        self.checkpoint_path = checkpoint_path or DEFAULT_CHECKPOINT
        paired_vocoder = os.path.splitext(self.checkpoint_path)[0] + "_hifigan.pt"
        self.vocoder_path = vocoder_path or (paired_vocoder if os.path.exists(paired_vocoder) else UNIVERSAL_VOCODER)

        self.model = None
        self.vocoder = None
        self.denoiser = None
        self.symbol2id = {}
        self.keep_punctuation = False

    def _ensure_model_loaded(self) -> None:
        """Nạp vocoder và mô hình Matcha-TTS (một lần).

        Raises:
            FileNotFoundError: Chưa có checkpoint Matcha-TTS.
        """
        if self.model is not None:
            return
        if not os.path.exists(self.checkpoint_path):
            raise FileNotFoundError(f"Chưa có checkpoint Matcha-TTS: {self.checkpoint_path}")

        from omegaconf import OmegaConf
        from matcha.hifigan.config import v1 as HIFIGAN_CONFIG
        from matcha.hifigan.denoiser import Denoiser
        from matcha.hifigan.env import AttrDict
        from matcha.hifigan.models import Generator as HiFiGAN
        from matcha.models.matcha_tts import MatchaTTS

        if not os.path.exists(self.vocoder_path):
            os.makedirs(os.path.dirname(self.vocoder_path), exist_ok=True)
            torch.hub.download_url_to_file(self.HIFIGAN_UNIV_URL, self.vocoder_path)
        vocoder = HiFiGAN(AttrDict(HIFIGAN_CONFIG)).to(self.device)
        vocoder.load_state_dict(torch.load(self.vocoder_path, map_location=self.device)["generator"])
        vocoder.eval()
        vocoder.remove_weight_norm()

        ckpt = torch.load(self.checkpoint_path, map_location=self.device, weights_only=False)
        model = MatchaTTS(**OmegaConf.create(ckpt["hparams"])).to(self.device).eval()
        model.load_state_dict(ckpt["state_dict"])

        meta = ckpt["meta"]
        self.symbol2id = {c: i for i, c in enumerate(meta["vocab"])}
        self.keep_punctuation = meta.get("keep_punctuation", False)
        self.vocoder, self.denoiser, self.model = vocoder, Denoiser(vocoder, mode="zeros"), model
        print(f"[Matcha-TTS] {os.path.basename(self.checkpoint_path)} (step {ckpt.get('step', '?')}), "
              f"vocoder {os.path.basename(self.vocoder_path)}, {self.device.upper()}")

    @staticmethod
    def _split_phrases(text: str) -> List[Tuple[str, str, float]]:
        """Tách văn bản thành các cụm theo dấu câu: (cụm, dấu câu kết thúc, khoảng lặng giây sau cụm).

        Dữ liệu huấn luyện không có dấu câu nên mô hình không tự học được chỗ ngắt nghỉ; ngắt cụm ở bước
        suy luận giúp giọng đọc có nhịp tự nhiên thay vì đọc liền một hơi.
        """
        phrases = []
        for chunk, punct in re.findall(r"([^,;:.!?…\n]+)([,;:.!?…\n]*)", text):
            pause = max((PHRASE_PAUSES.get(p, 0.0) for p in punct), default=PHRASE_PAUSES[","])
            if chunk.strip():
                phrases.append((chunk.strip(), punct[:1], pause))
        return phrases

    @staticmethod
    def _trim_silence(wav: np.ndarray, sr: int, top_db: float = 30.0, margin: float = 0.05) -> np.ndarray:
        """Cắt khoảng lặng/nhiễu ở hai đầu cụm, giữ lại một chút biên để không mất phụ âm cuối."""
        frame = int(0.01 * sr)
        n_frames = len(wav) // frame
        if n_frames == 0:
            return wav
        rms = np.sqrt((wav[: n_frames * frame].reshape(n_frames, frame) ** 2).mean(axis=1) + 1e-12)
        voiced = np.where(20 * np.log10(rms / rms.max()) > -top_db)[0]
        if len(voiced) == 0:
            return wav
        pad = int(margin * sr)
        start = max(0, voiced[0] * frame - pad)
        end = min(len(wav), (voiced[-1] + 1) * frame + pad)
        return wav[start:end]

    def _text_to_token_ids(self, text: str, punct: str = "") -> List[int]:
        """Chuyển cụm văn bản thành IDs có xen kẽ blank token (id 0).

        Dấu câu cuối cụm chỉ được giữ khi mô hình đã học dấu câu (ví dụ "?" cho ngữ điệu câu hỏi).
        """
        if self.keep_punctuation and punct:
            text = f"{text}{punct}"
        return tokens_to_ids(text_to_tokens(text, keep_punctuation=self.keep_punctuation), self.symbol2id)

    def synthesize(
        self,
        text: str,
        output_path: Optional[str] = None,
        normalize: bool = True,
        n_timesteps: int = 20,
        temperature: float = 0.667,
        speaking_rate: float = 1.0,
        **kwargs,
    ) -> Tuple[str, float]:
        """Tổng hợp giọng nói bằng Flow Matching.

        Args:
            text: Văn bản đầu vào.
            output_path: Đường dẫn lưu file .wav. None: outputs/matcha_<ms>.wav.
            normalize: Tự động chuẩn hóa tiếng Việt qua normalizer.
            n_timesteps: Số bước giải ODE Euler. 20 bước cho giọng mượt hơn 10 bước, vẫn nhanh hơn thời gian
                thực trên CPU.
            temperature: Độ lệch chuẩn của nhiễu khởi tạo; thấp hơn thì đều hơn, cao hơn thì biểu cảm hơn.
            speaking_rate: Tốc độ đọc (> 1.0 là nhanh hơn).
            **kwargs: Tham số của engine khác (voice, ...), bị bỏ qua.

        Returns:
            Tuple (đường dẫn file âm thanh tuyệt đối, RTF).
        """
        if not text or not text.strip():
            raise ValueError("Văn bản không được để trống!")

        clean_text = normalize_vietnamese_text(text) if normalize else text.strip()
        if output_path is None:
            out_dir = os.path.join(_root_dir, "outputs")
            os.makedirs(out_dir, exist_ok=True)
            output_path = os.path.join(out_dir, f"matcha_{int(time.time() * 1000)}.wav")
        else:
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        t0 = time.time()
        self._ensure_model_loaded()
        fade = np.linspace(0.0, 1.0, int(0.01 * self.sample_rate), dtype=np.float32)

        # Sinh từng cụm (theo dấu câu) rồi ghép lại với khoảng lặng tương ứng
        pieces = []
        for phrase, punct, pause in self._split_phrases(clean_text):
            token_ids = self._text_to_token_ids(phrase, punct)
            if len(token_ids) <= 1:
                continue
            x = torch.tensor(token_ids, dtype=torch.long, device=self.device)[None]
            x_lengths = torch.tensor([x.shape[-1]], dtype=torch.long, device=self.device)
            with torch.no_grad():
                mel = self.model.synthesise(
                    x,
                    x_lengths,
                    n_timesteps=n_timesteps,
                    temperature=temperature,
                    spks=None,
                    length_scale=1.0 / speaking_rate,
                )["mel"]
                audio = self.vocoder(mel).clamp(-1, 1)
                wav = self.denoiser(audio.squeeze(), strength=0.00025).cpu().squeeze().numpy()

            wav = self._trim_silence(wav, self.sample_rate)
            if len(wav) > 2 * len(fade):
                wav[: len(fade)] *= fade
                wav[-len(fade):] *= fade[::-1]
            pieces += [wav, np.zeros(int(pause * self.sample_rate), dtype=np.float32)]

        if not pieces:
            raise ValueError(f"Văn bản không chứa âm tiết tiếng Việt đọc được: {text!r}")
        waveform = np.concatenate(pieces[:-1])
        # Chuẩn hóa âm lượng đồng đều giữa các câu (đỉnh ~ -1 dBFS)
        waveform = 0.9 * waveform / max(1e-6, float(np.abs(waveform).max()))
        sf.write(output_path, waveform, samplerate=self.sample_rate)

        rtf = round((time.time() - t0) / max(0.01, len(waveform) / self.sample_rate), 3)
        return os.path.abspath(output_path), rtf


if __name__ == "__main__":
    path, rtf = MatchaTTSEngine().synthesize("Hồ Gươm nằm ở trung tâm thủ đô Hà Nội.")
    print(f"[OK] {path} (RTF: {rtf})")
