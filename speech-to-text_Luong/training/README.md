# Whisper Small Vietnamese Training

Run these commands in Ubuntu WSL from the repository root:

```bash
cd /mnt/d/K14/Code/vimmrc-qa-voice
source ~/venvs/whisper-train/bin/activate
uv pip install -r speech-to-text_Luong/training/requirements.txt
```

Dataset preparation uses a separate environment without CUDA libraries:

```bash
uv venv --python 3.11 ~/venvs/vietspeech-data
uv pip install --python ~/venvs/vietspeech-data/bin/python \
  -r speech-to-text_Luong/training/requirements-data.txt
```

## 1. Hugging Face access

Accept the VietSpeech access conditions in the browser, then authenticate in WSL:

```bash
hf auth login
hf auth whoami
```

Enter the token only in the terminal. Do not store it in this repository.

## 2. Stream and split 20 hours

```bash
~/venvs/vietspeech-data/bin/python \
  speech-to-text_Luong/training/prepare_vietspeech.py \
  --hours 20 \
  --output-dir ~/vimmrc-training/data/vietspeech_20h
```

The script creates FLAC files plus `train.jsonl`, `validation.jsonl`, and
`test.jsonl` using an 80/10/10 duration target. It uses a speaker/source field
when one is present. If VietSpeech exposes no such field, duplicate normalized
transcripts remain in the same split; this fallback is not speaker-disjoint.
Inspect `~/vimmrc-training/data/vietspeech_20h/stats.json` before training.

For a quick pipeline check, start with `--hours 0.25`.

## 3. Baseline

```bash
python speech-to-text_Luong/training/evaluate_models.py \
  --manifest ~/vimmrc-training/data/vietspeech_20h/test.jsonl \
  --models openai/whisper-small \
  --output reports/openai_whisper_small_baseline.json
```

Use `--limit 100` for the first check.

## 4. LoRA fine-tuning

First verify the complete training path with 10 steps:

```bash
python speech-to-text_Luong/training/train_lora.py \
  --data-dir ~/vimmrc-training/data/vietspeech_20h \
  --output-dir ~/vimmrc-training/checkpoints/whisper-small-vi-lora \
  --max-steps 10 \
  --batch-size 2
```

Then run the experiment:

```bash
python speech-to-text_Luong/training/train_lora.py \
  --data-dir ~/vimmrc-training/data/vietspeech_20h \
  --output-dir ~/vimmrc-training/checkpoints/whisper-small-vi-lora \
  --epochs 3 \
  --batch-size 4 \
  --gradient-accumulation 8 \
  --learning-rate 1e-4
```

If CUDA runs out of memory, set `--batch-size 2` and
`--gradient-accumulation 16`. Monitor training with:

```bash
tensorboard --logdir ~/vimmrc-training/checkpoints/whisper-small-vi-lora --bind_all
```

## 5. Merge and evaluate

```bash
python speech-to-text_Luong/training/merge_lora.py \
  --adapter ~/vimmrc-training/checkpoints/whisper-small-vi-lora/best_adapter \
  --output-dir ~/vimmrc-training/models/whisper-small-vi-merged

python speech-to-text_Luong/training/evaluate_models.py \
  --manifest ~/vimmrc-training/data/vietspeech_20h/test.jsonl \
  --models \
    openai/whisper-small \
    ~/vimmrc-training/models/whisper-small-vi-merged \
    NhutP/ViWhisper-small \
  --output reports/stt_model_comparison.json
```

All three models must use the same untouched test manifest for a valid comparison.

## 6. Convert and deploy

```bash
python speech-to-text_Luong/training/convert_ct2.py \
  --model ~/vimmrc-training/models/whisper-small-vi-merged \
  --output-dir ~/vimmrc-training/models/whisper-small-vi-ct2
```

Copy the converted model to Windows, then start the existing API:

```powershell
Copy-Item -Recurse `
  "\\wsl.localhost\Ubuntu-24.04\home\anhlu\vimmrc-training\models\whisper-small-vi-ct2" `
  ".\speech-to-text_Luong\models\whisper-small-vi-ct2"

$env:WHISPER_MODEL = Resolve-Path ".\speech-to-text_Luong\models\whisper-small-vi-ct2"
$env:WHISPER_DEVICE = "cpu"
$env:WHISPER_COMPUTE_TYPE = "int8"
uvicorn stt_server:app --port 8001
```

## 7. Expand to a 50-hour experiment

Keep the original two-hour validation and test manifests unchanged while
expanding only the training set. Existing audio is hard-linked, so it does not
consume duplicate disk space on the Linux filesystem.

```bash
~/venvs/vietspeech-data/bin/python \
  speech-to-text_Luong/training/expand_vietspeech.py \
  --base-dir ~/vimmrc-training/data/vietspeech_20h \
  --output-dir ~/vimmrc-training/data/vietspeech_50h \
  --total-hours 50

~/venvs/vietspeech-data/bin/python \
  speech-to-text_Luong/training/validate_expansion.py \
  --base-dir ~/vimmrc-training/data/vietspeech_20h \
  --expanded-dir ~/vimmrc-training/data/vietspeech_50h
```

Train into a separate checkpoint directory. Early stopping requires a WER
improvement of at least 0.2 points and stops after three evaluations without
that improvement.

```bash
python speech-to-text_Luong/training/train_lora.py \
  --data-dir ~/vimmrc-training/data/vietspeech_50h \
  --output-dir ~/vimmrc-training/checkpoints/whisper-small-vi-50h-lora \
  --cache-dir /mnt/d/vimmrc-training-cache/datasets \
  --epochs 3 \
  --batch-size 4 \
  --gradient-accumulation 8 \
  --learning-rate 1e-4 \
  --eval-steps 250 \
  --save-steps 250 \
  --early-stopping-patience 3 \
  --early-stopping-threshold 0.2
```

Use distinct `whisper-small-vi-50h-*` directories for merge and conversion so
the 20-hour checkpoints and deployed model remain untouched.

Merge, compare on the fixed test set, and convert the winning model:

```bash
python speech-to-text_Luong/training/merge_lora.py \
  --adapter ~/vimmrc-training/checkpoints/whisper-small-vi-50h-lora/best_adapter \
  --output-dir ~/vimmrc-training/models/whisper-small-vi-50h-merged

python speech-to-text_Luong/training/evaluate_models.py \
  --manifest ~/vimmrc-training/data/vietspeech_50h/test.jsonl \
  --models \
    ~/vimmrc-training/models/whisper-small-vi-merged \
    ~/vimmrc-training/models/whisper-small-vi-50h-merged \
  --output ~/vimmrc-training/reports/stt_20h_vs_50h.json

python speech-to-text_Luong/training/convert_ct2.py \
  --model ~/vimmrc-training/models/whisper-small-vi-50h-merged \
  --output-dir ~/vimmrc-training/models/whisper-small-vi-50h-ct2
```

Training stopped early at step 2,750 (epoch 2.1351). The 50-hour model reached
13.77% WER and 6.67% CER, compared with 15.20% WER and 7.29% CER for the
20-hour model on the identical 1,802-sample test set. Full parameters and
metrics are recorded in `results_50h.json`.