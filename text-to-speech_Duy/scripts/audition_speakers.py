"""Chấm điểm độ rõ (intelligibility) của từng giọng trong Matcha-TTS bằng ASR tiếng Việt.

Mỗi speaker đọc cùng một bộ câu; PhoWhisper nhận dạng lại và tính CER (Character Error Rate).
CER thấp = phát âm rõ, đúng thanh điệu. Dùng kết quả để chọn DEFAULT_SPEAKERS trong src/matcha_engine.py,
và để so sánh trước/sau khi đổi cấu hình suy luận hoặc train lại mô hình.

Ví dụ (chạy được từ bất kỳ thư mục nào):
    python scripts/audition_speakers.py                       # chấm toàn bộ 65 speaker
    python scripts/audition_speakers.py --speakers 0 5 12     # chỉ chấm vài speaker
    python scripts/audition_speakers.py --n-timesteps 10 --temperature 0.5
    python scripts/audition_speakers.py --checkpoint checkpoints/matcha_vi_v2.pt   # chấm mô hình mới (một giọng)
"""

import argparse
import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT_DIR, "src"))

from evaluator import calculate_cer, load_mono  # noqa: E402
from matcha_engine import MatchaTTSEngine  # noqa: E402

AUDITION_SENTENCES = [
    "Hôm nay trời trong xanh, gió nhẹ thổi qua những hàng cây ven đường.",
    "Chiến thắng Điện Biên Phủ diễn ra ngày bảy tháng năm năm một nghìn chín trăm năm mươi tư.",
    "Hồ Gươm nằm ở trung tâm thủ đô Hà Nội, gắn liền với truyền thuyết vua Lê Lợi trả gươm báu.",
]


def main() -> None:
    """Sinh bộ câu thử cho từng speaker, nhận dạng lại bằng ASR và xếp hạng theo CER."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--checkpoint", default=None, help="File .pt cần chấm (mặc định: checkpoint engine tự chọn)")
    parser.add_argument("--speakers", type=int, nargs="*", default=None, help="Chỉ số speaker cần chấm (mặc định: tất cả)")
    parser.add_argument("--n-timesteps", type=int, default=10)
    parser.add_argument("--temperature", type=float, default=0.667)
    parser.add_argument("--rate", type=float, default=1.0, help="speaking_rate (>1 nhanh hơn)")
    parser.add_argument("--asr-model", default="vinai/PhoWhisper-base")
    parser.add_argument("--out-dir", default=os.path.join(ROOT_DIR, "outputs", "audition"))
    args = parser.parse_args()

    from transformers import pipeline

    asr = pipeline("automatic-speech-recognition", model=args.asr_model, device="cpu",
                   generate_kwargs={"language": "vi", "task": "transcribe"})
    engine = MatchaTTSEngine(checkpoint_path=args.checkpoint)
    engine._ensure_model_loaded()
    genders = {}
    if len(engine.speakers) > 1 and os.path.exists(engine.meta_path):
        with open(engine.meta_path, encoding="utf-8") as f:
            genders = json.load(f).get("genders", {})

    os.makedirs(args.out_dir, exist_ok=True)
    spk_ids = args.speakers if args.speakers is not None else range(max(1, len(engine.speakers)))
    results = []
    for spk in spk_ids:
        name = engine.speakers[spk] if engine.speakers else "single"
        scores = []
        for i, sentence in enumerate(AUDITION_SENTENCES):
            path = os.path.join(args.out_dir, f"spk{spk:02d}_{name}_{i}.wav")
            engine.synthesize(sentence, output_path=path, normalize=False, speaker_id=spk,
                              n_timesteps=args.n_timesteps, temperature=args.temperature,
                              speaking_rate=args.rate)
            hyp = asr(load_mono(path, 16000).astype(np.float32))["text"]
            scores.append(calculate_cer(sentence, hyp))
        mean_cer = float(np.mean(scores))
        results.append({"id": spk, "speaker": name, "gender": genders.get(name, "?"), "cer": mean_cer})
        print(f"spk {spk:2d} {name} ({genders.get(name, '?')}): CER {mean_cer:.3f}", flush=True)

    results.sort(key=lambda r: r["cer"])
    print("\nTop 5 giọng rõ nhất theo giới tính:")
    for g in ("f", "m"):
        top = [r for r in results if r["gender"] == g][:5]
        print(f"  {g}: " + ", ".join(f"{r['id']}:{r['speaker']} ({r['cer']:.3f})" for r in top))
    print(f"\nCER trung bình toàn bộ: {np.mean([r['cer'] for r in results]):.3f}")

    with open(os.path.join(args.out_dir, "audition_results.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
