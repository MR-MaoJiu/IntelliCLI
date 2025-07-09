# IntelliCLI

**IntelliCLI** 是一个智能命令行助手，结合大型语言模型 (LLM) 和动态任务规划能力，简化复杂的软件工程任务。支持多种模型后端，智能路由，并能为复杂任务生成可执行的步骤计划。

## 🚀 核心特性

### 🐳 Docker 化部署
- **一键部署**: 使用 `make quick-start` 完成所有配置
- **零配置启动**: 无需安装 Python 环境和依赖包
- **数据持久化**: 配置和数据自动保存，重启不丢失
- **服务编排**: 自动管理 IntelliCLI 和 Ollama 服务
- **健康监控**: 实时监控服务状态和健康检查

### 🤖 智能模型系统
- **统一配置**: 首次运行自动启动交互式配置向导
- **智能路由**: 根据任务类型自动选择最合适的模型
- **多供应商支持**: Ollama、Google Gemini、OpenAI、Claude、DeepSeek
- **能力标签**: 为每个模型指定通用、代码、推理、视觉等能力

### 🔍 智能搜索系统
- **多引擎支持**: Google、Bing、Yahoo、DuckDuckGo、Startpage、SearX
- **自动切换**: 引擎失效时自动切换到其他可用引擎
- **健康监控**: 实时监控引擎状态，自动禁用失败引擎
- **故障转移**: 完全自动化的故障转移机制

### 🛠️ 强大功能
- **动态任务规划**: 将复杂任务分解为可执行步骤
- **多模态处理**: 支持文本和图像的统一处理
- **可插拔工具**: 通过简单的 Python 函数扩展功能
- **持续会话**: 支持上下文记忆和错误纠正

## 🚀 快速开始

### 方法一：Docker 部署（推荐）

**最简单的部署方式，无需配置 Python 环境**

```bash
# 1. 克隆仓库
git clone https://github.com/MR-MaoJiu/IntelliCLI.git
cd IntelliCLI

# 2. 初始化环境
make init

# 3. 编辑 API 密钥（可选）
nano .env

# 4. 一键启动
make quick-start

# 5. 进入交互式会话
make session
```

### 方法二：全局安装

```bash
# 1. 克隆仓库
git clone https://github.com/MR-MaoJiu/IntelliCLI.git
cd IntelliCLI

# 2. 运行安装脚本
./install.sh  # Unix/Linux/macOS
# 或
install.bat   # Windows

# 3. 开始使用
intellicli session
```

### 方法三：开发模式

```bash
# 1. 克隆仓库
git clone https://github.com/MR-MaoJiu/IntelliCLI.git
cd IntelliCLI

# 2. 开发模式安装
pip install -e .[dev]

# 3. 开始使用
intellicli session
```

### 方法四：本地运行

```bash
# 1. 克隆仓库
git clone https://github.com/MR-MaoJiu/IntelliCLI.git
cd IntelliCLI

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行
python main.py session
```

## ⚙️ 配置说明

### 首次运行

无论使用哪种方式，首次运行都会自动启动**配置向导**，引导您完成：

1. **选择模型供应商**: Ollama、Google Gemini、OpenAI、Claude、DeepSeek
2. **配置模型信息**: 别名、模型名称、服务器地址等
3. **设置模型能力**: 通用、代码、推理、视觉等标签
4. **选择主模型**: 默认使用的模型
5. **配置搜索引擎**: 网络搜索功能（可选）

### 环境变量配置

在 `.env` 文件或环境变量中配置 API 密钥：

```bash
# 模型 API 密钥
GEMINI_API_KEY=your_gemini_key
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_claude_key
DEEPSEEK_API_KEY=your_deepseek_key

# 搜索引擎 API 密钥
GOOGLE_SEARCH_API_KEY=your_google_key
GOOGLE_SEARCH_ENGINE_ID=your_engine_id
BING_SEARCH_API_KEY=your_bing_key
```

### 配置示例

```yaml
models:
  primary: gemma3_local
  providers:
    - alias: gemma3_local
      provider: ollama
      model_name: "gemma3:27b"
      base_url: "http://localhost:11434"
      capabilities: ["general", "code", "reasoning"]
    
    - alias: llava_vision
      provider: ollama
      model_name: "llava:34b"
      base_url: "http://localhost:11434"
      capabilities: ["vision", "general"]

search_engines:
  engines:
    google:
      api_key: "your_google_api_key"
      search_engine_id: "your_search_engine_id"
    bing:
      api_key: "your_bing_api_key"
```

## 📖 使用方法

### Docker 部署命令

```bash
make session        # 启动交互式会话
make status         # 查看服务状态
make logs           # 查看日志
make restart        # 重启服务
make stop           # 停止服务
make config         # 配置向导
make help           # 查看所有命令
```

### 全局安装命令

