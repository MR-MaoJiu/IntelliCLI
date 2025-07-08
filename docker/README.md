# IntelliCLI Docker 部署指南

本指南将帮助您使用Docker部署和运行IntelliCLI智能命令行助手。

## 📋 前置要求

- Docker Engine 20.10+
- Docker Compose 1.29+
- 至少2GB可用内存
- 至少1GB可用磁盘空间

## 🚀 快速开始

### 1. 准备环境变量

```bash
# 复制环境变量示例文件
cp env.example .env

# 编辑环境变量文件，填入您的API密钥
nano .env
```

### 2. 创建必要的目录

```bash
# 创建配置和数据目录
mkdir -p config data workspace
```

### 3. 构建和启动服务

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f intellicli
```

### 4. 进入交互式会话

```bash
# 连接到IntelliCLI容器
docker-compose exec intellicli python main.py session
```

## 📁 目录结构

```
IntelliCLI/
├── Dockerfile              # Docker镜像构建文件
├── docker-compose.yml      # Docker Compose配置
├── .dockerignore           # Docker构建忽略文件
├── env.example             # 环境变量示例
├── config/                 # 配置文件目录（持久化）
├── data/                   # 数据目录（持久化）
├── workspace/              # 工作目录（可选挂载）
└── docker/
    └── README.md           # 本文档
```

## 🔧 配置说明

### 环境变量

| 变量名 | 说明 | 必需 |
|--------|------|------|
| `GEMINI_API_KEY` | Google Gemini API密钥 | 可选 |
| `OPENAI_API_KEY` | OpenAI API密钥 | 可选 |
| `ANTHROPIC_API_KEY` | Anthropic Claude API密钥 | 可选 |
| `BING_SEARCH_API_KEY` | Bing搜索API密钥 | 可选 |
| `GOOGLE_SEARCH_API_KEY` | Google搜索API密钥 | 可选 |
| `GOOGLE_SEARCH_ENGINE_ID` | Google搜索引擎ID | 可选 |

### 数据持久化

- **配置文件**: `./config` → `/app/config`
- **数据文件**: `./data` → `/app/data`
- **工作空间**: `./workspace` → `/app/workspace`

## 🎯 使用方式

### 1. 交互式会话模式

```bash
# 启动交互式会话
docker-compose exec intellicli python main.py session
```

### 2. 单次任务执行

```bash
# 执行单个任务
docker-compose exec intellicli python main.py task "创建一个简单的网页"
```

### 3. 配置管理

```bash
# 显示当前配置
docker-compose exec intellicli python main.py config

# 运行配置向导
docker-compose exec intellicli python main.py config-wizard

# 配置复盘功能
docker-compose exec intellicli python main.py review-config
```

### 4. 复盘功能

```bash
# 手动复盘最近任务
docker-compose exec intellicli python main.py review

# 查看任务历史
docker-compose exec intellicli python main.py history
```

## 🔍 故障排除

### 检查服务状态

```bash
# 查看所有服务状态
docker-compose ps

# 查看服务日志
docker-compose logs intellicli
docker-compose logs ollama
```

### 重启服务

```bash
# 重启IntelliCLI服务
docker-compose restart intellicli

# 重启所有服务
docker-compose restart
```

### 重新构建镜像

```bash
# 重新构建镜像
docker-compose build --no-cache intellicli

# 重新启动服务
docker-compose up -d
```

### 清理资源

```bash
# 停止并删除容器
docker-compose down

# 删除数据卷（注意：会删除所有数据）
docker-compose down -v

# 删除镜像
docker rmi intellicli:latest
```

## 🚀 高级配置

### 1. GPU支持（NVIDIA）

如果您有NVIDIA GPU，可以启用GPU支持：

1. 安装NVIDIA Container Toolkit
2. 取消docker-compose.yml中GPU相关配置的注释
3. 重新启动服务

### 2. 自定义Ollama模型

```bash
# 进入Ollama容器
docker-compose exec ollama bash

# 下载模型
ollama pull gemma3:27b
ollama pull llava:34b

# 列出已下载的模型
ollama list
```

### 3. 网络配置

如果需要自定义网络配置，可以修改docker-compose.yml中的networks部分。

### 4. 资源限制

在docker-compose.yml中添加资源限制：

```yaml
services:
  intellicli:
    # ... 其他配置
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 1G
          cpus: '0.5'
```

## 📚 更多信息

- [IntelliCLI 主要文档](../README.md)
- [配置系统说明](../docs/配置系统说明.md)
- [快速安装指南](../docs/快速安装指南.md)

## 🆘 获取帮助

如果遇到问题，请：

1. 查看日志：`docker-compose logs intellicli`
2. 检查配置：`docker-compose exec intellicli python main.py config`
3. 提交Issue到GitHub仓库 