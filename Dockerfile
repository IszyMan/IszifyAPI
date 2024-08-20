FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    musl-dev \
    tzdata \
    libc-dev \
    libffi-dev \
    openssl

WORKDIR /app

COPY requirements.txt /app

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 7000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:7000", "runserver:app"]
