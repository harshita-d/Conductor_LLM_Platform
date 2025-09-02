# backend/Dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# System deps (curl for healthchecks, tzdata optional)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl tzdata && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY backend/ ./ 

# Expose the app port
EXPOSE 8000

# Healthcheck (expects GET /healthz to return 200)
HEALTHCHECK --interval=20s --timeout=3s --retries=5 \
  CMD curl -fsS http://localhost:8000/healthz || exit 1

# Run uvicorn in multi-process mode
# Tune --workers to your CPU (start with 2)
CMD ["uvicorn", "app.main:app", \
     "--host", "0.0.0.0", "--port", "8000", \
     "--workers", "2", "--proxy-headers", "--forwarded-allow-ips", "*"]
