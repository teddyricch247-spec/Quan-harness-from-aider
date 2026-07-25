FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    SETUPTOOLS_SCM_PRETEND_VERSION_FOR_AIDER_CHAT=0.75.0

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    git gcc g++ curl \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install --upgrade pip \
    && pip install -e . \
    && pip install uvicorn[standard]

RUN mkdir -p /workspace/data /workspace/logs /workspace/repos

EXPOSE 8080

CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080"]
