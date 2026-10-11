"""Module điều khiển và tích hợp mô hình Matcha-TTS (Optimal-Transport Conditional Flow Matching).

Bài báo gốc:
Shivam Mehta et al., "Matcha-TTS: A fast TTS architecture with conditional flow matching", ICASSP 2024.

Hỗ trợ:
- Tải trọng số tự huấn luyện từ Colab: checkpoints/matcha_vi_v2.pt (notebooks/02_train_matcha_colab.ipynb, ưu tiên)
  hoặc checkpoint VIVOS cũ checkpoints/matcha_vi.pt (+ checkpoints/vivos_meta.json).
- Frontend tiếng Việt dùng chung với notebook (src/vi_frontend.py): char_v1 hoặc vi_tone_v2 (tách thanh điệu).
- Neural Vocoder HiFi-GAN: bản fine-tune đi kèm checkpoint (<tên checkpoint>_hifigan.pt) nếu có,
  ngược lại dùng HiFi-GAN Universal (g_02500000).
- Chạy suy luận (Inference) dựa trên bộ giải vi phân thường (ODE Solver).
- Điều chỉnh số bước lấy mẫu (n_timesteps: 4 - 50 bước), tốc độ đọc, và chọn người nói (65 speakers).
- Đo đạc thời gian xử lý và Real-Time Factor (RTF).
"""

import json
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

# Đảm bảo import được Match-TTS từ thư mục con
_current_dir = os.path.dirname(os.path.abspath(__file__))
_root_dir = os.path.dirname(_current_dir)
_matcha_dir = os.path.join(_root_dir, "Matcha-TTS")
if _matcha_dir not in sys.path and os.path.exists(_matcha_dir):
    sys.path.insert(0, _matcha_dir)

try:
    from .normalizer import normalize_vietnamese_text
    from .vi_frontend import text_to_tokens, tokens_to_ids
except ImportError:
    from normalizer import normalize_vietnamese_text
    from vi_frontend import text_to_tokens, tokens_to_ids


# Khoảng lặng (giây) chèn sau cụm, theo dấu câu kết thúc cụm
PHRASE_PAUSES = {",": 0.15, ";": 0.25, ":": 0.25, ".": 0.4, "!": 0.4, "?": 0.4, "…": 0.4, "\n": 0.45}
# Speaker mặc định theo giới tính cho checkpoint VIVOS đa giọng (chọn bằng audition_speakers.py: CER ASR thấp nhất)
DEFAULT_SPEAKERS = {"f": "VIVOSSPK25", "m": "VIVOSSPK12"}


