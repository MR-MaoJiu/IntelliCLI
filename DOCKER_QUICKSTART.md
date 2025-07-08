# IntelliCLI Docker 快速开始指南

## 🚀 5分钟快速部署

### 1. 克隆项目
```bash
git clone <your-repo-url>
cd IntelliCLI
```

### 2. 初始化环境
```bash
# 使用Makefile（推荐）
make init

# 或使用部署脚本
./docker-deploy.sh init
```

### 3. 配置API密钥
编辑 `.env` 文件，填入您的API密钥：
```bash
nano .env
```

### 4. 构建和启动
```bash
# 快速启动（一键完成所有步骤）
make quick-start

# 或分步执行
make build
make start
```

### 5. 进入交互式会话
```bash
make session
```

## 🎯 常用命令

### 使用Makefile（推荐）
```bash
make help          # 查看所有可用命令
make init          # 初始化环境
make build         # 构建镜像
make start         # 启动服务
make stop          # 停止服务
make restart       # 重启服务
make logs          # 查看日志
make session       # 进入交互式会话
make config        # 运行配置向导
make status        # 查看服务状态
make cleanup       # 清理所有资源
```

### 使用部署脚本
```bash
./docker-deploy.sh help       # 查看帮助
./docker-deploy.sh init       # 初始化环境
./docker-deploy.sh build      # 构建镜像
./docker-deploy.sh start      # 启动服务
./docker-deploy.sh session    # 进入交互式会话
./docker-deploy.sh logs       # 查看日志
./docker-deploy.sh status     # 查看状态
```

### 直接使用Docker Compose
```bash
docker-compose up -d                              # 启动服务
docker-compose exec intellicli python main.py session  # 进入会话
docker-compose logs -f intellicli                 # 查看日志
docker-compose down                               # 停止服务
```

## 📁 目录结构

```
IntelliCLI/
├── Dockerfile                  # Docker镜像定义
├── docker-compose.yml          # Docker Compose配置
├── .dockerignore              # Docker构建忽略文件
├── docker-deploy.sh           # 部署脚本
├── Makefile                   # Make命令定义
├── env.example                # 环境变量示例
├── DOCKER_QUICKSTART.md       # 本文档
├── config/                    # 配置文件目录（持久化）
├── data/                      # 数据目录（持久化）
├── workspace/                 # 工作目录（可选）
└── docker/
    └── README.md              # 详细部署文档
```

## 🔧 配置说明

### 必需的API密钥
至少需要配置一个LLM提供商的API密钥：
- `GEMINI_API_KEY` - Google Gemini
- `OPENAI_API_KEY` - OpenAI GPT
- `ANTHROPIC_API_KEY` - Anthropic Claude

### 可选的搜索API密钥
- `BING_SEARCH_API_KEY` - Bing搜索
- `GOOGLE_SEARCH_API_KEY` - Google搜索
- `GOOGLE_SEARCH_ENGINE_ID` - Google搜索引擎ID

## 🎪 使用示例

### 1. 基本任务执行
```bash
# 进入会话模式
make session

# 在会话中执行任务
> 帮我分析这个Python文件的复杂度
> 创建一个简单的网页
> 搜索最新的AI技术趋势
```

### 2. 配置管理
```bash
# 运行配置向导
make config

# 配置复盘功能
make review-config

# 查看当前配置
docker-compose exec intellicli python main.py config
```

### 3. 复盘功能
```bash
# 手动复盘任务
docker-compose exec intellicli python main.py review

# 查看执行历史
docker-compose exec intellicli python main.py history
```

## 🔍 故障排除

### 常见问题

1. **容器启动失败**
   ```bash
   make logs  # 查看日志
   make status  # 检查状态
   ```

2. **API密钥配置错误**
   ```bash
   nano .env  # 编辑环境变量
   make restart  # 重启服务
   ```

3. **权限问题**
   ```bash
   sudo chown -R $USER:$USER config data workspace
   ```

### 重新部署
```bash
# 完整重新部署
make redeploy

# 清理所有资源后重新开始
make cleanup
make quick-start
```

## 📚 进阶用法

### 1. 自定义配置
将自定义配置文件放在 `config/` 目录下，容器重启后会自动加载。

### 2. 数据持久化
- 配置文件：`./config` → `/app/config`
- 历史数据：`./data` → `/app/data`
- 工作文件：`./workspace` → `/app/workspace`

### 3. 网络访问
如果需要访问外部服务，可以修改 `docker-compose.yml` 中的网络配置。

### 4. 资源限制
在 `docker-compose.yml` 中添加资源限制：
```yaml
deploy:
  resources:
    limits:
      memory: 2G
      cpus: '1.0'
```

## 🆘 获取帮助

- 查看详细文档：`docker/README.md`
- 查看项目主文档：`README.md`
- 提交Issue到GitHub仓库
- 使用 `make help` 查看所有可用命令

---

**提示**: 首次使用建议先运行 `make config` 进行基本配置，然后使用 `make session` 开始体验！ 