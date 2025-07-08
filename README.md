# IntelliCLI

**IntelliCLI** 是一个智能命令行助手，旨在通过结合大型语言模型 (LLM) 的强大功能和动态任务规划能力，简化复杂的软件工程任务。它支持灵活的模型后端，允许您无缝切换本地 Ollama 模型和远程 API，并能为复杂任务生成并执行逐步计划。

## 核心特性

- **🐳 Docker化部署:** 提供完整的Docker解决方案，包含Dockerfile、docker-compose.yml和管理脚本。支持一键部署、数据持久化、服务编排和健康监控，无需配置Python环境即可快速使用。

- **统一模型配置系统:** 首次运行时自动启动交互式配置向导，引导用户完成模型设置。支持多种模型供应商（Ollama、Google Gemini、OpenAI、Claude、DeepSeek），并可为每个模型指定能力标签。

- **智能模型路由:** 根据用户指令的性质和配置的模型能力，IntelliCLI 能够智能地将任务路由到最合适的模型。例如，图像任务自动使用视觉模型，代码任务使用代码模型。

- **动态任务规划:** 对于复杂任务，IntelliCLI 会利用最合适的模型生成详细的、可执行的步骤列表。它会逐步执行这些任务，并实时更新进度，确保复杂工作流的透明和高效。

- **智能网络搜索:** 集成多种搜索引擎（Google、Bing、Yahoo、DuckDuckGo、Startpage、SearX），支持智能引擎切换和故障转移，确保搜索功能高可用性。

- **多模态处理:** 支持文本和图像的统一处理，自动识别多模态输入并选择合适的模型进行处理。

- **可插拔工具系统:** 通过定义简单的 Python 函数，可以轻松扩展 IntelliCLI 的功能，使其能够执行文件系统操作、运行 shell 命令、网络搜索等。

- **持续会话模式:** 允许用户在一个持续的交互会话中与代理进行对话，迭代地完成任务，并支持错误纠正和重试。

## 🐳 Docker部署优势

### 为什么选择Docker部署？

- **🚀 零配置启动**: 无需安装Python环境和依赖包
- **📦 一键部署**: 使用 `make quick-start` 即可完成所有配置
- **🔄 服务编排**: 自动管理IntelliCLI和Ollama服务
- **💾 数据持久化**: 配置和数据自动保存，重启不丢失
- **🔧 环境隔离**: 独立的容器环境，不影响主机系统
- **🏥 健康监控**: 自动监控服务状态和健康检查
- **🛠️ 便捷管理**: 提供完整的管理工具和脚本
- **🌐 跨平台**: 支持Windows、macOS和Linux

### 适用场景

- **新手用户**: 无需了解Python环境配置
- **生产部署**: 稳定可靠的容器化部署
- **团队协作**: 统一的开发和部署环境
- **快速体验**: 5分钟即可开始使用

## 快速开始

### 方法一：Docker部署（推荐）

**最简单的部署方式，无需配置Python环境**

#### 1. 克隆仓库
```bash
git clone https://github.com/MR-MaoJiu/IntelliCLI.git
cd IntelliCLI
```

#### 2. 5分钟快速部署
```bash
# 初始化环境
make init

# 编辑API密钥
nano .env

# 一键启动
make quick-start

# 进入交互式会话
make session
```

#### 3. 其他Docker命令
```bash
# 查看所有可用命令
make help

# 查看服务状态
make status

# 查看日志
make logs

# 停止服务
make stop

# 清理资源
make cleanup
```

> 📚 **详细文档**: 查看 [Docker快速开始指南](DOCKER_QUICKSTART.md) 和 [Docker部署文档](docker/README.md)

### 方法二：全局安装

适合需要在本地环境中使用的用户：

#### 1. 克隆仓库
```bash
git clone https://github.com/MR-MaoJiu/IntelliCLI.git
cd IntelliCLI
```

#### 2. 快速安装
```bash
# Unix/Linux/macOS
./install.sh

# Windows
install.bat

# 或者使用 Python 安装脚本
python scripts/install.py install
```

#### 3. 开始使用
```bash
# 在任意位置运行
intellicli session

# 或使用简短别名
icli session
```

### 方法三：开发模式安装

适合开发者，支持代码修改后立即生效：

```bash
# 克隆仓库
git clone https://github.com/MR-MaoJiu/IntelliCLI.git
cd IntelliCLI

# 开发模式安装
pip install -e .[dev]

# 开始使用
intellicli session
```

### 方法四：本地运行（传统方式）

