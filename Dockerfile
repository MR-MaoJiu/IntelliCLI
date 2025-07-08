# 使用官方Python运行时作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    git \
    curl \
    vim \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt pyproject.toml ./

# 安装Python依赖
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY intellicli/ ./intellicli/
COPY main.py ./
COPY config.yaml.template ./

# 安装项目（可编辑模式）
RUN pip install -e .

# 创建配置和数据目录
RUN mkdir -p /app/data /app/config

# 创建非root用户
RUN useradd --create-home --shell /bin/bash intellicli && \
    chown -R intellicli:intellicli /app

# 切换到非root用户
USER intellicli

# 设置默认配置文件位置
ENV INTELLICLI_CONFIG_PATH=/app/config/config.yaml

# 暴露端口（如果需要Web服务）
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import intellicli; print('IntelliCLI is healthy')" || exit 1

# 默认命令
CMD ["python", "main.py", "--help"] 