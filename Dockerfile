FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    procps \
    iproute2 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Створення користувача без прав root
RUN useradd -m -u 10001 -s /bin/bash appuser

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ /app/app/
RUN chown -R appuser:appuser /app

ENV APP_PORT=5000 \
    APP_VERSION=1.0.0 \
    APP_STATUS=BROKEN \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

USER appuser

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app.main:app"]