FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    musl-dev \
    tzdata \
    libc-dev \
    libffi-dev \
    openssl \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*


WORKDIR /app

COPY requirements.txt /app

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 7000
#"uvicorn app_config:create_app --host 0.0.0.0 --port 8000 --workers 4 --factory"
#CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:7000", "runserver:app"]
CMD ["uvicorn", "runserver:asgi_app", "--host", "0.0.0.0", "--port", "7000", "--workers", "4"]