```bash
# 克隆仓库
git clone https://github.com/MR-MaoJiu/IntelliCLI.git
cd IntelliCLI

# 安装依赖
pip install -r requirements.txt

# 运行
python main.py session
```

### 首次运行

无论使用哪种方式，首次运行时都会自动启动**配置向导**：

配置向导将引导您完成以下步骤：
1. **选择模型供应商**：Ollama、Google Gemini、OpenAI、Claude、DeepSeek
2. **配置模型信息**：别名、模型名称、服务器地址等
3. **选择模型能力**：通用、代码、推理、视觉等
4. **设置主模型**：选择默认使用的模型
5. **配置搜索引擎**：设置网络搜索功能（可选）

### 3. 模型供应商配置

#### Ollama 模型
- **本地服务器**: `http://localhost:11434`
- **远程服务器**: 输入您的 Ollama 服务器地址
- **支持模型**: gemma3:27b, llava:34b, llama3:8b 等

#### Google Gemini
- **API 密钥**: 设置环境变量 `GEMINI_API_KEY`
- **支持模型**: gemini-1.5-pro-latest, gemini-1.5-flash 等

#### OpenAI
- **API 密钥**: 设置环境变量 `OPENAI_API_KEY`
- **支持模型**: gpt-4, gpt-3.5-turbo, gpt-4-vision-preview 等

#### Claude (Anthropic)
- **API 密钥**: 设置环境变量 `ANTHROPIC_API_KEY`
- **支持模型**: claude-3-sonnet-20240229, claude-3-haiku-20240307 等

#### DeepSeek
- **API 密钥**: 设置环境变量 `DEEPSEEK_API_KEY`
- **支持模型**: deepseek-chat, deepseek-coder 等

### 4. 搜索引擎配置

IntelliCLI 支持多种搜索引擎，提供智能切换和故障转移功能：

#### 免费搜索引擎
- **Yahoo**: 免费，实际可用性较好
- **DuckDuckGo**: 免费，但受反爬虫机制限制
- **Startpage**: 免费，隐私保护，但受访问限制
- **SearX**: 免费，使用公开实例，连接不稳定

#### 商业搜索引擎
- **Google**: 需要 Google Custom Search API 密钥和搜索引擎 ID
- **Bing**: 需要 Bing Search API 密钥

#### 搜索引擎配置命令
```bash
# 配置搜索引擎
intellicli search-config

# 查看搜索引擎状态
intellicli search-status

# 测试搜索功能
intellicli search-test

# 查看搜索引擎健康状态
intellicli search-health
```

### 5. 配置示例

完成配置向导后，会生成类似以下的配置文件：

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
    
    - alias: gemini_pro
      provider: gemini
      model_name: "gemini-1.5-pro-latest"
      capabilities: ["general", "code", "reasoning", "vision"]
    
    - alias: claude_sonnet
      provider: claude
      model_name: "claude-3-sonnet-20240229"
      capabilities: ["general", "code", "reasoning", "vision"]

search_engines:
  engines:
    google:
      api_key: "your_google_api_key"
      search_engine_id: "your_search_engine_id"
    bing:
      api_key: "your_bing_api_key"

tools:
  file_system:
    enabled: true
  shell:
    enabled: true
  system_operations:
    enabled: true
  python_analyzer:
    enabled: true
  web_search:
    enabled: true

logging:
  level: INFO
```

## 使用方法

### Docker部署命令

如果您使用Docker部署，推荐使用以下命令：

```bash
# 启动交互式会话
make session

# 查看服务状态
make status

# 查看日志
make logs

# 重启服务
make restart

# 停止服务
make stop

# 配置向导
make config

# 配置复盘功能
make review-config

# 查看所有可用命令
make help
```

### 全局安装命令

如果您使用全局安装：

```bash
# 启动交互式会话
intellicli session

# 单次对话
intellicli chat "你好，帮我创建一个简单的网页"

# 显示可用模型
intellicli models

# 显示当前配置
intellicli config

# 重新运行配置向导
intellicli config-wizard

# 重置配置
intellicli config-reset
```

### 搜索功能命令

```bash
# 配置搜索引擎
intellicli search-config

# 查看搜索引擎状态
intellicli search-status

# 测试搜索功能
intellicli search-test

# 查看搜索引擎健康状态
intellicli search-health

# 测试故障转移功能
intellicli search-test --test-failover
```

### 传统方式（项目目录内）

如果您使用传统方式在项目目录内运行：

```bash
# 启动交互式会话
python main.py session

# 单次对话
python main.py chat "你好，帮我创建一个简单的网页"

