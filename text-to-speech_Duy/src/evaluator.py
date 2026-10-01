"""Module đánh giá và đo đạc thực nghiệm các mô hình TTS theo chuẩn học thuật.

Bao gồm các chỉ số:
- MCD (Mel-Cepstral Distortion): Đo sai số phổ âm thanh (dB).
- F0 RMSE (Pitch/Fundamental Frequency Error): Đo sai số cao độ thanh điệu (Hz).
- RTF (Real-Time Factor): Tốc độ sinh so với thời gian thực.
- Báo cáo đối sánh hàng loạt (Batch Benchmark Comparison) xuất bảng Markdown.
"""

import math
import os
import time
from typing import Dict, List, Optional, Tuple

import numpy as np
import soundfile as sf
from scipy.signal import spectrogram


def extract_mel_cepstrum(
    audio: np.ndarray,
    sr: int,
    n_mfcc: int = 16,
    n_fft: int = 1024,
    hop_length: int = 256,
) -> np.ndarray:
    """Trích xuất ma trận Mel-Frequency Cepstral Coefficients (MFCCs)."""
    # 1. Tính Spectrogram
    frequencies, times, sxx = spectrogram(
        audio,
        fs=sr,
        nperseg=n_fft,
        noverlap=n_fft - hop_length,
        window="hann",
    )
    # Tránh log(0)
    power_spec = np.maximum(sxx, 1e-10)

    # 2. Ngân hàng bộ lọc Mel tam giác đơn giản (Mel Filterbank)
    low_freq_mel = 0.0
    high_freq_mel = 2595.0 * np.log10(1.0 + (sr / 2.0) / 700.0)
    mel_points = np.linspace(low_freq_mel, high_freq_mel, n_mfcc + 2)
    hz_points = 700.0 * (10.0 ** (mel_points / 2595.0) - 1.0)
    bin_points = np.floor((n_fft + 1) * hz_points / sr).astype(int)

    fbank = np.zeros((n_mfcc, len(frequencies)))
    for m in range(1, n_mfcc + 1):
        f_m_minus = bin_points[m - 1]
        f_m = bin_points[m]
        f_m_plus = bin_points[m + 1]

        for k in range(f_m_minus, f_m):
            if f_m != f_m_minus:
                fbank[m - 1, k] = (k - f_m_minus) / (f_m - f_m_minus)
        for k in range(f_m, f_m_plus):
            if f_m_plus != f_m:
                fbank[m - 1, k] = (f_m_plus - k) / (f_m_plus - f_m)

    mel_spec = np.dot(fbank, power_spec)
    log_mel = np.log(np.maximum(mel_spec, 1e-10))

    # 3. Biến đổi Cosine rời rạc (DCT-II)
    mfcc = np.zeros_like(log_mel)
    num_filters = log_mel.shape[0]
    for i in range(num_filters):
        for j in range(num_filters):
            mfcc[i, :] += log_mel[j, :] * np.cos(np.pi * i * (j + 0.5) / num_filters)

    return mfcc.T  # Shape: (num_frames, n_mfcc)


def dynamic_time_warping(s1: np.ndarray, s2: np.ndarray) -> Tuple[float, List[Tuple[int, int]]]:
    """Căn chỉnh thời gian động (DTW) giữa 2 chuỗi vector đặc trưng."""
    n, m = len(s1), len(s2)
    cost_matrix = np.full((n + 1, m + 1), np.inf)
    cost_matrix[0, 0] = 0.0

    # Tính khoảng cách Euclidean từng cặp frame
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            dist = np.linalg.norm(s1[i - 1] - s2[j - 1])
            cost_matrix[i, j] = dist + min(
                cost_matrix[i - 1, j],      # insertion
                cost_matrix[i, j - 1],      # deletion
                cost_matrix[i - 1, j - 1],  # match
            )

    # Truy vết đường đi tối ưu
    i, j = n, m
    path = []
    while i > 0 and j > 0:
        path.append((i - 1, j - 1))
        steps = [
            (cost_matrix[i - 1, j - 1], (i - 1, j - 1)),
            (cost_matrix[i - 1, j], (i - 1, j)),
            (cost_matrix[i, j - 1], (i, j - 1)),
        ]
        _, (i, j) = min(steps, key=lambda x: x[0])

    path.reverse()
    normalized_cost = cost_matrix[n, m] / len(path)
    return float(normalized_cost), path


def calculate_mcd(ref_wav_path: str, synth_wav_path: str) -> float:
    """Tính chỉ số Mel-Cepstral Distortion (MCD) bằng dB giữa 2 file audio.

    MCD càng nhỏ biểu thị âm thanh tổng hợp càng gần với âm thanh gốc.
    """
    ref_audio, ref_sr = sf.read(ref_wav_path)
    synth_audio, synth_sr = sf.read(synth_wav_path)

    # Đưa về mono nếu là stereo
    if ref_audio.ndim > 1:
        ref_audio = np.mean(ref_audio, axis=1)
    if synth_audio.ndim > 1:
        synth_audio = np.mean(synth_audio, axis=1)

    # Trích xuất MFCCs
    ref_mfcc = extract_mel_cepstrum(ref_audio, ref_sr)
    synth_mfcc = extract_mel_cepstrum(synth_audio, synth_sr)

    # Bỏ qua hệ số c0 (năng lượng) chỉ tính từ c1 trở đi
    ref_mfcc = ref_mfcc[:, 1:]
    synth_mfcc = synth_mfcc[:, 1:]

    # Căn chỉnh DTW
    _, path = dynamic_time_warping(ref_mfcc, synth_mfcc)

    # Tính MCD theo công thức chuẩn: (10 * sqrt(2) / ln(10)) * mean(norm(diff))
    factor = (10.0 * math.sqrt(2.0)) / math.log(10.0)
    diffs = []
    for idx_ref, idx_synth in path:
        diff = np.linalg.norm(ref_mfcc[idx_ref] - synth_mfcc[idx_synth])
        diffs.append(diff)

    mcd_value = factor * float(np.mean(diffs))
    return round(mcd_value, 2)


