# MentorMind AI — production backend image (Railway / Render)
# Build from repo root: docker build -f Dockerfile -t mentormind-api .

FROM python:3.12-slim

WORKDIR /app

# System deps for some ML / PDF optional packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app ./app
COPY backend/start.sh ./start.sh
RUN chmod +x ./start.sh

# ML artifacts + feature scripts (copy local joblib if present in build context)
COPY ml-models ./ml-models
COPY datasets/scripts ./datasets/scripts

ENV ML_MODELS_DIR=/app/ml-models
ENV PYTHONUNBUFFERED=1
ENV DEBUG=false

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health')" || exit 1

CMD ["./start.sh"]