# 显示可用模型
python main.py models

# 显示当前配置
python main.py config

# 重新运行配置向导
python main.py config-wizard

# 重置配置
python main.py config-reset

# 搜索功能
python main.py search-config
python main.py search-status
python main.py search-test
python main.py search-health
```

### 智能模型路由示例

系统会根据任务类型自动选择最合适的模型：

```bash
# 图像任务 → 自动使用视觉模型
"帮我分析这张截图的内容"

# 代码任务 → 自动使用代码模型
"写一个Python函数来计算斐波那契数列"

# 推理任务 → 自动使用推理模型
"分析这个算法的时间复杂度"

# 搜索任务 → 自动使用搜索引擎
"搜索最新的Python开发资讯"

# 一般任务 → 使用通用模型
"今天天气怎么样？"
```

### 会话模式功能

在会话模式中，您可以使用以下命令：

- `help` - 显示帮助信息
- `models` - 查看可用模型
- `clear` - 清空会话记忆
- `exit` - 退出会话

## 模型能力说明

### 能力标签

- **general**: 通用对话和文本处理
- **code**: 代码生成和编程任务
- **reasoning**: 复杂推理和分析任务
- **vision**: 图像和视觉相关任务

### 路由规则

系统使用以下规则进行模型路由：

1. **视觉任务**: 包含"图像"、"截图"、"识别"等关键词
2. **代码任务**: 包含"代码"、"编程"、"函数"等关键词
3. **推理任务**: 包含"分析"、"推理"、"解决"等关键词
4. **搜索任务**: 包含"搜索"、"查找"、"最新"等关键词
5. **一般任务**: 其他所有任务

## 搜索引擎功能

### 智能搜索引擎切换

IntelliCLI 提供了强大的搜索引擎管理功能：

#### 特性
- **多引擎支持**: 支持 Google、Bing、Yahoo、DuckDuckGo、Startpage、SearX
- **智能切换**: 引擎失效时自动切换到其他可用引擎
- **健康监控**: 实时监控引擎状态，自动禁用连续失败的引擎
- **优先级管理**: 基于可靠性的动态优先级排序
- **故障转移**: 完全自动化的故障转移机制

#### 使用示例
```bash
# 在会话中直接搜索
"搜索 Python 最新版本信息"
"查找 React 18 新特性"
"帮我搜索机器学习教程"

# 系统会自动：
# 1. 选择最优的搜索引擎
# 2. 失败时自动切换到其他引擎
# 3. 返回整合的搜索结果
```

#### 搜索引擎优先级
1. **Yahoo** - 免费，可靠性最高
2. **Google** - 需要API，质量最高
3. **Bing** - 需要API，质量较高
4. **DuckDuckGo** - 免费，受限制
5. **Startpage** - 免费，隐私保护
6. **SearX** - 免费，不稳定

### 搜索配置管理

#### 配置 Google 搜索
```bash
# 设置环境变量
export GOOGLE_SEARCH_API_KEY="your_api_key"
export GOOGLE_SEARCH_ENGINE_ID="your_engine_id"

# 或在配置向导中设置
intellicli search-config
```

#### 配置 Bing 搜索
```bash
# 设置环境变量
export BING_SEARCH_API_KEY="your_api_key"

# 或在配置向导中设置
intellicli search-config
```

## 管理配置

### 查看配置

```bash
# 全局安装后
intellicli config

# 传统方式
python main.py config
```

### 修改配置

```bash
# 全局安装后
intellicli config-wizard

# 传统方式
python main.py config-wizard

# 或者直接编辑配置文件
vim config.yaml
```

### 重置配置

```bash
# 全局安装后
intellicli config-reset

