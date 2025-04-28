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

# Create app folder and fix permissions BEFORE switching user
RUN mkdir /app && chown appuser:appgroup /app

# Create user and group
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Set working directory
WORKDIR /app

# Switch to appuser


# Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy rest of the application
COPY app.py .
COPY frontend/build frontend/build

EXPOSE 8080

CMD ["python", "app.py"]
