"""Keep only ViMMRC-origin articles (those with "options") from the combined splits,
so a reader can be specialised on ViMMRC questions without changing the split boundaries."""
import argparse
import json
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--src", type=Path, default=Path(__file__).resolve().parents[1] / "data" / "combined")
    ap.add_argument("--out", type=Path, default=Path(__file__).resolve().parents[1] / "data" / "combined_vimmrc")
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    for split in ("train", "dev", "test"):
        articles = json.loads((args.src / f"{split}_vimmrc.json").read_text(encoding="utf-8"))
        kept = [a for a in articles if "options" in a]
        (args.out / f"{split}_vimmrc.json").write_text(json.dumps(kept, ensure_ascii=False), encoding="utf-8")
        print(split, len(kept), "articles,", sum(len(a["questions"]) for a in kept), "questions")


if __name__ == "__main__":
    main()
