# ==========================================
# Multi-stage Dockerfile for ViMMRC Voice Q&A
# ==========================================

# Stage 1: Build Angular Web Interface
FROM node:22-alpine AS frontend-builder
WORKDIR /app

COPY web-interface_Luong/package*.json ./
RUN npm ci --ignore-scripts || npm install

COPY web-interface_Luong/ ./
RUN npm run build

# Stage 2: Runtime Backend & Static Serving
# shortcut: pin theo digest khi build có mạng
FROM python:3.11-slim AS runtime
WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    WHISPER_DEVICE=cpu \
    TTS_ENGINE=matcha \
    PORT=8000 \
    HF_HOME=/opt/hf \
    NUMBA_CACHE_DIR=/tmp/numba \
    MPLCONFIGDIR=/tmp/mpl

# Người dùng không root. /app giữ quyền root (app chỉ đọc); app chỉ ghi được HF cache và outputs/.
RUN useradd -m -u 10001 app && mkdir -p /opt/hf && chown app:app /opt/hf

# Install required system packages for audio processing (ffmpeg, libsndfile) and health check (curl)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (using PyTorch CPU wheels for lightweight container size)
COPY requirements-docker.txt .
RUN pip install --no-cache-dir --default-timeout=300 --retries 10 --extra-index-url https://download.pytorch.org/whl/cpu -r requirements-docker.txt

# e5 query encoder for the dense Wikipedia index (data/kb_wiki_full/shard_*/embeddings.npy)
USER app
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('intfloat/multilingual-e5-small')" \
 && python -c "from sentence_transformers import CrossEncoder; CrossEncoder('BAAI/bge-reranker-v2-m3')"
USER root

# Copy repository source code, datasets, and pre-trained checkpoints
COPY . .

RUN python text-to-speech_Duy/scripts/setup_matcha.py \
    && test -f text-to-speech_Duy/checkpoints/matcha_vi.pt \
    && test -f text-to-speech_Duy/checkpoints/matcha_vi_hifigan.pt

# Copy compiled Angular frontend from builder stage into expected path
COPY --from=frontend-builder /app/dist/web-interface/browser /app/web-interface_Luong/dist/web-interface/browser

# outputs/ là volume ghi của compose; trên host Linux thư mục bind-mount phải ghi được bởi uid 10001
RUN mkdir -p text-to-speech_Duy/outputs && chown app:app text-to-speech_Duy/outputs

EXPOSE 8000

# Container healthcheck testing the unified backend health endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

USER app

CMD ["python", "-m", "uvicorn", "scripts.api_server:app", "--host", "0.0.0.0", "--port", "8000"]
