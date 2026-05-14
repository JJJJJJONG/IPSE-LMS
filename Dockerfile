# ==========================================
# Stage 1: builder — 의존성 설치 + Tailwind 빌드
# ==========================================
FROM python:3.12-slim AS builder

WORKDIR /app

# 시스템 의존성 (Pillow 빌드용)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY requirements/base.txt requirements/base.txt
COPY requirements/production.txt requirements/production.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements/production.txt

# pytailwindcss 설치 및 CSS 빌드
RUN pip install --no-cache-dir pytailwindcss
COPY static/src/input.css static/src/input.css
RUN tailwindcss -i static/src/input.css -o static/css/tailwind.css --minify

# ==========================================
# Stage 2: runtime — 최소 이미지
# ==========================================
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings

WORKDIR /app

# 런타임 시스템 의존성
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# builder에서 설치된 패키지 복사
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 소스 코드 복사
COPY . .

# builder에서 빌드된 Tailwind CSS 덮어쓰기
COPY --from=builder /app/static/css/tailwind.css static/css/tailwind.css

# entrypoint 실행 권한 부여
RUN chmod +x docker/entrypoint.sh

# media 볼륨 마운트 포인트
RUN mkdir -p /app/media /app/staticfiles

EXPOSE 8000

ENTRYPOINT ["docker/entrypoint.sh"]
