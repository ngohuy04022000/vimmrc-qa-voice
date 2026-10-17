"""Benchmark định lượng các engine TTS so với giọng người thật.

Thiết lập thực nghiệm:
- Tham chiếu: N câu thu âm người thật của InfoRe1 (giọng nữ, công khai trên Hugging Face), tải qua
  datasets-server và lưu đệm ở outputs/benchmark/refs/. Các engine đọc đúng văn bản của từng câu.
- Engine: Matcha-TTS (checkpoints/matcha_vi.pt), VITS MMS (facebook/mms-tts-vie),
  Edge-TTS (vi-VN-HoaiMyNeural, giọng nữ).
- Chỉ số (src/evaluator.py): MCD-DTW (dB), F0 RMSE (Hz), log-F0 RMSE (bán cung, không phụ thuộc giọng),
  CER qua ASR PhoWhisper, RTF. Dòng "Giọng người thật" cho CER trần (sai số của chính ASR).

Lưu ý diễn giải: tham chiếu là một người nói khác với giọng của các engine, nên MCD và F0 RMSE gồm cả
khác biệt về chất giọng; log-F0 RMSE và CER phản ánh độ chuẩn thanh điệu và độ rõ tốt hơn.
Notebook huấn luyện loại các câu từ chỉ số REF_OFFSET trở đi khỏi dữ liệu train, nên đây là tập kiểm thử riêng.

Chạy lệnh (từ thư mục gốc repository):
    cd text-to-speech_Duy
    python scripts/benchmark.py                 # 10 câu, đủ chỉ số
    python scripts/benchmark.py -n 5 --no-cer   # nhanh hơn, bỏ ASR
    python scripts/benchmark.py --engines matcha vits

Hoặc chạy trực tiếp từ thư mục gốc:
    python text-to-speech_Duy/scripts/benchmark.py
"""