```bash
intellicli session          # 启动交互式会话
intellicli chat "问题"      # 单次对话
intellicli models           # 显示可用模型
intellicli config           # 显示当前配置
intellicli config-wizard    # 重新配置
intellicli search-config    # 配置搜索引擎
intellicli search-status    # 搜索引擎状态
```

### 智能路由示例

系统会根据任务类型自动选择最合适的模型：

```bash
# 图像任务 → 视觉模型
"帮我分析这张截图的内容"

# 代码任务 → 代码模型
"写一个Python函数计算斐波那契数列"

# 推理任务 → 推理模型
"分析这个算法的时间复杂度"

# 搜索任务 → 搜索引擎
"搜索最新的Python开发资讯"
```

## 🏗️ 项目结构

```
IntelliCLI/
├── main.py                    # 主入口点
├── pyproject.toml            # 项目配置
├── requirements.txt          # 依赖文件
├── config.yaml               # 配置文件
├── install.sh/.bat          # 安装脚本
├── Dockerfile               # Docker 镜像
├── docker-compose.yml       # Docker 服务编排
├── Makefile                 # 快捷命令
├── env.example              # 环境变量示例
├── /intellicli              # 主包
│   ├── cli.py              # 命令行界面
│   ├── /agent              # 智能代理
│   │   ├── planner.py      # 任务规划器
│   │   ├── executor.py     # 任务执行器
│   │   └── model_router.py # 模型路由器
│   ├── /config             # 配置管理
│   │   ├── model_config.py # 模型配置
│   │   └── search_config.py # 搜索配置
│   ├── /models             # 模型客户端
│   │   ├── base_llm.py     # 基础接口
│   │   ├── ollama_client.py # Ollama 客户端
│   │   ├── gemini_client.py # Gemini 客户端
│   │   ├── openai_client.py # OpenAI 客户端
│   │   ├── claude_client.py # Claude 客户端
│   │   └── deepseek_client.py # DeepSeek 客户端
│   ├── /tools              # 工具模块
│   │   ├── file_system.py  # 文件系统
│   │   ├── shell.py        # Shell 命令
│   │   ├── web_search.py   # 网络搜索
│   │   └── python_analyzer.py # 代码分析
│   └── /ui                 # 用户界面
│       └── display.py      # CLI 界面
└── /docs              # 文档
```

## 🔧 高级功能

### 模型能力路由

- **general**: 通用对话和文本处理
- **code**: 代码生成和编程任务
- **reasoning**: 复杂推理和分析任务
- **vision**: 图像和视觉相关任务

### 搜索引擎优先级

1. **Yahoo** - 免费，可靠性高
2. **Google** - 需要 API，质量最高
3. **Bing** - 需要 API，质量较高
4. **DuckDuckGo** - 免费，受限制
5. **Startpage** - 免费，隐私保护
6. **SearX** - 免费，不稳定

### 会话模式命令

- `help` - 显示帮助信息
- `models` - 查看可用模型
- `clear` - 清空会话记忆
- `exit` - 退出会话

## ❓ 常见问题

### 配置相关
- **Q**: 如何添加新的模型供应商？
- **A**: 运行 `intellicli config-wizard` 重新配置

- **Q**: 如何更改主模型？
- **A**: 编辑 `config.yaml` 中的 `primary` 字段或重新运行配置向导

- **Q**: 如何重置所有配置？
- **A**: 运行 `intellicli config-reset` 或删除 `config.yaml` 文件

### 搜索相关
- **Q**: 搜索功能不工作怎么办？
- **A**: 使用 `intellicli search-status` 检查状态，`intellicli search-test` 测试功能

- **Q**: 如何配置搜索引擎 API？
- **A**: 运行 `intellicli search-config` 或设置相应的环境变量

### Docker 相关
- **Q**: 如何在 Docker 中配置 API 密钥？
- **A**: 编辑 `.env` 文件，然后运行 `make restart`

- **Q**: Docker 容器启动失败怎么办？
- **A**: 使用 `make logs` 查看错误信息，`make status` 检查状态

### 其他问题
- **Q**: 支持哪些操作系统？
- **A**: 支持 Windows、macOS 和 Linux

- **Q**: 支持哪些图像格式？
- **A**: 支持 PNG、JPG、JPEG、GIF、BMP、TIFF、WebP

## 🗑️ 卸载

### Docker 部署卸载
```bash
make stop     # 停止服务
make cleanup  # 清理资源
```

### 本地安装卸载
```bash
pip uninstall intellicli
# 或
python scripts/install.py uninstall
```

## 📝 更新日志

### v1.0.0
- 🎉 首个稳定版本
- 🤖 智能模型路由系统
- 📝 动态任务规划
- 🔧 可插拔工具系统

## 📞 联系我们

- 📧 邮箱：lovemaojiu@gmail.com
- 🐛 问题报告：[GitHub Issues](https://github.com/MR-MaoJiu/IntelliCLI/issues)

## 📄 许可证

本项目采用 MIT 许可证。详情请参阅 LICENSE 文件。