# 传统方式
python main.py config-reset
```

## 项目结构

```
IntelliCLI/
├── main.py                      # 向后兼容的主入口点
├── pyproject.toml              # Python 项目配置
├── requirements.txt            # Python 依赖
├── config.yaml                 # 配置文件（自动生成）
├── config.yaml.template        # 配置模板
├── install.sh                  # Unix/Linux/macOS 安装脚本
├── install.bat                 # Windows 安装脚本
├── /scripts                    # 脚本目录
│   └── install.py             # Python 安装脚本
├── /intellicli                 # 主包目录
│   ├── __init__.py            # 包初始化
│   ├── cli.py                 # 命令行界面
│   ├── /agent                 # 智能代理模块
│   │   ├── planner.py         # 任务规划器
│   │   ├── executor.py        # 任务执行器
│   │   ├── model_router.py    # 智能模型路由器
│   │   ├── shell_planner.py   # Shell任务规划器
│   │   └── shell_error_handler.py # Shell错误处理器
│   ├── /config                # 配置管理模块
│   │   ├── model_config.py    # 模型配置管理器
│   │   └── search_config.py   # 搜索引擎配置管理器
│   ├── /models                # 模型客户端
│   │   ├── base_llm.py        # 基础LLM接口
│   │   ├── ollama_client.py   # Ollama客户端
│   │   ├── gemini_client.py   # Gemini客户端
│   │   ├── openai_client.py   # OpenAI客户端
│   │   ├── claude_client.py   # Claude客户端
│   │   ├── deepseek_client.py # DeepSeek客户端
│   │   └── multimodal_manager.py # 多模态管理器
│   ├── /tools                 # 工具模块
│   │   ├── file_system.py     # 文件系统工具
│   │   ├── shell.py           # Shell命令工具
│   │   ├── python_analyzer.py # Python代码分析
│   │   ├── system_operations.py # 系统操作工具
│   │   ├── web_search.py      # 网络搜索工具
│   │   ├── shell_validator.py # Shell命令验证
│   │   └── image_processor.py # 图像处理工具
│   └── /ui                    # 用户界面
│       └── display.py         # 现代化CLI界面
├── /docs                      # 文档目录
│   ├── 配置系统说明.md        # 配置系统详细说明
│   └── 快速安装指南.md        # 快速安装指南
├── /docker                    # Docker部署相关
│   └── README.md              # Docker详细部署文档
├── Dockerfile                 # Docker镜像构建文件
├── docker-compose.yml         # Docker Compose服务编排
├── .dockerignore              # Docker构建忽略文件
├── docker-deploy.sh           # Docker部署脚本
├── Makefile                   # Make命令定义
├── env.example                # 环境变量配置示例
├── DOCKER_QUICKSTART.md       # Docker快速开始指南
├── DOCKER_SUMMARY.md          # Docker功能总结
├── config/                    # 配置文件目录（Docker持久化）
├── data/                      # 数据目录（Docker持久化）
└── workspace/                 # 工作目录（Docker可选挂载）
```

## 高级功能

### 环境变量配置

```bash
# 模型 API 密钥
export GEMINI_API_KEY="your_api_key_here"
export OPENAI_API_KEY="your_api_key_here"
export ANTHROPIC_API_KEY="your_api_key_here"
export DEEPSEEK_API_KEY="your_api_key_here"

# 搜索引擎 API 密钥
export GOOGLE_SEARCH_API_KEY="your_google_api_key"
export GOOGLE_SEARCH_ENGINE_ID="your_search_engine_id"
export BING_SEARCH_API_KEY="your_bing_api_key"
```

### 自定义工具

您可以通过扩展 `tools` 目录来添加自定义工具。每个工具都是一个简单的 Python 函数，可以被智能代理调用。

### 多模态处理

系统支持文本和图像的统一处理：

```bash
# 自动识别图像任务
"分析这张图片的内容"
"识别截图中的文字"
"这张图片显示了什么？"

# 系统会自动：
# 1. 检测到图像处理需求
# 2. 选择支持视觉的模型
# 3. 处理图像并返回结果
```

### 会话记忆

系统会记住：
- 创建的文件
- 访问的目录
- 最近的操作
- 项目上下文
- 搜索历史

这使得连续的任务能够基于之前的操作结果进行优化。

### 搜索引擎健康监控

系统提供完善的搜索引擎健康监控：

- **实时状态监控**: 跟踪每个引擎的成功/失败状态
- **自动黑名单**: 连续失败3次的引擎会被暂时禁用5分钟
- **动态优先级**: 根据历史表现动态调整引擎优先级
- **故障转移**: 失败时自动切换到其他可用引擎

## 卸载

### Docker部署卸载

如果您使用Docker部署：

```bash
# 停止并删除容器
make stop

# 清理所有Docker资源
make cleanup

# 删除项目目录（可选）
cd ..
rm -rf IntelliCLI
```

### 本地安装卸载

如果您使用本地安装：

```bash
# 使用 pip 卸载
pip uninstall intellicli

# 或者使用安装脚本
python scripts/install.py uninstall

