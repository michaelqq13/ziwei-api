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

# 設置環境變數
ENV PYTHONPATH=/app

# 暴露端口
EXPOSE 8000

# 運行遷移並啟動應用
CMD sh -c "alembic upgrade head && python app/main.py" 