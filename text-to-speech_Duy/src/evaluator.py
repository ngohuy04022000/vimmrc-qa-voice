"""Module đánh giá định lượng các mô hình TTS theo chuẩn học thuật.

Các chỉ số (mũi tên ↓: càng nhỏ càng tốt):
- MCD ↓ (Mel-Cepstral Distortion, dB): sai khác phổ giữa giọng tổng hợp và giọng tham chiếu,
  căn chỉnh thời gian bằng DTW.
- F0 RMSE ↓ (Hz): sai số cao độ trên các khung hữu thanh đã căn chỉnh DTW. Phụ thuộc cao độ riêng của
  từng giọng (nam/nữ), chỉ nên so khi giọng tổng hợp và tham chiếu cùng giới tính.
- log-F0 RMSE ↓ (bán cung): sai số hình dạng đường cao độ sau khi bỏ cao độ trung bình của mỗi câu,
  phản ánh độ chuẩn thanh điệu mà không phụ thuộc giọng.
- CER ↓ (Character Error Rate): tỷ lệ lỗi ký tự khi ASR nhận dạng lại giọng tổng hợp (độ rõ, đúng thanh).
- RTF ↓ (Real-Time Factor): thời gian sinh / thời lượng audio; < 1 là nhanh hơn thời gian thực.
"""

import math
import os
from typing import Dict, List, Optional, Tuple

import numpy as np
import soundfile as sf
from scipy.fft import dct
from scipy.signal import resample_poly, spectrogram

try:
    from .vi_frontend import clean_chars
except ImportError:
    from vi_frontend import clean_chars

# Tần số lấy mẫu chung: mọi file được resample về đây trước khi so sánh
EVAL_SAMPLE_RATE = 22050
FRAME_SIZE = 1024
HOP_SIZE = 256