# 删除配置文件（可选）
rm -f config.yaml
```

## 常见问题

### Q: 如何添加新的模型供应商？

A: 运行 `intellicli config-wizard`（全局安装）或 `python main.py config-wizard`（传统方式）并选择添加新模型，或者手动编辑 `config.yaml` 文件。

### Q: 如何更改主模型？

A: 运行 `intellicli config-wizard`（全局安装）或 `python main.py config-wizard`（传统方式）重新配置，或者直接编辑配置文件中的 `primary` 字段。

### Q: 模型路由不准确怎么办？

A: 检查模型的能力配置是否正确，确保为每个模型设置了合适的能力标签。

### Q: 搜索功能不工作怎么办？

A: 使用 `intellicli search-status` 检查搜索引擎配置状态，使用 `intellicli search-test` 测试搜索功能，使用 `intellicli search-health` 查看引擎健康状态。

### Q: 如何配置搜索引擎API？

A: 运行 `intellicli search-config` 进入搜索引擎配置向导，或者设置相应的环境变量。

### Q: 搜索引擎经常失败怎么办？

A: 系统会自动处理引擎失败并切换到其他可用引擎。您可以通过 `intellicli search-health` 查看引擎状态，连续失败的引擎会被暂时禁用。

### Q: 如何重置所有配置？

A: 运行 `intellicli config-reset`（全局安装）或 `python main.py config-reset`（传统方式），或者删除 `config.yaml` 文件后重新运行程序。

### Q: 全局安装和传统方式有什么区别？

A: 全局安装后可以在任意位置运行 `intellicli` 命令，就像使用 `git` 或 `npm` 一样。传统方式需要在项目目录中使用 `python main.py` 运行。

### Q: 如何在不同项目中使用不同的配置？

A: 每个项目目录都可以有自己的 `config.yaml` 文件。IntelliCLI 会优先使用当前目录的配置文件。

### Q: 支持哪些操作系统？

A: 支持 Windows、macOS 和 Linux。提供了对应的安装脚本。

### Q: 支持哪些图像格式？

A: 支持常见的图像格式：PNG、JPG、JPEG、GIF、BMP、TIFF、WebP。

### Q: 如何提高搜索结果的准确性？

A: 使用具体的关键词，配置高质量的搜索引擎（如Google、Bing），系统会自动选择最合适的引擎并整合结果。

### Q: Docker部署和本地安装有什么区别？

A: Docker部署无需配置Python环境，提供完整的容器化解决方案，包括数据持久化和服务编排。本地安装直接在系统中运行，更适合开发和定制。

### Q: 如何在Docker中配置API密钥？

A: 编辑项目根目录的 `.env` 文件，填入您的API密钥，然后重启Docker服务：`make restart`。

### Q: Docker容器启动失败怎么办？

A: 使用 `make logs` 查看详细错误信息，使用 `make status` 检查服务状态。常见问题包括端口占用、API密钥配置错误等。

### Q: 如何在Docker中持久化数据？

A: 配置文件存储在 `./config` 目录，历史数据存储在 `./data` 目录，工作文件存储在 `./workspace` 目录。这些目录会自动挂载到容器中。

### Q: 如何更新Docker版本？

A: 使用 `make stop` 停止服务，`git pull` 拉取最新代码，`make build` 重新构建镜像，`make start` 启动服务。

## 更新日志

### v2.1.0 (最新)
- 🐳 **新增完整Docker支持**: 提供Dockerfile、docker-compose.yml和管理脚本
- 📦 **一键部署**: 支持 `make quick-start` 快速部署
- 🔄 **服务编排**: 集成Ollama本地LLM服务
- 💾 **数据持久化**: 配置、数据和工作空间的持久化存储
- 🛠️ **管理工具**: 提供Makefile和部署脚本，简化Docker管理
- 📚 **完整文档**: 包含快速开始指南和详细部署文档
- 🔧 **环境变量管理**: 安全的API密钥配置方式
- 🏥 **健康监控**: 自动监控服务状态和健康检查

### v2.0.0
- ✨ 新增智能搜索引擎系统，支持多引擎智能切换
- 🔄 实现搜索引擎故障转移和健康监控
- 🎯 优化模型路由，支持更多模型供应商
- 🖼️ 增强多模态处理能力
- 🛠️ 新增搜索配置管理命令
- 🔧 改进错误处理和用户体验

### v1.0.0
- 🎉 首个稳定版本发布
- 🤖 智能模型路由系统
- 📝 动态任务规划
- 🔧 可插拔工具系统
- 💬 持续会话模式

## 联系我们

如有问题或建议，请联系：
- 📧 邮箱：lovemaojiu@gmail.com
- 🐛 问题报告：[GitHub Issues](https://github.com/MR-MaoJiu/IntelliCLI/issues)

## 许可证

本项目采用 MIT 许可证。详情请参阅 LICENSE 文件。