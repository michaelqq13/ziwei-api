FROM python:3.11-slim

WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 升級 pip
RUN pip install --upgrade pip

# 複製依賴文件並安裝
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程序代碼
COPY . .

# 複製並設置啟動腳本
COPY start.sh .
RUN chmod +x start.sh

# 設置環境變數
ENV PYTHONPATH=/app
ENV PORT=8000

# 暴露端口
EXPOSE 8000

# 使用啟動腳本
CMD ["./start.sh"] 