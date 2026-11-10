FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DATA_DIR=/data
ENV CACHE_DIR=/data/cache
ENV STATE_PATH=/data/state.json
ENV PLAYBACK_MODE=embed
ENV PORT=8080

RUN mkdir -p /data/cache

EXPOSE 8080

CMD ["uvicorn", "canal_automato.main:app", "--host", "0.0.0.0", "--port", "8080"]
