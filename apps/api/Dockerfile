FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY apps/api/pyproject.toml apps/api/README.md /app/apps/api/
COPY apps/api/src /app/apps/api/src
COPY config.yaml /app/config.yaml

WORKDIR /app/apps/api
RUN pip install --no-cache-dir -e .

ENV QUANT_OS_CONFIG_PATH=/app/config.yaml
# Runs as root so a mounted ./data volume stays writable in local Compose.
# Do not publish port 8000 onto an untrusted network.
EXPOSE 8000

CMD ["uvicorn", "quant_os_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
