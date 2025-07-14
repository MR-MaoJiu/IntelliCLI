# IntelliCLI

[🇺🇸 English Version](README_EN.md) | [📖 MCP 使用指南](docs/MCP_GUIDE.md) | [📖 MCP User Guide](docs/MCP_GUIDE_EN.md)

**IntelliCLI** 是一个智能命令行助手，结合大型语言模型 (LLM) 和动态任务规划能力，简化复杂的软件工程任务。支持多种模型后端，智能路由，并能为复杂任务生成可执行的步骤计划。

## 🚀 核心特性

### 🧠 智能续接规划 
- **智能错误恢复**: 出现错误后不会完全重新规划，而是从失败位置智能续接
- **保留成功步骤**: 自动保持已完成步骤的状态和输出，避免重复工作
- **上下文感知规划**: 规划器理解当前进度，生成针对性的后续计划
- **累积进度显示**: 实时显示总体完成进度，包括跨轮次的累积统计
- **失败位置分析**: 智能分析失败原因，生成修复或替代方案

### 🧠 智能双层模型架构 
- **主模型主导规划**: 使用主模型进行一致的任务分解和整体思考
- **专业模型执行**: 根据任务类型动态选择最合适的专业模型执行
- **配置驱动路由**: 完全基于用户配置的模型能力进行智能路由
- **优先级系统**: 支持模型优先级设置，精准控制模型选择

### 🔄 任务复盘功能 
- **智能分析**: 自动分析任务执行结果，识别问题和改进机会
- **补充计划**: 为未完成的任务生成补充执行计划
- **历史记录**: 完整的任务执行历史和复盘记录
- **迭代改进**: 支持多轮改进和优化

### 🛠️ AI增强工具系统 
- **智能图像处理**: AI驱动的图像分析、风格识别、内容提取
- **智能文档管理**: AI生成技术文档、项目架构分析
- **智能代码分析**: 多维度代码分析、质量评估、安全检查
- **动态模型注入**: 工具可根据需要动态使用不同的专业模型

### 🖥️ 智能Shell执行系统
- **透明命令执行**: 命令执行完全如同直接在终端操作，保持原生体验
- **智能模式切换**: 自动检测命令类型，动态选择最佳执行模式
- **学习适应机制**: 系统自动学习命令特征，优化后续执行策略
- **问题自动检测**: 实时监控输出格式，检测到异常自动切换执行方式
- **交互式命令支持**: 完美支持Vue CLI、React CLI等复杂交互式脚手架工具

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
- **优先级管理**: 支持1-100的模型优先级设置

### 🔍 智能搜索系统
- **多引擎支持**: Google、Bing、Yahoo、DuckDuckGo、Startpage、SearX
- **自动切换**: 引擎失效时自动切换到其他可用引擎
- **健康监控**: 实时监控引擎状态，自动禁用失败引擎
- **故障转移**: 完全自动化的故障转移机制

### 🔧 MCP (Model Context Protocol) 支持 (v1.1 新增)
- **协议标准**: 支持开放的 MCP 标准，连接外部工具和数据源
- **多服务器管理**: 同时连接多个 MCP 服务器，统一工具管理
- **预设服务器**: 内置文件系统、数据库、搜索等常用服务器配置
- **动态工具加载**: 自动发现和加载 MCP 工具，无缝集成到规划系统
- **健康检查**: 自动监控服务器状态，支持断线重连
- **冲突解决**: 智能处理同名工具冲突，确保系统稳定

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
4. **设置模型优先级**: 1-100的优先级范围，控制模型选择
5. **选择主模型**: 默认使用的模型
6. **配置搜索引擎**: 网络搜索功能（可选）
7. **配置复盘功能**: 任务复盘和自动改进（可选）

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
  primary: claude_primary
  providers:
    - alias: claude_primary
      provider: claude
      model_name: "claude-3-5-sonnet-20241022"
      capabilities: ["general", "code", "reasoning", "vision"]
      priority: 90
    
    - alias: deepseek_coder
      provider: deepseek
      model_name: "deepseek-coder"
      capabilities: ["code", "reasoning"]
      priority: 85
    
    - alias: gemma3_local
      provider: ollama
      model_name: "gemma3:27b"
      base_url: "http://localhost:11434"
      capabilities: ["general", "code", "reasoning"]
      priority: 70
    
    - alias: llava_vision
      provider: ollama
      model_name: "llava:34b"
      base_url: "http://localhost:11434"
      capabilities: ["vision", "general"]
      priority: 80

