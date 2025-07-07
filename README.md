# IntelliCLI

**IntelliCLI** 是一个智能命令行助手，旨在通过结合大型语言模型 (LLM) 的强大功能和动态任务规划能力，简化复杂的软件工程任务。它支持灵活的模型后端，允许您无缝切换本地 Ollama 模型和远程 API，并能为复杂任务生成并执行逐步计划。

## 核心特性

- **统一模型配置系统:** 首次运行时自动启动交互式配置向导，引导用户完成模型设置。支持多种模型供应商（Ollama、Google Gemini、OpenAI），并可为每个模型指定能力标签。

- **智能模型路由:** 根据用户指令的性质和配置的模型能力，IntelliCLI 能够智能地将任务路由到最合适的模型。例如，图像任务自动使用视觉模型，代码任务使用代码模型。

- **动态任务规划:** 对于复杂任务，IntelliCLI 会利用最合适的模型生成详细的、可执行的步骤列表。它会逐步执行这些任务，并实时更新进度，确保复杂工作流的透明和高效。

- **可插拔工具系统:** 通过定义简单的 Python 函数，可以轻松扩展 IntelliCLI 的功能，使其能够执行文件系统操作、运行 shell 命令等。

- **持续会话模式:** 允许用户在一个持续的交互会话中与代理进行对话，迭代地完成任务，并支持错误纠正和重试。

## 快速开始

### 方法一：全局安装（推荐）

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

### 方法二：开发模式安装

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

### 方法三：本地运行（传统方式）

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
1. **选择模型供应商**：Ollama、Google Gemini、OpenAI
2. **配置模型信息**：别名、模型名称、服务器地址等
3. **选择模型能力**：通用、代码、推理、视觉等
4. **设置主模型**：选择默认使用的模型

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

### 4. 配置示例

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

tools:
  file_system:
    enabled: true
  shell:
    enabled: true
  system_operations:
    enabled: true
  python_analyzer:
    enabled: true

logging:
  level: INFO
```

## 使用方法

### 基本命令

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
4. **一般任务**: 其他所有任务

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
│   │   └── model_router.py    # 智能模型路由器
│   ├── /config                # 配置管理模块
│   │   └── model_config.py    # 模型配置管理器
│   ├── /models                # 模型客户端
│   │   ├── base_llm.py        # 基础LLM接口
│   │   ├── ollama_client.py   # Ollama客户端
│   │   └── gemini_client.py   # Gemini客户端
│   ├── /tools                 # 工具模块
│   │   ├── file_system.py     # 文件系统工具
│   │   ├── shell.py           # Shell命令工具
│   │   ├── python_analyzer.py # Python代码分析
│   │   └── system_operations.py # 系统操作工具
│   └── /ui                    # 用户界面
│       └── display.py         # 现代化CLI界面
└── /docs                      # 文档目录
    └── 配置系统说明.md        # 配置系统详细说明
```

## 高级功能

### 环境变量配置

```bash
# Gemini API 密钥
export GEMINI_API_KEY="your_api_key_here"

# OpenAI API 密钥
export OPENAI_API_KEY="your_api_key_here"
```

### 自定义工具

您可以通过扩展 `tools` 目录来添加自定义工具。每个工具都是一个简单的 Python 函数，可以被智能代理调用。

### 会话记忆

系统会记住：
- 创建的文件
- 访问的目录
- 最近的操作
- 项目上下文

这使得连续的任务能够基于之前的操作结果进行优化。

## 卸载

如果您需要卸载 IntelliCLI：

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

### Q: 如何重置所有配置？

A: 运行 `intellicli config-reset`（全局安装）或 `python main.py config-reset`（传统方式），或者删除 `config.yaml` 文件后重新运行程序。

### Q: 全局安装和传统方式有什么区别？

A: 全局安装后可以在任意位置运行 `intellicli` 命令，就像使用 `git` 或 `npm` 一样。传统方式需要在项目目录中使用 `python main.py` 运行。

### Q: 如何在不同项目中使用不同的配置？

A: 每个项目目录都可以有自己的 `config.yaml` 文件。IntelliCLI 会优先使用当前目录的配置文件。

### Q: 支持哪些操作系统？

A: 支持 Windows、macOS 和 Linux。提供了对应的安装脚本。

## 联系我们

如有问题或建议，请联系：
- 📧 邮箱：lovemaojiu@gmail.com
- 🐛 问题报告：[GitHub Issues](https://github.com/MR-MaoJiu/IntelliCLI/issues)

## 许可证

本项目采用 MIT 许可证。详情请参阅 LICENSE 文件。