def load_mono(path: str, target_sr: int = EVAL_SAMPLE_RATE) -> np.ndarray:
    """Đọc file audio (wav/mp3/...), trộn về mono, resample về `target_sr` và cắt khoảng lặng hai đầu.

    Args:
        path: Đường dẫn file audio.
        target_sr: Tần số lấy mẫu đích (Hz).

    Returns:
        Mảng float64 một chiều ở tần số `target_sr`, đã cắt khoảng lặng hai đầu.
    """
    audio, sr = sf.read(path)
    if audio.ndim > 1:
        audio = audio.mean(axis=1)
    if sr != target_sr:
        g = math.gcd(sr, target_sr)
        audio = resample_poly(audio, target_sr // g, sr // g)
    return trim_silence(audio, target_sr)


def trim_silence(audio: np.ndarray, sr: int = EVAL_SAMPLE_RATE, top_db: float = 40.0) -> np.ndarray:
    """Cắt khoảng lặng ở hai đầu tín hiệu (khung 10 ms có năng lượng thấp hơn đỉnh quá `top_db` dB).

    Hai đầu câu chỉ chứa im lặng / nhiễu nền, khác nhau tùy hệ thống, nên được loại khỏi phép đo
    để MCD và F0 phản ánh phần tiếng nói.
    """
    frame = int(0.01 * sr)
    n_frames = len(audio) // frame
    if n_frames == 0:
        return audio
    rms = np.sqrt((audio[: n_frames * frame].reshape(n_frames, frame) ** 2).mean(axis=1) + 1e-12)
    voiced = np.where(20 * np.log10(rms / rms.max()) > -top_db)[0]
    if len(voiced) == 0:
        return audio
    return audio[voiced[0] * frame: (voiced[-1] + 1) * frame]


def extract_mel_cepstrum(
    audio: np.ndarray,
    sr: int,
    n_mfcc: int = 25,
    n_mels: int = 40,
    fmax: float = 8000.0,
    n_fft: int = FRAME_SIZE,
    hop_length: int = HOP_SIZE,
) -> np.ndarray:
    """Trích xuất ma trận hệ số Mel-cepstral (MFCC) theo từng khung.

    Gồm các bước: phổ công suất (STFT cửa sổ Hann) → ngân hàng bộ lọc Mel tam giác trong [0, fmax] →
    log biên độ → DCT-II, chuẩn hóa theo định nghĩa mel-cepstrum của công thức MCD. Giới hạn fmax = 8 kHz là dải tần chung của mọi hệ thống được so sánh
    (dữ liệu huấn luyện VIVOS/InfoRe gốc 16 kHz); nếu không, dải trống trên 8 kHz của giọng tổng hợp
    sẽ chi phối toàn bộ phép đo.

    Args:
        audio: Tín hiệu mono.
        sr: Tần số lấy mẫu (Hz).
        n_mfcc: Số hệ số cepstral giữ lại (gồm cả c0); mặc định bậc 24 như các nghiên cứu TTS.
        n_mels: Số bộ lọc Mel.
        fmax: Tần số cao nhất của ngân hàng bộ lọc (Hz).
        n_fft: Độ dài khung FFT (mẫu).
        hop_length: Bước nhảy giữa hai khung (mẫu).

    Returns:
        Ma trận kích thước (số khung, n_mfcc).
    """
    frequencies, _, sxx = spectrogram(audio, fs=sr, nperseg=n_fft, noverlap=n_fft - hop_length, window="hann")
    # scipy trả về mật độ phổ (đã chia fs·Σw²) -> đưa về thang |X|² để mức sàn log không lấn át tín hiệu
    sxx = sxx * sr * float(np.sum(np.hanning(n_fft) ** 2))

    # Ngân hàng bộ lọc Mel tam giác trên dải [0, fmax]
    high_freq_mel = 2595.0 * np.log10(1.0 + min(fmax, sr / 2.0) / 700.0)
    mel_points = np.linspace(0.0, high_freq_mel, n_mels + 2)
    hz_points = 700.0 * (10.0 ** (mel_points / 2595.0) - 1.0)
    bin_points = np.floor((n_fft + 1) * hz_points / sr).astype(int)

    fbank = np.zeros((n_mels, len(frequencies)))
    for m in range(1, n_mels + 1):
        f_m_minus, f_m, f_m_plus = bin_points[m - 1], bin_points[m], bin_points[m + 1]
        for k in range(f_m_minus, f_m):
            if f_m != f_m_minus:
                fbank[m - 1, k] = (k - f_m_minus) / (f_m - f_m_minus)
        for k in range(f_m, f_m_plus):
            if f_m_plus != f_m:
                fbank[m - 1, k] = (f_m_plus - k) / (f_m_plus - f_m)

    # Log biên độ (= ½ log công suất), đúng đơn vị của công thức MCD
    log_mel = 0.5 * np.log(np.maximum(fbank @ sxx, 1e-10))

    # Mel-cepstrum dạng chuỗi cosin: ln A(ω) = c0 + 2·Σ c_m·cos(mω)  =>  c_m = Σ_k ln A_k·cos(…) / N.
    # scipy DCT-II (không chuẩn hóa) = 2·Σ_k ln A_k·cos(…), nên chia cho 2N.
    return (dct(log_mel, type=2, axis=0)[:n_mfcc] / (2 * n_mels)).T


def dynamic_time_warping(s1: np.ndarray, s2: np.ndarray) -> Tuple[float, List[Tuple[int, int]]]:
    """Căn chỉnh thời gian động (DTW) giữa hai chuỗi vector đặc trưng theo khoảng cách Euclid.

    Args:
        s1: Chuỗi thứ nhất, kích thước (n, d).
        s2: Chuỗi thứ hai, kích thước (m, d).

    Returns:
        Tuple (chi phí tích lũy chuẩn hóa theo độ dài đường đi, đường đi tối ưu [(i, j), ...]).
    """
    n, m = len(s1), len(s2)
    dist = np.sqrt(((s1[:, None, :] - s2[None, :, :]) ** 2).sum(axis=-1))
    cost = np.full((n + 1, m + 1), np.inf)
    cost[0, 0] = 0.0
    for i in range(1, n + 1):
        row_prev, row = cost[i - 1], cost[i]
        for j in range(1, m + 1):
            row[j] = dist[i - 1, j - 1] + min(row_prev[j], row[j - 1], row_prev[j - 1])

    # Truy vết đường đi tối ưu
    i, j = n, m
    path = []
    while i > 0 and j > 0:
        path.append((i - 1, j - 1))
        _, (i, j) = min(
            ((cost[i - 1, j - 1], (i - 1, j - 1)), (cost[i - 1, j], (i - 1, j)), (cost[i, j - 1], (i, j - 1))),
            key=lambda x: x[0],
        )
    path.reverse()
    return float(cost[n, m] / len(path)), path


def _aligned_mfcc(ref_audio: np.ndarray, synth_audio: np.ndarray) -> Tuple[np.ndarray, np.ndarray, List[Tuple[int, int]]]:
    """Tính MFCC (bỏ c0 năng lượng) của hai tín hiệu và đường căn chỉnh DTW giữa chúng."""
    ref_mfcc = extract_mel_cepstrum(ref_audio, EVAL_SAMPLE_RATE)[:, 1:]
    synth_mfcc = extract_mel_cepstrum(synth_audio, EVAL_SAMPLE_RATE)[:, 1:]
    _, path = dynamic_time_warping(ref_mfcc, synth_mfcc)
    return ref_mfcc, synth_mfcc, path


def calculate_mcd(ref_wav_path: str, synth_wav_path: str) -> float:
    """Tính Mel-Cepstral Distortion (dB) giữa audio tham chiếu và audio tổng hợp.

    MCD = (10·√2 / ln 10) · trung bình ‖c_ref − c_synth‖ trên đường căn chỉnh DTW (hệ số c1 trở đi).

    Args:
        ref_wav_path: File audio tham chiếu (giọng người thật).
        synth_wav_path: File audio tổng hợp.

    Returns:
        MCD (dB), làm tròn 2 chữ số. Càng nhỏ càng gần tham chiếu.
    """
    ref_mfcc, synth_mfcc, path = _aligned_mfcc(load_mono(ref_wav_path), load_mono(synth_wav_path))
    diffs = [np.linalg.norm(ref_mfcc[i] - synth_mfcc[j]) for i, j in path]
    return round((10.0 * math.sqrt(2.0)) / math.log(10.0) * float(np.mean(diffs)), 2)


def estimate_f0(audio: np.ndarray, sr: int, frame_size: int = FRAME_SIZE, hop_size: int = HOP_SIZE) -> np.ndarray:
    """Ước lượng đường cao độ F0 theo từng khung bằng thuật toán pYIN (Mauch & Dixon, 2014).

    pYIN dùng mô hình Markov ẩn để chọn ứng viên cao độ nhất quán theo thời gian, tránh lỗi nhảy bát độ
    (×2, ×½) thường gặp ở phương pháp tự tương quan đơn giản trên giọng nói thật.

    Args:
        audio: Tín hiệu mono.
        sr: Tần số lấy mẫu (Hz).
        frame_size: Độ dài khung (mẫu), trùng với khung MFCC để dùng chung đường căn chỉnh DTW.
        hop_size: Bước nhảy giữa hai khung (mẫu).

    Returns:
        Mảng F0 (Hz) theo khung, dải 60 - 400 Hz; 0 ở khung vô thanh / im lặng.
    """
    import librosa

    if len(audio) < frame_size:
        return np.zeros(0)
    f0, voiced, _ = librosa.pyin(
        audio.astype(np.float64), fmin=60.0, fmax=400.0, sr=sr,
        frame_length=frame_size, hop_length=hop_size, center=False,
    )
    return np.where(voiced & np.isfinite(f0), f0, 0.0)


def calculate_f0_rmse(ref_wav_path: str, synth_wav_path: str, normalize_speaker: bool = False) -> float:
    """Tính sai số cao độ giữa audio tham chiếu và audio tổng hợp trên các khung hữu thanh đã căn chỉnh DTW.

    Args:
        ref_wav_path: File audio tham chiếu.
        synth_wav_path: File audio tổng hợp.
        normalize_speaker: False → F0 RMSE tính bằng Hz (phụ thuộc cao độ riêng của giọng).
            True → log-F0 RMSE tính bằng bán cung sau khi trừ log-F0 trung bình của từng câu,
            chỉ so hình dạng đường thanh điệu.

    Returns:
        RMSE làm tròn 2 chữ số; 0.0 nếu không có khung hữu thanh chung.
    """
    ref_audio, synth_audio = load_mono(ref_wav_path), load_mono(synth_wav_path)
    _, _, path = _aligned_mfcc(ref_audio, synth_audio)
    ref_f0 = estimate_f0(ref_audio, EVAL_SAMPLE_RATE)
    synth_f0 = estimate_f0(synth_audio, EVAL_SAMPLE_RATE)

    pairs = np.array([(ref_f0[i], synth_f0[j]) for i, j in path if i < len(ref_f0) and j < len(synth_f0)])
    if len(pairs) == 0:
        return 0.0
    pairs = pairs[(pairs[:, 0] > 0) & (pairs[:, 1] > 0)]
    if len(pairs) == 0:
        return 0.0

    if normalize_speaker:
        semitones = 12.0 * np.log2(pairs)
        semitones -= semitones.mean(axis=0, keepdims=True)
        return round(float(np.sqrt(np.mean((semitones[:, 0] - semitones[:, 1]) ** 2))), 2)
    return round(float(np.sqrt(np.mean((pairs[:, 0] - pairs[:, 1]) ** 2))), 2)


def edit_distance(a: str, b: str) -> int:
    """Khoảng cách Levenshtein (số phép chèn/xóa/thay ký tự tối thiểu) giữa hai chuỗi."""
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def calculate_cer(ref_text: str, hyp_text: str) -> float:
    """Tính Character Error Rate giữa văn bản gốc và kết quả ASR nhận dạng lại giọng tổng hợp.

    Hai chuỗi được đưa về cùng dạng (chữ thường, bỏ dấu câu/chữ số, đánh vần chữ viết tắt)
    bằng `vi_frontend.clean_chars` trước khi so.

    Returns:
        CER trong [0, +∞); 0 là nhận dạng đúng hoàn toàn.
    """
    ref, hyp = clean_chars(ref_text), clean_chars(hyp_text)
    return edit_distance(ref, hyp) / max(1, len(ref))


def calculate_rtf(audio_duration_sec: float, inference_time_sec: float) -> float:
    """Tính Real-Time Factor = thời gian sinh / thời lượng audio. RTF < 1.0 là nhanh hơn thời gian thực."""
    if audio_duration_sec <= 0:
        return 0.0
    return round(inference_time_sec / audio_duration_sec, 3)


def generate_benchmark_markdown_table(results: List[Dict[str, object]]) -> str:
    """Xuất bảng so sánh kết quả thực nghiệm dạng Markdown.

    Args:
        results: Mỗi phần tử là một dict gồm các khóa `model_name`, `mcd`, `f0_rmse`, `log_f0_rmse`,
            `cer`, `rtf`, `note`. Giá trị None được hiển thị là "–".

    Returns:
        Chuỗi bảng Markdown.
    """

    def fmt(value: Optional[object]) -> str:
        """Định dạng một ô bảng; None hiển thị là "–"."""
        return "–" if value is None else str(value)

    lines = [
        "| Mô hình | MCD (dB) ↓ | F0 RMSE (Hz) ↓ | log-F0 RMSE (bán cung) ↓ | CER ↓ | RTF ↓ | Ghi chú |",
        "|---|:---:|:---:|:---:|:---:|:---:|---|",
    ]
    for r in results:
        lines.append(
            f"| **{r['model_name']}** | {fmt(r.get('mcd'))} | {fmt(r.get('f0_rmse'))} | "
            f"{fmt(r.get('log_f0_rmse'))} | {fmt(r.get('cer'))} | {fmt(r.get('rtf'))} | {r.get('note', '')} |"
        )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    # Tự kiểm tra trên tín hiệu tổng hợp: hai âm điều hòa lệch nhau ~3% tần số
    sr = EVAL_SAMPLE_RATE
    t = np.linspace(0, 2.0, sr * 2, endpoint=False)
    s1 = 0.5 * np.sin(2 * np.pi * 150 * t) + 0.2 * np.sin(2 * np.pi * 300 * t)
    s2 = 0.5 * np.sin(2 * np.pi * 155 * t) + 0.2 * np.sin(2 * np.pi * 310 * t)
    tmp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs")
    os.makedirs(tmp_dir, exist_ok=True)
    p1, p2 = os.path.join(tmp_dir, "eval_ref.wav"), os.path.join(tmp_dir, "eval_synth.wav")
    sf.write(p1, s1, sr)
    sf.write(p2, s2, sr)

    print(f"MCD          : {calculate_mcd(p1, p2)} dB")
    print(f"F0 RMSE      : {calculate_f0_rmse(p1, p2)} Hz (kỳ vọng ~5 Hz)")
    print(f"log-F0 RMSE  : {calculate_f0_rmse(p1, p2, normalize_speaker=True)} bán cung (kỳ vọng ~0)")
    print(f"CER          : {calculate_cer('Hồ Gươm', 'hồ gươm'):.3f} (kỳ vọng 0)")
    print(f"RTF          : {calculate_rtf(2.0, 0.4)}")