# 任务复盘功能配置
task_review:
  enabled: true
  auto_review: false
  review_threshold: 0.8
  max_iterations: 3

search_engines:
  engines:
    google:
      api_key: "your_google_api_key"
      search_engine_id: "your_search_engine_id"
      enabled: true
    bing:
      api_key: "your_bing_api_key"
      enabled: true
    duckduckgo:
      enabled: true
      default: true
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
# 基础命令
intellicli session          # 启动交互式会话
intellicli chat "问题"      # 单次对话
intellicli task "任务"      # 执行复杂任务
intellicli task --review "任务"  # 执行任务并启用复盘

# 模型管理
intellicli models           # 显示可用模型
intellicli config           # 显示当前配置
intellicli config-wizard    # 重新配置
intellicli config-edit      # 直接编辑配置文件
intellicli config-reset     # 重置配置

# 复盘功能 
intellicli review           # 复盘最近的任务
intellicli review --goal "任务目标"  # 复盘指定任务
intellicli history          # 查看任务历史
intellicli review-config    # 配置复盘功能

# MCP 服务器管理 
intellicli mcp-config       # 配置 MCP 服务器
intellicli mcp-status       # 查看 MCP 服务器状态
intellicli mcp-tools        # 显示所有可用的 MCP 工具
intellicli mcp-refresh      # 刷新 MCP 工具列表

# 搜索功能
intellicli search-config    # 配置搜索引擎
intellicli search-status    # 搜索引擎状态
intellicli search-test      # 测试搜索功能
intellicli search-health    # 搜索引擎健康报告
```

### 智能路由示例

系统会根据任务类型自动选择最合适的模型：

```bash
# 图像任务 → 自动选择具备vision能力的模型
"帮我分析这张截图的内容"

# 代码任务 → 自动选择具备code能力的高优先级模型
"写一个Python函数计算斐波那契数列"

# 推理任务 → 自动选择具备reasoning能力的模型
"分析这个算法的时间复杂度"

# 文档任务 → 自动选择具备code+reasoning能力的模型
"生成这个项目的README文档"

# 搜索任务 → 自动选择搜索引擎
"搜索最新的Python开发资讯"
```

### 任务复盘示例 (v1.1 新增)

```bash
# 在交互式会话中
intellicli session
> 创建一个Python Web应用
> review     # 复盘刚刚的任务
> history    # 查看任务历史