import argparse
import json
import os
import sys
import time
import urllib.request
from typing import Dict, List

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import soundfile as sf

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (ROOT_DIR, os.path.join(ROOT_DIR, "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from src.evaluator import calculate_cer, calculate_f0_rmse, calculate_mcd, calculate_rtf, generate_benchmark_markdown_table  # noqa: E402
from src.normalizer import normalize_vietnamese_text  # noqa: E402
from src.tts_engine import get_tts_engine  # noqa: E402

OUT_DIR = os.path.join(ROOT_DIR, "outputs", "benchmark")
REF_DIR = os.path.join(OUT_DIR, "refs")
ROWS_API = "https://datasets-server.huggingface.co/rows?dataset=doof-ferb/infore1_25hours&config=default&split=train"
REF_OFFSET = 14800  # cuối dataset, cố định để tái lập kết quả
MIN_REF_SEC, MAX_REF_SEC = 2.0, 8.0

ENGINES = {
    "matcha": {"name": "Matcha-TTS (tự huấn luyện)", "ext": ".wav", "kwargs": {},
               "note": "OT-CFM, CPU cục bộ"},
    "vits": {"name": "VITS MMS (pretrained)", "ext": ".wav", "kwargs": {},
             "note": "End-to-end VAE, CPU cục bộ"},
    "edge": {"name": "Edge-TTS HoaiMy", "ext": ".mp3", "kwargs": {"voice": "vi-VN-HoaiMyNeural"},
             "note": "Cloud, RTF gồm độ trễ mạng"},
}


def fetch_references(n: int) -> List[Dict[str, str]]:
    """Tải (hoặc nạp từ bộ đệm) n câu tham chiếu InfoRe1 dài MIN_REF_SEC - MAX_REF_SEC giây."""
    os.makedirs(REF_DIR, exist_ok=True)
    index_path = os.path.join(REF_DIR, "refs.json")
    refs = []
    if os.path.exists(index_path):
        with open(index_path, encoding="utf-8") as f:
            refs = json.load(f)
    if len(refs) >= n:
        return refs[:n]

    print(f"[refs] Tải câu tham chiếu InfoRe1 (offset {REF_OFFSET})...")
    with urllib.request.urlopen(f"{ROWS_API}&offset={REF_OFFSET}&length=60", timeout=60) as resp:
        rows = json.load(resp)["rows"]
    refs = []
    for row in rows:
        path = os.path.join(REF_DIR, f"infore_{row['row_idx']}.wav")
        urllib.request.urlretrieve(row["row"]["audio"][0]["src"], path)
        if MIN_REF_SEC <= sf.info(path).duration <= MAX_REF_SEC:
            refs.append({"id": f"infore_{row['row_idx']}", "text": row["row"]["transcription"], "wav": path})
        if len(refs) >= max(n, 10):
            break
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(refs, f, ensure_ascii=False, indent=1)
    return refs[:n]


def load_asr():
    """Nạp ASR tiếng Việt PhoWhisper-base (dùng để tính CER)."""
    from transformers import pipeline

    return pipeline("automatic-speech-recognition", model="vinai/PhoWhisper-base", device="cpu",
                    generate_kwargs={"language": "vi", "task": "transcribe"})


def transcribe(asr, path: str) -> str:
    """Nhận dạng file audio bằng ASR (resample về 16 kHz mono)."""
    from src.evaluator import load_mono

    return asr(load_mono(path, 16000).astype(np.float32))["text"]


def run_benchmark(n: int, engines: List[str], with_cer: bool) -> str:
    """Chạy benchmark, in và lưu báo cáo Markdown; trả về nội dung báo cáo."""
    refs = fetch_references(n)
    asr = load_asr() if with_cer else None
    print(f"Số câu tham chiếu: {len(refs)} | engine: {', '.join(engines)} | CER: {with_cer}\n")

    results = []
    if asr is not None:
        human_cer = [calculate_cer(r["text"], transcribe(asr, r["wav"])) for r in refs]
        results.append({"model_name": "Giọng người thật (InfoRe1)", "cer": round(float(np.mean(human_cer)), 3),
                        "note": "Tham chiếu; CER trần của ASR"})

    for eid in engines:
        cfg = ENGINES[eid]
        engine = get_tts_engine(eid)
        warmup = os.path.join(OUT_DIR, f"warmup_{eid}{cfg['ext']}")
        engine.synthesize(text="xin chào", output_path=warmup, **cfg["kwargs"])  # nạp mô hình trước khi đo RTF

        scores = {k: [] for k in ("mcd", "f0_rmse", "log_f0_rmse", "cer", "rtf")}
        for ref in refs:
            out_path = os.path.join(OUT_DIR, f"{ref['id']}_{eid}{cfg['ext']}")
            t0 = time.time()
            out_path = engine.synthesize(text=normalize_vietnamese_text(ref["text"]), output_path=out_path,
                                         **cfg["kwargs"])
            scores["rtf"].append(calculate_rtf(sf.info(out_path).duration, time.time() - t0))
            scores["mcd"].append(calculate_mcd(ref["wav"], out_path))
            scores["f0_rmse"].append(calculate_f0_rmse(ref["wav"], out_path))
            scores["log_f0_rmse"].append(calculate_f0_rmse(ref["wav"], out_path, normalize_speaker=True))
            if asr is not None:
                scores["cer"].append(calculate_cer(ref["text"], transcribe(asr, out_path)))
        row = {k: (round(float(np.mean(v)), 3 if k in ("cer", "rtf") else 2) if v else None) for k, v in scores.items()}
        results.append({"model_name": cfg["name"], **row, "note": cfg["note"]})
        print(f"• {cfg['name']:<28} MCD {row['mcd']} | F0 {row['f0_rmse']} Hz | log-F0 {row['log_f0_rmse']} | "
              f"CER {row['cer']} | RTF {row['rtf']}")

    report = (
        "## Kết quả benchmark Text-to-Speech tiếng Việt\n\n"
        f"- Thời điểm: {time.strftime('%Y-%m-%d %H:%M')} · {len(refs)} câu tham chiếu InfoRe1 (giọng nữ, người thật)\n"
        "- MCD, F0: căn chỉnh DTW, dải 0 - 8 kHz, cắt khoảng lặng hai đầu · CER: ASR PhoWhisper-base · RTF: CPU\n\n"
        + generate_benchmark_markdown_table(results)
    )
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "benchmark_report.md"), "w", encoding="utf-8") as f:
        f.write(report)
    print("\n" + report)
    print(f"[OK] Báo cáo: {os.path.join(OUT_DIR, 'benchmark_report.md')}")
    return report


def main() -> None:
    """Giao diện dòng lệnh của benchmark."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-n", "--num-sentences", type=int, default=10, help="Số câu tham chiếu (mặc định 10)")
    parser.add_argument("--engines", nargs="+", default=list(ENGINES), choices=list(ENGINES))
    parser.add_argument("--no-cer", action="store_true", help="Bỏ đo CER (không cần tải PhoWhisper)")
    args = parser.parse_args()
    run_benchmark(args.num_sentences, args.engines, with_cer=not args.no_cer)


if __name__ == "__main__":
    main()
