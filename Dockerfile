
# 1. Base image
FROM python:3.12-slim

# 2. Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# RUN 1: Cài chứng chỉ CA cần thiết, dọn cache package
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy file khai báo dependencies trước để tận dụng cache
COPY requirements.txt .

# RUN 2: Cài thư viện Python
RUN pip install --no-cache-dir -r requirements.txt

# RUN 3: Tạo user và group không có quyền quản trị
RUN groupadd --system appgroup \
    && useradd --system --gid appgroup \
       --home-dir /nonexistent \
       --shell /usr/sbin/nologin appuser

# RUN 4: Chuẩn bị thư mục ứng dụng và phân quyền
RUN mkdir -p /app \
    && chown -R appuser:appgroup /app

# Sao chép mã nguồn và script khởi động
COPY --chown=appuser:appgroup app.py /app/app.py
COPY --chown=root:root docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

# RUN 5: Cấp quyền đọc và thực thi script
RUN chmod 0555 /usr/local/bin/docker-entrypoint.sh \
    && chmod 0444 /app/app.py

# Chạy ứng dụng bằng user không phải root
USER appuser

EXPOSE 8000

# ENTRYPOINT: Script khởi động cố định
ENTRYPOINT ["/bin/sh", "/usr/local/bin/docker-entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]