# 命令行模式
intellicli task --review "创建一个Python Web应用"
intellicli review --goal "Python Web应用"
intellicli history
```

## 🏗️ 项目结构

```
IntelliCLI/
├── main.py                    # 主入口点
├── pyproject.toml            # 项目配置和依赖
├── requirements.txt          # Python 依赖文件
├── config.yaml.template      # 配置文件模板
├── config.yaml               # 运行时配置文件
├── install.sh               # Unix/Linux/macOS 安装脚本
├── install.bat              # Windows 安装脚本
├── docker-deploy.sh         # Docker 部署脚本
├── Dockerfile               # Docker 镜像配置
├── docker-compose.yml       # Docker 服务编排
├── Makefile                 # 快捷命令集
├── env.example              # 环境变量配置示例
├── README.md                # 项目说明文档 (中文)
├── README_EN.md             # 项目说明文档 (英文)
├── /scripts/                # 脚本工具
│   └── install.py           # Python 安装脚本
├── /docs/                   # 文档目录
│   ├── MCP_GUIDE.md         # MCP 使用指南 (中文)
│   └── MCP_GUIDE_EN.md      # MCP 使用指南 (英文)
├── /intellicli/             # 主包目录
│   ├── __init__.py          # 包初始化
│   ├── cli.py               # 命令行界面主入口
│   │
│   ├── /agent/              # 智能代理模块
│   │   ├── __init__.py      # 代理包初始化
│   │   ├── agent.py         # 智能代理主类 (v1.1 新增)
│   │   ├── planner.py       # 任务规划器
│   │   ├── executor.py      # 任务执行器
│   │   ├── model_router.py  # 智能模型路由器 (v1.1 增强)
│   │   └── task_reviewer.py # 任务复盘分析器 (v1.1 新增)
│   │
│   ├── /config/             # 配置管理模块
│   │   ├── __init__.py      # 配置包初始化
│   │   ├── model_config.py  # 模型配置管理 (v1.1 增强)
│   │   └── search_config.py # 搜索引擎配置管理
│   │
│   ├── /mcp/                # MCP (Model Context Protocol) 模块 (v1.1 新增)
│   │   ├── __init__.py      # MCP 包初始化
│   │   ├── mcp_client.py    # MCP 客户端实现
│   │   └── mcp_tool_manager.py # MCP 工具管理器
│   │
│   ├── /models/             # 模型客户端模块
│   │   ├── __init__.py      # 模型包初始化
│   │   ├── base_llm.py      # 模型基础接口定义
│   │   ├── ollama_client.py # Ollama 本地模型客户端
│   │   ├── gemini_client.py # Google Gemini 客户端
│   │   ├── openai_client.py # OpenAI 模型客户端
│   │   ├── claude_client.py # Anthropic Claude 客户端
│   │   ├── deepseek_client.py # DeepSeek 模型客户端
│   │   └── multimodal_manager.py # 多模态处理管理器
│   │
│   ├── /tools/              # 工具模块 (v1.1 全面AI增强)
│   │   ├── __init__.py      # 工具包初始化
│   │   ├── file_system.py   # 文件系统操作工具
│   │   ├── shell.py         # Shell 命令执行工具
│   │   ├── system_operations.py # 系统操作工具
│   │   ├── git_operations.py # Git 版本控制工具
│   │   ├── web_search.py    # 智能网络搜索工具
│   │   ├── python_analyzer.py # Python 代码分析工具
│   │   ├── code_analyzer.py # AI 代码分析工具 (v1.1 增强)
│   │   ├── document_manager.py # AI 文档管理工具 (v1.1 增强)
│   │   ├── image_processor.py # AI 图像处理工具 (v1.1 增强)
│   │   └── content_integrator.py # 智能内容整合工具
│   │
│   └── /ui/                 # 用户界面模块
│       ├── __init__.py      # UI 包初始化
│       └── display.py       # 现代化 CLI 界面
│
└── /intellicli.egg-info/    # 包安装信息 (自动生成)
```

### 📁 目录说明

**核心模块**：
- `/agent/` - 智能代理系统，负责任务规划、执行和复盘
- `/models/` - 多种 LLM 模型客户端，支持统一接口调用
- `/tools/` - 丰富的工具生态，支持文件、代码、图像、网络等操作
- `/config/` - 灵活的配置管理，支持模型、搜索、MCP 等配置
- `/mcp/` - MCP 协议实现，扩展外部工具和数据源
- `/ui/` - 现代化用户界面，提供友好的交互体验

**文档和配置**：
- `/docs/` - 详细的使用文档和指南
- `/scripts/` - 安装和部署脚本
- `config.yaml.template` - 配置文件模板
- `env.example` - 环境变量配置示例

**部署相关**：
- `Dockerfile` - 容器化部署配置
- `docker-compose.yml` - 多服务编排
- `Makefile` - 便捷的管理命令

## 🔧 高级功能

### 模型能力路由 

IntelliCLI 的智能路由系统完全基于用户配置，支持以下能力标签：

- **general**: 通用对话和文本处理
- **code**: 代码生成和编程任务
- **reasoning**: 复杂推理和分析任务
- **vision**: 图像和视觉相关任务

**路由策略优先级**：
1. **视觉任务** (优先级: 10) - 图像分析、截图处理
2. **代码生成** (优先级: 9) - 编程、代码分析
3. **文档生成** (优先级: 8) - 技术文档、API文档
4. **内容处理** (优先级: 7) - 内容整合、格式转换
5. **网络搜索** (优先级: 6) - 信息检索
6. **复杂推理** (优先级: 5) - 分析、决策支持
7. **系统操作** (优先级: 4) - 文件管理、系统命令
8. **一般任务** (优先级: 1) - 默认任务

### 任务复盘功能 

**自动分析**：
- 任务成功率统计
- 问题识别和分类
- 改进建议生成
- 补充计划创建

**配置选项**：
- `enabled`: 是否启用复盘功能
- `auto_review`: 是否自动复盘
- `review_threshold`: 复盘阈值 (0.0-1.0)
- `max_iterations`: 最大改进迭代次数

### AI增强工具系统 

**智能图像处理**：
- `analyze_image_style()` - AI风格分析
- `generate_image_tags()` - 智能标签生成
- `compare_images()` - 图像对比分析

**智能文档管理**：
- `generate_technical_documentation()` - 技术文档生成
- `analyze_project_architecture()` - 项目架构分析
- `generate_project_readme()` - AI README生成

**智能代码分析**：
- `analyze_code_with_ai()` - 多维度代码分析
- `generate_code_documentation()` - 代码文档生成
- `suggest_code_improvements()` - 改进建议
- `explain_code_logic()` - 代码逻辑解释

### MCP (Model Context Protocol) 集成 

**支持的 MCP 服务器**：
- **文件系统服务器** - 安全的文件操作工具
- **PostgreSQL 数据库** - 数据库查询和操作
- **Brave 搜索** - 网络搜索功能扩展
- **Google Maps** - 地图和位置服务
- **测试服务器** - 完整的 MCP 功能演示

**配置示例**：
```yaml
mcp_servers:
  servers:
    - name: filesystem
      command: ["npx", "@modelcontextprotocol/server-filesystem"]
      args: ["/Users/username/Projects"]
      enabled: true
    - name: postgres
      command: ["npx", "@modelcontextprotocol/server-postgres"]
      args: ["postgresql://postgres:password@localhost:5432/mydb"]
      enabled: true
