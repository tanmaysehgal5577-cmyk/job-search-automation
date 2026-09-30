FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright \
    HEADLESS=true

WORKDIR /app

# Dependencies first so this layer is cached until requirements change.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && playwright install --with-deps chromium \
    && rm -rf /var/lib/apt/lists/*

COPY src ./src

# Run as a non-root user; results are written to /data (mount a volume there).
RUN useradd --create-home appuser && mkdir /data && chown appuser /data
USER appuser
ENV OUTPUT_DIR=/data/output SCREENSHOT_DIR=/data/screenshots LOG_DIR=/data/logs

ENTRYPOINT ["python", "-m", "job_automation"]
CMD ["search", "--limit", "20", "--format", "csv"]
