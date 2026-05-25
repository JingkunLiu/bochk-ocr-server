# ddddocr 在 Python 3.9 环境下运行最为稳定
FROM python:3.9-slim

WORKDIR /app

# ddddocr 底层依赖 OpenCV，需要安装一些系统级图形库
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# 使用清华源加速国内依赖安装
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY . .

# 暴露 FastAPI 默认端口
EXPOSE 8080

# 启动服务
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080"]