```

**MCP 工具集成**：
- 在任务规划阶段自动发现 MCP 工具
- 与内置工具统一管理，无缝调用
- 支持工具名称冲突自动解决
- 实时健康检查和自动重连

**快速开始 MCP**：
```bash
# 1. 安装 MCP 服务器
npm install -g @modelcontextprotocol/server-everything

# 2. 配置 IntelliCLI
intellicli mcp-config

# 3. 查看状态和可用工具
intellicli mcp-status
intellicli mcp-tools

# 4. 在任务中使用
intellicli task "使用文件系统工具创建项目结构"
```

**详细文档**：
- 📖 [MCP 使用指南](docs/MCP_GUIDE.md) - 完整配置和使用说明

### 搜索引擎优先级

1. **Google** - 需要 API，质量最高
2. **Bing** - 需要 API，质量较高
3. **Yahoo** - 免费，可靠性高
4. **DuckDuckGo** - 免费，受限制
5. **Startpage** - 免费，隐私保护
6. **SearX** - 免费，不稳定

### 会话模式命令

**基础命令**：
- `help` - 显示帮助信息
- `models` - 查看可用模型
- `clear` - 清空会话记忆
- `exit` - 退出会话

**复盘命令** (v1.1 新增)：
- `review` - 复盘最近的任务
- `history` - 查看任务历史

## 🌟 新功能展示 

### 双层模型架构

```bash
# 主模型负责任务规划
intellicli task "创建一个Python Web应用"

# 执行过程中自动选择专业模型：
# 1. 规划阶段: 使用主模型 (claude_primary)
# 2. 代码生成: 使用代码模型 (deepseek_coder)
# 3. 文档生成: 使用推理模型 (claude_primary)
# 4. 图像处理: 使用视觉模型 (llava_vision)
```

### 任务复盘体验

```bash
# 执行任务时启用复盘
intellicli task --review "部署一个Docker应用"

# 任务完成后自动分析：
# ✅ 任务成功完成！
# 🔍 开始复盘分析...
# 📊 整体评分: 85/100
# 🎯 目标达成度: 90%
# ⚠️ 发现 2 个问题
# 💡 改进建议: 添加健康检查配置
```

### 配置驱动的模型选择

```bash
# 方式1: 使用配置向导
intellicli config-wizard

# 方式2: 直接编辑配置文件 
intellicli config-edit

# 配置文件中定义模型能力和优先级
models:
  providers:
    - alias: claude_primary
      capabilities: ["general", "code", "reasoning", "vision"]
      priority: 90
    - alias: deepseek_coder
      capabilities: ["code", "reasoning"]
      priority: 85