def estimate_f0(audio: np.ndarray, sr: int, frame_size: int = 1024, hop_size: int = 256) -> np.ndarray:
    """Ước lượng đường cong tần số cơ bản F0 contour (cao độ thanh điệu) qua Autocorrelation."""
    num_frames = (len(audio) - frame_size) // hop_size + 1
    f0 = np.zeros(num_frames)

    fmin = 60.0   # Hz (tần số nam thấp nhất)
    fmax = 400.0  # Hz (tần số nữ cao nhất)
    lag_min = int(sr / fmax)
    lag_max = int(sr / fmin)

    for i in range(num_frames):
        frame = audio[i * hop_size : i * hop_size + frame_size]
        # Trừ giá trị trung bình
        frame = frame - np.mean(frame)
        if np.std(frame) < 1e-4:
            continue

        # Tự tương quan
        corr = np.correlate(frame, frame, mode="full")
        corr = corr[len(corr) // 2 :]

        if lag_max < len(corr):
            peak_lag = lag_min + np.argmax(corr[lag_min:lag_max])
            if corr[peak_lag] > 0.3 * corr[0]:
                f0[i] = sr / peak_lag

    return f0


def calculate_f0_rmse(ref_wav_path: str, synth_wav_path: str) -> float:
    """Tính sai số toàn phương trung bình F0 RMSE (Hz) giữa 2 file audio."""
    ref_audio, ref_sr = sf.read(ref_wav_path)
    synth_audio, synth_sr = sf.read(synth_wav_path)

    if ref_audio.ndim > 1:
        ref_audio = np.mean(ref_audio, axis=1)
    if synth_audio.ndim > 1:
        synth_audio = np.mean(synth_audio, axis=1)

    ref_f0 = estimate_f0(ref_audio, ref_sr)
    synth_f0 = estimate_f0(synth_audio, synth_sr)

    # Căn chỉnh chiều dài
    min_len = min(len(ref_f0), len(synth_f0))
    ref_f0 = ref_f0[:min_len]
    synth_f0 = synth_f0[:min_len]

    # Chỉ tính trên các frame có tiếng (voiced frames: cả 2 cùng > 0)
    voiced = (ref_f0 > 0) & (synth_f0 > 0)
    if np.sum(voiced) == 0:
        return 0.0

    rmse = math.sqrt(np.mean((ref_f0[voiced] - synth_f0[voiced]) ** 2))
    return round(float(rmse), 2)


def calculate_rtf(audio_duration_sec: float, inference_time_sec: float) -> float:
    """Tính Real-Time Factor (RTF). RTF < 1.0 nghĩa là nhanh hơn thời gian thực."""
    if audio_duration_sec <= 0:
        return 0.0
    return round(inference_time_sec / audio_duration_sec, 3)


def generate_benchmark_markdown_table(results: List[Dict[str, any]]) -> str:
    """Xuất bảng so sánh kết quả thực nghiệm dạng Markdown phục vụ báo cáo luận văn."""
    header = (
        "| Mô hình thực nghiệm | MCD (dB) ↓ | F0 RMSE (Hz) ↓ | RTF (CPU) ↓ | Trạng thái |\n"
        "|---|:---:|:---:|:---:|:---:|\n"
    )
    rows = []
    for r in results:
        rows.append(
            f"| **{r['model_name']}** | {r['mcd']} | {r['f0_rmse']} | {r['rtf']} | {r['status']} |"
        )
    return header + "\n".join(rows) + "\n"


if __name__ == "__main__":
    print("=" * 60)
    print("KIỂM TRA HỆ THỐNG ĐO ĐẠC HỌC THUẬT (EVALUATOR)")
    print("=" * 60)

    # Tạo 2 tín hiệu sóng âm giả lập để kiểm tra thuật toán
    sr = 16000
    t = np.linspace(0, 2.0, sr * 2)
    s1 = 0.5 * np.sin(2 * np.pi * 150 * t) + 0.2 * np.sin(2 * np.pi * 300 * t)
    s2 = 0.5 * np.sin(2 * np.pi * 155 * t) + 0.2 * np.sin(2 * np.pi * 310 * t)

    tmp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs")
    os.makedirs(tmp_dir, exist_ok=True)
    p1 = os.path.join(tmp_dir, "eval_ref.wav")
    p2 = os.path.join(tmp_dir, "eval_synth.wav")

    sf.write(p1, s1, sr)
    sf.write(p2, s2, sr)

    mcd = calculate_mcd(p1, p2)
    f0_rmse = calculate_f0_rmse(p1, p2)
    rtf = calculate_rtf(2.0, 0.4)

    print(f"• MCD đo được      : {mcd} dB")
    print(f"• F0 RMSE đo được  : {f0_rmse} Hz")
    print(f"• RTF tính toán    : {rtf}")

    table = generate_benchmark_markdown_table([
        {"model_name": "Baseline (Matcha-TTS gốc)", "mcd": 5.82, "f0_rmse": 28.4, "rtf": 0.18, "status": "Đã đo đạc"},
        {"model_name": "Proposed (Vietnamese Matcha)", "mcd": 5.12, "f0_rmse": 18.6, "rtf": 0.17, "status": "Mục tiêu"},
    ])
    print("\nBảng mẫu xuất báo cáo:\n")
    print(table)
