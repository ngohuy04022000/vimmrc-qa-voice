"""Module phân rã và thực thi mô hình VITS (Variational Inference Text-to-Speech).

Mục tiêu học tập & nghiên cứu:
- Bóc tách toàn bộ quy trình tính toán nội bộ của kiến trúc End-to-End VITS.
- Minh họa từng bước từ Text -> Token IDs -> Text Encoder -> Duration/Alignment -> Latent z -> HiFi-GAN Waveform.
- Hỗ trợ tinh chỉnh các tham số sinh: tốc độ nói (speaking_rate), độ biến thiên ngữ điệu (noise_scale).
"""

import os
import sys
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import soundfile as sf
import torch
from transformers import VitsModel, VitsTokenizer

# Đảm bảo import được module tiền xử lý cùng thư mục hoặc package
try:
    from .normalizer import normalize_vietnamese_text
except ImportError:
    from normalizer import normalize_vietnamese_text


@dataclass
class DecomposedVITSOutput:
    """Chứa toàn bộ các tensor trung gian và kết quả phân rã của VITS."""
    input_text: str
    normalized_text: str
    tokens: List[str]
    input_ids: List[int]
    encoder_hidden_shape: Tuple[int, ...]
    prior_mean_shape: Tuple[int, ...]
    durations_per_token: List[int]
    durations_ms: List[float]
    total_frames: int
    latent_z_shape: Tuple[int, ...]
    waveform: np.ndarray
    sample_rate: int
    duration_seconds: float
    output_path: Optional[str] = None