# 系统自动根据配置选择最合适的模型
# 代码任务 → deepseek_coder (专业+高优先级)
# 视觉任务 → claude_primary (唯一具备vision能力)
```

### MCP 工具扩展

```bash
# 配置文件系统 MCP 服务器
intellicli mcp-config
# 选择文件系统服务器，指定允许访问的目录

# 使用 MCP 工具执行文件操作
intellicli task "列出项目目录中的所有 Python 文件"

# 规划器自动选择合适的工具：
# 1. 规划阶段: 使用主模型分析任务
# 2. 执行阶段: 调用 MCP 文件系统工具
# 3. 结果处理: 使用主模型整理输出

# 查看 MCP 服务器状态
intellicli mcp-status
# ✅ filesystem: 已连接, 工具数量: 12
# ✅ postgres: 已连接, 工具数量: 8
```

## ❓ 常见问题

### 配置相关
- **Q**: 如何设置模型优先级？
- **A**: 在配置向导中设置1-100的优先级值，或编辑`config.yaml`中的`priority`字段

- **Q**: 模型路由不准确怎么办？
- **A**: 检查模型的`capabilities`配置，确保正确标注模型能力

- **Q**: 如何添加新的模型供应商？
- **A**: 运行 `intellicli config-wizard` 重新配置

- **Q**: 如何更改主模型？
- **A**: 编辑 `config.yaml` 中的 `primary` 字段或重新运行配置向导

- **Q**: 如何直接编辑配置文件？ 
- **A**: 运行 `intellicli config-edit` 会自动打开系统默认编辑器，支持VS Code、Cursor等

- **Q**: 配置文件格式错误怎么办？
- **A**: 使用 `intellicli config` 验证配置文件，注意YAML格式的缩进（使用空格，不要用Tab）

### 复盘功能相关 
- **Q**: 如何启用任务复盘？
- **A**: 运行 `intellicli review-config` 或在配置向导中启用

- **Q**: 复盘分析包含哪些内容？
- **A**: 成功率统计、问题识别、改进建议、补充计划等

- **Q**: 如何查看历史任务？
- **A**: 使用 `intellicli history` 命令或在会话中输入 `history`

### 搜索相关
- **Q**: 搜索功能不工作怎么办？
- **A**: 使用 `intellicli search-status` 检查状态，`intellicli search-test` 测试功能

- **Q**: 如何配置搜索引擎 API？
- **A**: 运行 `intellicli search-config` 或设置相应的环境变量

### MCP 相关 
- **Q**: 如何配置 MCP 服务器？
- **A**: 运行 `intellicli mcp-config` 启动配置向导，或查看 [MCP 使用指南](docs/MCP_GUIDE.md)

- **Q**: PostgreSQL 服务器连接失败怎么办？
- **A**: 检查数据库连接 URL 格式，确保使用 `postgresql://user:password@host:port/database` 格式

- **Q**: MCP 工具在规划中不显示？
- **A**: 使用 `intellicli mcp-status` 检查服务器状态，`intellicli mcp-refresh` 刷新工具列表

- **Q**: 如何安装 MCP 服务器？
- **A**: 使用 npm 全局安装，如 `npm install -g @modelcontextprotocol/server-filesystem`

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

### v1.1.0
- 🧠 **双层模型架构**: 主模型主导规划，专业模型执行任务
- 🔄 **任务复盘功能**: 智能分析执行结果，自动生成改进建议
- ⚙️ **配置驱动路由**: 完全基于用户配置的模型能力路由
- 🔧 **MCP 协议支持**: 完整的 Model Context Protocol 集成，扩展工具生态
- 🛠️ **AI增强工具**: 图像处理、文档管理、代码分析全面AI增强
- 📊 **优先级系统**: 支持模型优先级设置，精准控制选择策略
- 🎯 **智能路由优化**: 8种专业任务类型，动态模型选择
- 📝 **配置编辑器**: 新增 `config-edit` 命令，支持直接编辑配置文件
- 📈 **性能提升**: 优化路由算法，提高任务执行效率

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

---

*版本: 1.1.1*  
*最后更新: 2025年7月*

**相关链接:**
- [🇺🇸 English Version](README_EN.md)
- [📖 MCP 使用指南](docs/MCP_GUIDE.md)
- [📖 MCP User Guide](docs/MCP_GUIDE_EN.md)