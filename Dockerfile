# 使用Python 3.13作为基础镜像
FROM python:3.13-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY . .

# 创建缓存目录
RUN mkdir -p cache

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV CACHE_TYPE=local

# 启动命令
CMD ["python", "main.py", "start"]