class VITSDecomposedTTS:
    """Lớp điều khiển và phân rã mô hình VITS tiếng Việt (facebook/mms-tts-vie)."""

    DEFAULT_MODEL_ID = "facebook/mms-tts-vie"

    def __init__(self, model_id: str = DEFAULT_MODEL_ID, device: Optional[str] = None):
        self.model_id = model_id
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        print(f"[VITS] Đang khởi tạo mô hình '{model_id}' trên thiết bị: {self.device.upper()}...")
        self.tokenizer = VitsTokenizer.from_pretrained(model_id)
        self.model = VitsModel.from_pretrained(model_id).to(self.device)
        self.model.eval()
        self.sample_rate = self.model.config.sampling_rate
        # Trong VITS chuẩn của MMS, hệ số upsampling của HiFi-GAN là 256
        self.hop_length = 256
        self.ms_per_frame = (self.hop_length / self.sample_rate) * 1000.0

    def synthesize(
        self,
        text: str,
        output_path: Optional[str] = None,
        normalize: bool = True,
        speaking_rate: float = 1.0,
        noise_scale: float = 0.667,
    ) -> str:
        """Tổng hợp âm thanh tiêu chuẩn từ văn bản.

        Args:
            text: Văn bản tiếng Việt đầu vào.
            output_path: Đường dẫn file lưu .wav.
            normalize: Tự động chuẩn hóa số/ngày tháng bằng normalizer.
            speaking_rate: Tốc độ nói (> 1.0 là nói nhanh hơn, < 1.0 là nói chậm hơn).
            noise_scale: Độ ngẫu nhiên của ngữ điệu.

        Returns:
            Đường dẫn tuyệt đối đến file âm thanh đã lưu.
        """
        if not text or not text.strip():
            raise ValueError("Văn bản đầu vào không được để trống!")

        clean_text = normalize_vietnamese_text(text) if normalize else text.strip()
        inputs = self.tokenizer(clean_text, return_tensors="pt").to(self.device)

        with torch.no_grad():
            output = self.model(
                **inputs,
                speaking_rate=speaking_rate,
                noise_scale=noise_scale,
            )

        waveform = output.waveform[0].cpu().float().numpy()

        if output_path is None:
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            output_dir = os.path.join(root_dir, "outputs")
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"vits_{int(time.time() * 1000)}.wav")
        else:
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        sf.write(output_path, waveform, samplerate=self.sample_rate)
        return os.path.abspath(output_path)

    def decompose_inference(
        self,
        text: str,
        normalize: bool = True,
        speaking_rate: float = 1.0,
        output_path: Optional[str] = None,
    ) -> DecomposedVITSOutput:
        """Phân rã chi tiết từng bước tính toán bên trong mô hình VITS.

        Bóc tách:
        - Bước 1: Tiền xử lý & Tokenizer (Ký tự -> Token IDs)
        - Bước 2: Text Encoder (Token IDs -> Hidden states, Prior Distribution)
        - Bước 3: Duration Predictor & Alignment (Độ dài từng âm vị)
        - Bước 4: Latent space z & Flow
        - Bước 5: HiFi-GAN Decoder (z -> Raw Waveform)
        """
        clean_text = normalize_vietnamese_text(text) if normalize else text.strip()

        # ==============================================================
        # BƯỚC 1: TOKENIZATION & PHONEMIZATION
        # ==============================================================
        tokenized = self.tokenizer(clean_text, return_tensors="pt")
        input_ids = tokenized["input_ids"].to(self.device)
        id_list = input_ids[0].tolist()
        tokens = [self.tokenizer.decode([t_id]) for t_id in id_list]

        # ==============================================================
        # BƯỚC 2: TEXT ENCODER (TRANSFORMER + PROJECTION)
        # ==============================================================
        with torch.no_grad():
            attn_mask = tokenized.get("attention_mask", None)
            if attn_mask is not None:
                attn_mask = attn_mask.to(self.device)
            mask_dtype = self.model.text_encoder.embed_tokens.weight.dtype
            if attn_mask is not None:
                input_padding_mask = attn_mask.unsqueeze(-1).to(mask_dtype)
            else:
                input_padding_mask = torch.ones_like(input_ids).unsqueeze(-1).to(mask_dtype)

            # Trích xuất biểu diễn ẩn từ text encoder
            text_encoder_out = self.model.text_encoder(
                input_ids=input_ids,
                padding_mask=input_padding_mask,
                attention_mask=attn_mask,
                output_hidden_states=True,
            )
            h_text = text_encoder_out.last_hidden_state
            prior_means = text_encoder_out.prior_means
            prior_log_variances = text_encoder_out.prior_log_variances

            # ==========================================================
            # BƯỚC 3 & 4: DURATION PREDICTOR & LATENT EXPANSION (INFERENCE)
            # ==========================================================
            # Gọi forward đầy đủ để lấy waveform và ma trận căn chỉnh
            model_out = self.model(
                input_ids=input_ids,
                speaking_rate=speaking_rate,
                output_attentions=True,
            )
            waveform = model_out.waveform[0].cpu().float().numpy()

            # Trích xuất ma trận căn chỉnh (Alignment map) nếu có
            durations_list = []
            durations_ms = []
            total_frames = 0
            if hasattr(model_out, "attentions") and model_out.attentions is not None:
                attn = model_out.attentions[0].cpu().numpy()
                # attn shape: (batch, 1, time_audio, time_text)
                # Tổng số khung hình gán cho mỗi token
                align_per_token = np.argmax(attn[0, 0], axis=0)
                # Tính duration bằng histogram
                counts = np.bincount(align_per_token, minlength=len(id_list))
                durations_list = counts.tolist()
                durations_ms = [round(c * self.ms_per_frame, 1) for c in durations_list]
                total_frames = int(np.sum(counts))
            else:
                # Ước tính từ độ dài sóng âm
                total_frames = int(len(waveform) // self.hop_length)
                avg_frames = max(1, total_frames // len(id_list))
                durations_list = [avg_frames] * len(id_list)
                durations_ms = [round(avg_frames * self.ms_per_frame, 1)] * len(id_list)

        duration_sec = len(waveform) / self.sample_rate

        if output_path is not None:
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            sf.write(output_path, waveform, samplerate=self.sample_rate)
            saved_file = os.path.abspath(output_path)
        else:
            saved_file = None

        latent_channels = prior_means.shape[1]

        return DecomposedVITSOutput(
            input_text=text,
            normalized_text=clean_text,
            tokens=tokens,
            input_ids=id_list,
            encoder_hidden_shape=tuple(h_text.shape),
            prior_mean_shape=tuple(prior_means.shape),
            durations_per_token=durations_list,
            durations_ms=durations_ms,
            total_frames=total_frames,
            latent_z_shape=(1, latent_channels, total_frames),
            waveform=waveform,
            sample_rate=self.sample_rate,
            duration_seconds=duration_sec,
            output_path=saved_file,
        )


def print_decomposition_report(res: DecomposedVITSOutput):
    """In báo cáo phân rã chi tiết kiến trúc VITS ra màn hình."""
    print("=" * 75)
    print(" BÁO CÁO PHÂN RÃ NỘI TẠI MÔ HÌNH VITS (VARIATIONAL INFERENCE FOR TTS)")
    print("=" * 75)

    print("\n[BƯỚC 1: TIỀN XỬ LÝ VĂN BẢN & TOKENIZATION]")
    print(f"  • Văn bản gốc        : {res.input_text}")
    print(f"  • Văn bản chuẩn hóa  : {res.normalized_text}")
    print(f"  • Tổng số tokens     : {len(res.input_ids)}")
    print(f"  • Chuỗi Token IDs    : {res.input_ids[:15]}...")
    sample_tokens_str = " | ".join(f"'{tok}'({tid})" for tok, tid in zip(res.tokens[:8], res.input_ids[:8]))
    print(f"  • Ánh xạ mẫu         : {sample_tokens_str} ...")

    print("\n[BƯỚC 2: TEXT ENCODER (TRANSFORMER + PROJECTIONS)]")
    print(f"  • Kích thước ẩn (h_text)   : {res.encoder_hidden_shape} [Batch, SeqLen, HiddenDim]")
    print(f"  • Phân phối tiên nghiệm μ  : {res.prior_mean_shape} (Kỳ vọng không gian tiềm ẩn)")
    print(f"  • Phân phối tiên nghiệm σ  : {res.prior_mean_shape} (Log-phương sai không gian tiềm ẩn)")

    print("\n[BƯỚC 3: DURATION PREDICTOR & CĂN CHỈNH THỜI GIAN]")
    print(f"  • Tổng số khung hình (Frames) : {res.total_frames} khung")
    print(f"  • 1 Khung hình tương đương    : {256 / res.sample_rate * 1000:.2f} ms")
    print("  • Phân phối thời lượng từng ký tự đầu tiên:")
    for tok, ms, fr in zip(res.tokens[:6], res.durations_ms[:6], res.durations_per_token[:6]):
        print(f"      - Ký tự/Âm vị '{tok}': {fr:>2} khung (~{ms:>5.1f} ms)")

    print("\n[BƯỚC 4: NORMALIZING FLOW & KHÔNG GIAN TIỀM ẨN Z]")
    print(f"  • Vector tiềm ẩn z mở rộng: {res.latent_z_shape} [Batch, Channels, Frames]")
    print("  • Mạng Flow biến đổi phân phối Gauss cơ sở thành biểu diễn âm học giàu chi tiết.")

    print("\n[BƯỚC 5: HIFI-GAN DECODER (WAVEFORM GENERATOR)]")
    print(f"  • Tần số lấy mẫu âm thanh : {res.sample_rate} Hz (16.000 mẫu/giây)")
    print(f"  • Tổng số điểm mẫu sóng   : {len(res.waveform):,} mẫu")
    print(f"  • Thời lượng âm thanh     : {res.duration_seconds:.2f} giây")
    print(f"  • Miền biên độ sóng       : [{np.min(res.waveform):.3f}, {np.max(res.waveform):.3f}]")

    if res.output_path:
        print(f"\n[OK] File âm thanh đã được xuất tại: {res.output_path}")
    print("=" * 75)


if __name__ == "__main__":
    vits = VITSDecomposedTTS()
    sample_text = "Thủ đô của Việt Nam là Hà Nội."
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_audio = os.path.join(root_dir, "outputs", "demo_vits_decomposed.wav")
    report = vits.decompose_inference(sample_text, output_path=output_audio)
    print_decomposition_report(report)
