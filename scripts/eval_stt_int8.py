"""WER/CER và RTF của bản triển khai CTranslate2 INT8 trên câu VietSpeech chưa từng dùng để huấn luyện.

Bộ test chuẩn 1.802 câu của bài báo được lấy bằng streaming với seed cố định; không dựng lại được đúng từng câu
khi không có manifest. Ở đây lấy mẫu mới theo cùng quy tắc băm transcript (bucket 90-99 = test, tách khỏi
bucket 0-79 dùng để huấn luyện), nên transcript không trùng bộ train; WER chỉ so sánh được về mức độ.

Cần: huggingface-cli login (VietSpeech là dataset có điều kiện truy cập), gói datasets, jiwer, faster-whisper.
Dùng: python scripts/eval_stt_int8.py --n 300 [--model speech-to-text_Luong/models/whisper-small-vi-50h-ct2]
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import time
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[1]


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def bucket(text: str) -> int:
    return int(hashlib.sha1(norm(text).lower().encode("utf-8")).hexdigest()[:8], 16) % 100


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=300)
    ap.add_argument("--dataset", default="NhutP/VietSpeech", help="doof-ferb/infore1_25hours: câu từ chỉ số 14.800 trở đi (không tham gia huấn luyện STT, ngoài miền)")
    ap.add_argument("--model", default=str(ROOT / "speech-to-text_Luong/models/whisper-small-vi-50h-ct2"))
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--compute-type", default="int8")
    ap.add_argument("--buffer", type=int, default=2000)
    ap.add_argument("--out", type=Path, default=ROOT / "reports/stt_int8_sample.json")
    args = ap.parse_args()

    from datasets import Audio, load_dataset
    from faster_whisper import WhisperModel
    from jiwer import cer, wer

    infore = "infore1" in args.dataset
    ds = load_dataset(args.dataset, split="train", streaming=True).cast_column("audio", Audio(decode=False))
    ds = ds.skip(14800) if infore else ds.shuffle(seed=42, buffer_size=args.buffer)
    samples, seen = [], 0
    for ex in ds:
        seen += 1
        text = norm(str(ex.get("transcription") or ex.get("text") or ""))
        if not text or (not infore and bucket(text) < 90):
            continue
        a = ex["audio"]
        wav, sr = sf.read(io.BytesIO(a["bytes"]), dtype="float32", always_2d=False)
        if wav.ndim > 1:
            wav = wav.mean(axis=1)
        dur = len(wav) / sr
        if not 0.5 <= dur <= 30:
            continue
        if sr != 16000:
            idx = np.linspace(0, len(wav) - 1, int(len(wav) * 16000 / sr))
            wav = np.interp(idx, np.arange(len(wav)), wav).astype(np.float32)
        samples.append((wav, text, dur))
        if len(samples) >= args.n:
            break
    print(f"collected {len(samples)} test-bucket utterances after scanning {seen}", flush=True)

    model = WhisperModel(args.model, device=args.device, compute_type=args.compute_type)
    refs, hyps, audio_s, t0 = [], [], 0.0, time.time()
    for i, (wav, text, dur) in enumerate(samples):
        segs, _ = model.transcribe(wav, language="vi", beam_size=5, vad_filter=True, condition_on_previous_text=False)
        hyps.append(norm(" ".join(s.text for s in segs)))
        refs.append(text)
        audio_s += dur
        if i % 50 == 0:
            print(i, flush=True)
    wall = time.time() - t0
    keep = [(r, h) for r, h in zip(refs, hyps) if h]
    report = {
        "what": ("Bản triển khai CT2 INT8 (beam 5, VAD) trên " + ("InfoRe1 chỉ số >=14.800 (ngoài miền, đọc tin tức, một người đọc)" if infore else "mẫu VietSpeech bucket 90-99, không phải bộ test 1.802 câu chuẩn")), "dataset": args.dataset,
        "model": args.model, "device": args.device, "compute_type": args.compute_type,
        "n": len(refs), "empty_outputs": len(refs) - len(keep),
        "wer_percent": round(100 * wer(refs, hyps), 2), "cer_percent": round(100 * cer(refs, hyps), 2),
        "audio_hours": round(audio_s / 3600, 3), "rtf": round(wall / audio_s, 3),
        "seconds_per_utterance": round(wall / len(refs), 2),
        "examples": [{"ref": r, "hyp": h} for r, h in list(zip(refs, hyps))[:8]],
    }
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "examples"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