class MatchaTTSEngine:
    """Engine quản lý mô hình Matcha-TTS sử dụng Conditional Flow Matching."""

    HIFIGAN_UNIV_URL = "https://github.com/shivammehta25/Matcha-TTS-checkpoints/releases/download/v1.0/g_02500000"

    def __init__(
        self,
        checkpoint_path: Optional[str] = None,
        meta_path: Optional[str] = None,
        vocoder_path: Optional[str] = None,
        device: Optional[str] = None,
    ):
        """Khai báo đường dẫn tài nguyên; mô hình chỉ được nạp ở lần tổng hợp đầu tiên (lazy loading).

        Args:
            checkpoint_path: File .pt của Matcha-TTS. None: tìm lần lượt matcha_vi_v2.pt, matcha_vi.pt,
                best_model.pt trong checkpoints/.
            meta_path: Metadata cho checkpoint VIVOS cũ (bộ ký tự, danh sách speaker). Checkpoint mới
                lưu metadata ngay trong file .pt nên không cần.
            vocoder_path: Trọng số HiFi-GAN. None: dùng `<checkpoint>_hifigan.pt` nếu có, ngược lại
                HiFi-GAN Universal (tự tải về checkpoints/hifigan_univ_v1).
            device: 'cuda' hoặc 'cpu'. None: tự chọn.
        """
        self.device = device if device else ("cuda" if torch.cuda.is_available() else "cpu")
        self.sample_rate = 22050

        # Xác định đường dẫn mặc định tới checkpoints
        ckpt_dir = os.path.join(_root_dir, "checkpoints")
        if checkpoint_path is None:
            for candidate in ("matcha_vi_v2.pt", "matcha_vi.pt", "best_model.pt"):
                cand_path = os.path.join(ckpt_dir, candidate)
                if os.path.exists(cand_path):
                    checkpoint_path = cand_path
                    break
            if checkpoint_path is None:
                checkpoint_path = os.path.join(ckpt_dir, "matcha_vi.pt")

        self.checkpoint_path = checkpoint_path
        self.meta_path = meta_path or os.path.join(ckpt_dir, "vivos_meta.json")
        # Vocoder fine-tune đi kèm checkpoint (notebook train, mục 8) cho chất âm tốt hơn bản Universal
        paired_vocoder = os.path.splitext(checkpoint_path)[0] + "_hifigan.pt"
        self.vocoder_path = vocoder_path or (
            paired_vocoder if os.path.exists(paired_vocoder) else os.path.join(ckpt_dir, "hifigan_univ_v1")
        )

        self._is_loaded = False
        self.model = None
        self.vocoder = None
        self.denoiser = None
        self.symbol2id = {}
        self.frontend = "char_v1"
        self.keep_punctuation = False
        self.speakers = []
        self.spk2id = {}

        print(f"[Matcha-TTS] Khởi tạo Engine trên thiết bị: {self.device.upper()}")

    def _ensure_model_loaded(self) -> None:
        """Nạp vocoder, mô hình Matcha-TTS và metadata (một lần); đặt `_is_loaded` khi đủ thành phần."""
        if self._is_loaded:
            return

        # 1. Nạp Vocoder HiFi-GAN
        try:
            from matcha.hifigan.config import v1 as HIFIGAN_V1
            from matcha.hifigan.denoiser import Denoiser
            from matcha.hifigan.env import AttrDict
            from matcha.hifigan.models import Generator as HiFiGAN

            if not os.path.exists(self.vocoder_path):
                print(f"[Matcha-TTS] Tải checkpoint HiFi-GAN Vocoder về: {self.vocoder_path}...")
                os.makedirs(os.path.dirname(self.vocoder_path), exist_ok=True)
                torch.hub.download_url_to_file(self.HIFIGAN_UNIV_URL, self.vocoder_path)

            voc = HiFiGAN(AttrDict(HIFIGAN_V1)).to(self.device)
            voc_ckpt = torch.load(self.vocoder_path, map_location=self.device)
            voc.load_state_dict(voc_ckpt["generator"])
            voc.eval()
            voc.remove_weight_norm()
            self.vocoder = voc
            self.denoiser = Denoiser(voc, mode="zeros")
            print(f"[Matcha-TTS] Vocoder: {os.path.basename(self.vocoder_path)}")
        except Exception as e:
            print(f"[Matcha-TTS] Lỗi khi nạp Vocoder HiFi-GAN: {e}")

        # 2. Nạp trọng số Matcha-TTS
        try:
            from omegaconf import OmegaConf
            from matcha.models.matcha_tts import MatchaTTS

            if not (self.checkpoint_path and os.path.exists(self.checkpoint_path)):
                print(f"[Matcha-TTS] Chưa tìm thấy checkpoint tại: {self.checkpoint_path}")
                return
            print(f"[Matcha-TTS] Đang nạp trọng số mô hình tự huấn luyện: {self.checkpoint_path}")
            ckpt = torch.load(self.checkpoint_path, map_location=self.device)
            self.model = MatchaTTS(**OmegaConf.create(ckpt["hparams"])).to(self.device).eval()
            self.model.load_state_dict(ckpt["state_dict"])
        except Exception as e:
            print(f"[Matcha-TTS] Thông báo: Chưa nạp được checkpoint Matcha-TTS chuyên biệt: {e}")
            return

        # 3. Metadata (bộ token, frontend, danh sách speaker): checkpoint v2 lưu kèm trong file .pt,
        #    checkpoint VIVOS cũ dùng file vivos_meta.json riêng
        meta = ckpt.get("meta")
        if meta is None and os.path.exists(self.meta_path):
            with open(self.meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
        if meta is None:
            print(f"[Matcha-TTS] Cảnh báo: Không tìm thấy metadata tại: {self.meta_path}")
            return
        self.symbol2id = {c: i for i, c in enumerate(meta.get("vocab", []))}
        self.frontend = meta.get("frontend", "char_v1")
        self.keep_punctuation = meta.get("keep_punctuation", False)
        self.speakers = meta.get("speakers", [])
        self.spk2id = {s: i for i, s in enumerate(self.speakers)}
        self._is_loaded = True
        print(
            f"[Matcha-TTS] Nạp mô hình thành công (Epoch {ckpt.get('epoch', '?')}, Step {ckpt.get('step', '?')}, "
            f"frontend {self.frontend}, {len(self.speakers)} giọng)!"
        )

    @staticmethod
    def _split_phrases(text: str) -> List[Tuple[str, str, float]]:
        """Tách văn bản thành các cụm theo dấu câu: (cụm, dấu câu kết thúc, khoảng lặng giây sau cụm).

        VIVOS/InfoRe không có dấu câu nên mô hình không tự học được chỗ ngắt nghỉ; ngắt cụm ở bước suy luận
        giúp giọng đọc có nhịp tự nhiên thay vì đọc liền một hơi.
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

    def resolve_speaker(self, voice: Optional[str] = None, speaker_id: Optional[int] = None) -> int:
        """Chọn speaker: ưu tiên speaker_id, sau đó suy ra giới tính từ tên giọng ('nu', 'HoaiMy', 'nam', ...)."""
        if len(self.speakers) <= 1:
            return 0
        if speaker_id is not None:
            return max(0, min(speaker_id, len(self.speakers) - 1)) if self.speakers else 0
        v = (voice or "").lower()
        gender = "m" if any(k in v for k in ("nam", "male", "namminh")) and "female" not in v else "f"
        name = DEFAULT_SPEAKERS[gender]
        return self.spk2id.get(name, 0)

    def _text_to_token_ids(self, text: str, punct: str = "") -> List[int]:
        """Chuyển cụm văn bản thành IDs có xen kẽ blank token (id 0), theo frontend của checkpoint.

        Dấu câu cuối cụm chỉ được giữ khi mô hình đã học dấu câu (ví dụ "?" cho ngữ điệu câu hỏi).
        """
        if self.keep_punctuation and punct:
            text = f"{text}{punct}"
        tokens = text_to_tokens(text, frontend=self.frontend, keep_punctuation=self.keep_punctuation)
        return tokens_to_ids(tokens, self.symbol2id)

    def synthesize(
        self,
        text: str,
        output_path: Optional[str] = None,
        normalize: bool = True,
        speaker_id: Optional[int] = None,
        voice: Optional[str] = None,
        n_timesteps: int = 10,
        temperature: float = 0.667,
        speaking_rate: float = 1.0,
        **kwargs,
    ) -> Tuple[str, float]:
        """Tổng hợp giọng nói bằng giải thuật Flow Matching.

        Args:
            text: Văn bản đầu vào.
            output_path: Đường dẫn lưu file audio.
            normalize: Tự động chuẩn hóa tiếng Việt qua normalizer.
            speaker_id: Chỉ số người nói (VIVOS: 0 - 64; mô hình một giọng bỏ qua). None -> chọn theo `voice`.
            voice: Tên giọng ('nu', 'nam', 'vi-VN-HoaiMyNeural', ...) để chọn speaker mặc định theo giới tính.
            n_timesteps: Số bước giải ODE Euler. Mặc định 10: RTF khoảng 0,57 trên CPU, CER 1,0%; 20 bước:
                RTF khoảng 0,83, CER 0,5% (đo trên 10 câu InfoRe1).
            temperature: Nhiệt độ điều chỉnh ngẫu nhiên.
            speaking_rate: Tốc độ phát âm (> 1.0 là nhanh hơn).

        Returns:
            Tuple (đường dẫn file âm thanh tuyệt đối, giá trị RTF).
        """
        if not text or not text.strip():
            raise ValueError("Văn bản không được để trống!")

        clean_text = normalize_vietnamese_text(text) if normalize else text.strip()

        # Đường dẫn output mặc định
        if output_path is None:
            out_dir = os.path.join(_root_dir, "outputs")
            os.makedirs(out_dir, exist_ok=True)
            output_path = os.path.join(out_dir, f"matcha_{int(time.time() * 1000)}.wav")
        else:
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        t0 = time.time()
        self._ensure_model_loaded()

        if self._is_loaded and self.vocoder is not None:
            spks = None
            if self.model.n_spks > 1:
                spks = torch.tensor([self.resolve_speaker(voice, speaker_id)], dtype=torch.long, device=self.device)
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
                        spks=spks,
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
        else:
            # Fallback sang VITS nếu máy local chưa nạp được checkpoint Matcha
            print("[Matcha-TTS] Fallback sang VITS Decomposed Engine...")
            try:
                from .vits_decomposed import VITSDecomposedTTS
            except ImportError:
                from vits_decomposed import VITSDecomposedTTS
            fallback_vits = VITSDecomposedTTS()
            output_path = fallback_vits.synthesize(
                clean_text,
                output_path=output_path,
                normalize=False,
                speaking_rate=speaking_rate,
            )
            info = sf.info(output_path)
            self.sample_rate = info.samplerate

        t_infer = time.time() - t0
        audio_info = sf.info(output_path)
        rtf = round(t_infer / max(0.01, audio_info.duration), 3)

        return os.path.abspath(output_path), rtf


if __name__ == "__main__":
    matcha = MatchaTTSEngine()
    test_text = "Hệ thống tổng hợp tiếng nói sử dụng kỹ thuật Flow Matching tiên tiến."
    p, rtf_val = matcha.synthesize(test_text)
    print(f"[OK] File âm thanh sinh ra: {p} (RTF: {rtf_val})")

