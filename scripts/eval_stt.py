"""Compare Whisper models on spoken versions of dev questions: WER and downstream retrieval R@1.

Audio is synthesized with gTTS so the test does not reuse the project's own TTS voice.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from eval_e2e import eval_rows  # noqa: E402
from mrc_data import normalize_text  # noqa: E402
from retrieval_client import Retriever  # noqa: E402



def wer(ref: str, hyp: str) -> tuple[int, int]:
    r, h = normalize_text(ref).split(), normalize_text(hyp).split()
    d = list(range(len(h) + 1))
    for i, rw in enumerate(r, 1):
        prev, d[0] = d[0], i
        for j, hw in enumerate(h, 1):
            prev, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, prev + (rw != hw))
    return d[len(h)], len(r)


def synth(rows, out: Path):
    from gtts import gTTS
    out.mkdir(parents=True, exist_ok=True)
    for i, row in enumerate(rows):
        path = out / f"{i:03d}.mp3"
        if not path.exists():
            gTTS(row["question"], lang="vi").save(str(path))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--n", type=int, default=100)
    ap.add_argument("--audio-dir", type=Path, default=ROOT / "data" / "stt_eval_audio")
    ap.add_argument("--models", nargs="+", default=["small", str(ROOT / "speech-to-text_Luong/models/whisper-small-vi-50h-ct2")])
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()

    index = Retriever.load(ROOT / "data/vimmrc_index.json")
    rows = eval_rows("dev", index, args.n)
    synth(rows, args.audio_dir)

    from faster_whisper import WhisperModel
    report = {"questions": len(rows), "voice": "gTTS vi",
              "reference_R@1": sum(index.search(r["question"], 1)[0]["id"] == r["passage_id"] for r in rows) / len(rows)}
    for name in args.models:
        model = WhisperModel(name, device="cpu", compute_type="int8")
        errors = words = hits = 0
        samples = []
        for i, row in enumerate(rows):
            segs, _ = model.transcribe(str(args.audio_dir / f"{i:03d}.mp3"), language="vi", beam_size=5, vad_filter=True)
            text = " ".join(s.text.strip() for s in segs)
            e, n = wer(row["question"], text)
            errors, words = errors + e, words + n
            found = index.search(text, 1) if text.strip() else []
            hits += bool(found) and found[0]["id"] == row["passage_id"]
            if len(samples) < 5 and e:
                samples.append({"ref": row["question"], "hyp": text})
        key = Path(name).name
        report[key] = {"WER": errors / words, "R@1_from_transcript": hits / len(rows), "error_samples": samples}
        print(key, report[key]["WER"], report[key]["R@1_from_transcript"], flush=True)
    if args.output:
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
