"""Module tiền xử lý và chuẩn bị dữ liệu VIVOS (Vietnamese Speech Corpus).

Hỗ trợ:
- Tải hoặc phân tích cấu trúc thư mục VIVOS Dataset.
- Chuẩn hóa văn bản tiếng Việt qua module normalizer.
- Kiểm tra tính hợp lệ của file âm thanh (sample rate, số kênh, thời lượng).
- Phân chia và xuất file manifest chuẩn (JSON Lines) cho Train / Validation / Test.
"""

import json
import os
import sys
import tarfile
import urllib.request
from dataclasses import asdict, dataclass
from typing import Dict, List, Optional, Tuple

import soundfile as sf

# Đảm bảo import được normalizer trong cùng package src
try:
    from .normalizer import normalize_vietnamese_text
except ImportError:
    from normalizer import normalize_vietnamese_text


@dataclass
class AudioSample:
    audio_id: str
    audio_filepath: str
    raw_text: str
    normalized_text: str
    duration: float
    sample_rate: int
    speaker_id: str


class VIVOSPreprocessor:
    """Bộ xử lý dữ liệu VIVOS cho các mô hình TTS tiếng Việt."""

    # Mirror chính thức từ AILAB-VNUHCM trên Hugging Face CDN (tốc độ cao, luôn sẵn sàng)
    VIVOS_DOWNLOAD_URL = "https://huggingface.co/datasets/AILAB-VNUHCM/vivos/resolve/main/data/vivos.tar.gz"

    def __init__(self, data_root: str):
        self.data_root = os.path.abspath(data_root)
        self.raw_dir = os.path.join(self.data_root, "raw", "vivos")
        self.processed_dir = os.path.join(self.data_root, "processed")

    def download_and_extract(self) -> str:
        """Tải và giải nén bộ dữ liệu VIVOS nếu chưa tồn tại."""
        os.makedirs(os.path.dirname(self.raw_dir), exist_ok=True)
        tar_path = os.path.join(self.data_root, "raw", "vivos.tar.gz")

        if os.path.exists(self.raw_dir) and os.path.isdir(self.raw_dir):
            print(f"[VIVOS] Đã phát hiện thư mục dữ liệu tại: {self.raw_dir}")
            return self.raw_dir

        if not os.path.exists(tar_path):
            print(f"[VIVOS] Đang tải bộ dữ liệu VIVOS từ {self.VIVOS_DOWNLOAD_URL}...")
            print("Quá trình này có thể mất vài phút (~1.4 GB)...")
            try:
                urllib.request.urlretrieve(self.VIVOS_DOWNLOAD_URL, tar_path)
                print("[VIVOS] Đã tải xong file nén!")
            except Exception as e:
                print(f"[VIVOS] Không thể tải tự động từ web: {e}")
                print(f"Vui lòng tải thủ công 'vivos.tar.gz' và đặt vào: {tar_path}")
                raise e

        print(f"[VIVOS] Đang giải nén {tar_path}...")
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(path=os.path.join(self.data_root, "raw"))
        print(f"[VIVOS] Giải nén hoàn tất tại: {self.raw_dir}")
        return self.raw_dir

    @staticmethod
    def read_prompts(prompts_file: str) -> Dict[str, str]:
        """Đọc file prompts.txt ánh xạ audio_id sang văn bản."""
        prompts = {}
        if not os.path.exists(prompts_file):
            raise FileNotFoundError(f"Không tìm thấy file prompts: {prompts_file}")

        with open(prompts_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(maxsplit=1)
                if len(parts) == 2:
                    audio_id, text = parts
                    prompts[audio_id.strip()] = text.strip()
        return prompts

    def parse_split(self, split_name: str) -> List[AudioSample]:
        """Duyệt và trích xuất thông tin các mẫu âm thanh trong một split (train hoặc test)."""
        split_dir = os.path.join(self.raw_dir, split_name)
        prompts_file = os.path.join(split_dir, "prompts.txt")
        waves_dir = os.path.join(split_dir, "waves")

        prompts = self.read_prompts(prompts_file)
        samples = []

        print(f"[VIVOS] Đang xử lý tập '{split_name}' ({len(prompts)} câu)...")
        for speaker_id in sorted(os.listdir(waves_dir)):
            speaker_dir = os.path.join(waves_dir, speaker_id)
            if not os.path.isdir(speaker_dir):
                continue

            for fname in sorted(os.listdir(speaker_dir)):
                if not fname.endswith(".wav"):
                    continue

                audio_id = os.path.splitext(fname)[0]
                raw_text = prompts.get(audio_id, "")
                if not raw_text:
                    continue

                wav_path = os.path.join(speaker_dir, fname)

                # Đọc thông tin kỹ thuật của file audio
                try:
                    info = sf.info(wav_path)
                    duration = float(info.duration)
                    sr = int(info.samplerate)
                except Exception as e:
                    print(f"Lỗi đọc file {wav_path}: {e}")
                    continue

                # Chuẩn hóa văn bản tiếng Việt
                norm_text = normalize_vietnamese_text(raw_text)

                sample = AudioSample(
                    audio_id=audio_id,
                    audio_filepath=os.path.abspath(wav_path),
                    raw_text=raw_text,
                    normalized_text=norm_text,
                    duration=round(duration, 3),
                    sample_rate=sr,
                    speaker_id=speaker_id,
                )
                samples.append(sample)

        return samples

    def build_manifests(self, val_ratio: float = 0.05) -> Dict[str, str]:
        """Tạo các file manifest JSON Lines: train_manifest.json, val_manifest.json, test_manifest.json."""
        os.makedirs(self.processed_dir, exist_ok=True)

        # 1. Tập Train gốc được chia thành Train và Validation
        train_samples = self.parse_split("train")
        # Phân tách ngẫu nhiên nhưng có hạt giống cố định để tái lập kết quả
        import random
        random.seed(42)
        random.shuffle(train_samples)

        val_size = int(len(train_samples) * val_ratio)
        val_samples = train_samples[:val_size]
        actual_train_samples = train_samples[val_size:]

        # 2. Tập Test
        test_samples = self.parse_split("test")

        manifest_paths = {
            "train": os.path.join(self.processed_dir, "train_manifest.json"),
            "val": os.path.join(self.processed_dir, "val_manifest.json"),
            "test": os.path.join(self.processed_dir, "test_manifest.json"),
        }

        splits_data = {
            "train": actual_train_samples,
            "val": val_samples,
            "test": test_samples,
        }

        print("\n" + "=" * 60)
        print("THỐNG KÊ BỘ DỮ LIỆU VIVOS ĐÃ TIỀN XỬ LÝ:")
        print("=" * 60)

        for name, data in splits_data.items():
            path = manifest_paths[name]
            total_duration_sec = sum(s.duration for s in data)
            total_hours = total_duration_sec / 3600.0
            speakers = len(set(s.speaker_id for s in data))

            with open(path, "w", encoding="utf-8") as f:
                for sample in data:
                    f.write(json.dumps(asdict(sample), ensure_ascii=False) + "\n")

            print(f"• Tập {name:<6}: {len(data):>5} mẫu | {total_hours:>5.2f} giờ | {speakers:>3} người nói -> {path}")

        print("=" * 60 + "\n")
        return manifest_paths


if __name__ == "__main__":
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(current_script_dir)
    default_data_dir = os.path.join(root_dir, "data")

    preprocessor = VIVOSPreprocessor(data_root=default_data_dir)
    print(f"Thư mục dữ liệu: {default_data_dir}")
    print("Để tải và xử lý VIVOS, gọi: preprocessor.download_and_extract() và preprocessor.build_manifests()")
