FROM python:3.9-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    LOG_LEVEL=INFO \
    LOG_FORMAT='%(asctime)s - %(name)s - %(levelname)s - %(message)s'

RUN apk update && apk add --no-cache \
    build-base \
    libffi-dev \
    musl-dev \
    gcc \
    python3-dev \
    jpeg-dev \
    zlib-dev \
    && pip install --upgrade pip

RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY frontend/build frontend/build

EXPOSE 8080

CMD ["python", "app.py"]
