# Vietnamese Speech-to-Text

FastAPI service using `faster-whisper` to transcribe Vietnamese audio. The web
application sends 16 kHz mono WAV audio to `POST /api/stt`.

## Setup

Python 3.10 or newer is recommended.

```powershell
cd speech-to-text_Luong
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

The first transcription downloads the selected Whisper model from Hugging Face.
The default `small` model needs roughly 1 GB of disk space.
The default backend is CPU with `int8` computation, so CUDA is not required.

The API prefers `models/whisper-small-vi-50h-ct2`, then falls back to the
20-hour model at `models/whisper-small-vi-ct2`, and finally to the public
Whisper `small` model. `WHISPER_MODEL` always overrides this selection.

## Run

```powershell
uvicorn stt_server:app --host 0.0.0.0 --port 8001
```

Keep this server running while starting the Angular app with its proxy config.
Check the service at `http://localhost:8001/health`.

## Configuration

Environment variables can select another model or execution backend:

```powershell
$env:WHISPER_MODEL = "small"
$env:WHISPER_DEVICE = "cpu"
$env:WHISPER_COMPUTE_TYPE = "int8"
uvicorn stt_server:app --host 0.0.0.0 --port 8001
```

For an NVIDIA GPU with the required CUDA libraries, use `cuda` and `float16`.
On a CPU, `cpu` and `int8` generally use less memory. Accepted model names
include `tiny`, `base`, `small`, `medium`, and `large-v3`.

## API

```powershell
curl.exe -X POST http://localhost:8001/api/stt `
  -F "file=@question.wav;type=audio/wav"
```

Successful response:

```json
{"text":"Câu hỏi đã được nhận dạng."}
```

Uploads are limited to 25 MB. The service returns `422` when no speech is
detected and does not return internal model errors to clients.

## Fine-tuning result

`openai/whisper-small` was fine-tuned with LoRA on streamed VietSpeech subsets.
The 50-hour experiment expanded only the training split to 46 hours and kept
the original 2-hour validation and 2-hour test sets unchanged. On the same
1,802 test samples:

| Model | WER | CER |
|---|---:|---:|
| `openai/whisper-small` | 36.76% | 19.43% |
| Self-trained LoRA, 20 hours | 15.20% | 7.29% |
| Self-trained LoRA, 50 hours | **13.77%** | **6.67%** |
| `NhutP/ViWhisper-small` | 0.82% | 0.54% |

The 50-hour model improves WER by 9.46% relative to the 20-hour model and is
the preferred local deployment. The `NhutP/ViWhisper-small` score is contextual
only because that model was trained on the full VietSpeech dataset.

VietSpeech exposes no speaker/source field in this configuration. Splits keep
duplicate normalized transcripts together but cannot guarantee speaker-disjoint
evaluation. Reproduce the experiment with [training/README.md](training/README.md).