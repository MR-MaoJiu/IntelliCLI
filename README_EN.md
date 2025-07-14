# IntelliCLI

[🇨🇳 中文版本](README.md) | [📖 MCP User Guide](docs/MCP_GUIDE_EN.md) | [📖 MCP 使用指南](docs/MCP_GUIDE.md)

**IntelliCLI** is an intelligent command-line assistant that combines Large Language Models (LLMs) with dynamic task planning capabilities to simplify complex software engineering tasks. It supports multiple model backends with intelligent routing and can generate executable step-by-step plans for complex tasks.

## 🚀 Core Features

### 🧠 Intelligent Continuation Planning
- **Smart Error Recovery**: After errors occur, the system doesn't completely re-plan but intelligently continues from the failure point
- **Preserve Successful Steps**: Automatically maintains the state and output of completed steps, avoiding redundant work
- **Context-aware Planning**: The planner understands current progress and generates targeted subsequent plans
- **Cumulative Progress Display**: Real-time display of overall completion progress, including cross-iteration cumulative statistics
- **Failure Point Analysis**: Intelligently analyzes failure causes and generates fixes or alternative solutions

### 🧠 Intelligent Dual-layer Model Architecture
- **Primary Model-driven Planning**: Uses primary model for consistent task decomposition and holistic thinking
- **Specialized Model Execution**: Dynamically selects the most appropriate specialized model for execution based on task type
- **Configuration-driven Routing**: Completely based on user-configured model capabilities for intelligent routing
- **Priority System**: Supports model priority settings for precise model selection control

### 🔄 Task Review Functionality
- **Intelligent Analysis**: Automatically analyzes task execution results, identifies problems and improvement opportunities
- **Supplementary Planning**: Generates supplementary execution plans for incomplete tasks
- **Historical Records**: Complete task execution history and review records
- **Iterative Improvement**: Supports multiple rounds of improvement and optimization

### 🛠️ AI-Enhanced Tool System
- **Smart Image Processing**: AI-driven image analysis, style recognition, content extraction
- **Smart Document Management**: AI-generated technical documentation, project architecture analysis
- **Smart Code Analysis**: Multi-dimensional code analysis, quality assessment, security checks
- **Dynamic Model Injection**: Tools can dynamically use different specialized models as needed

### 🖥️ Intelligent Shell Execution System
- **Transparent Command Execution**: Command execution is completely like direct terminal operation, maintaining native experience
- **Smart Mode Switching**: Automatically detects command types and dynamically selects optimal execution mode
- **Learning Adaptation Mechanism**: System automatically learns command characteristics and optimizes subsequent execution strategies
- **Automatic Problem Detection**: Real-time monitoring of output formats, automatically switches execution methods when anomalies are detected
- **Interactive Command Support**: Perfect support for complex interactive scaffolding tools like Vue CLI, React CLI

### 🐳 Dockerized Deployment
- **One-click Deployment**: Complete all configurations using `make quick-start`
- **Zero-configuration Startup**: No need to install Python environment and dependency packages
- **Data Persistence**: Configuration and data are automatically saved, no loss on restart
- **Service Orchestration**: Automatically manages IntelliCLI and Ollama services
- **Health Monitoring**: Real-time monitoring of service status and health checks

### 🤖 Intelligent Model System
- **Unified Configuration**: Automatically starts interactive configuration wizard on first run
- **Smart Routing**: Automatically selects the most appropriate model based on task type
- **Multi-vendor Support**: Ollama, Google Gemini, OpenAI, Claude, DeepSeek
- **Capability Tags**: Specify general, code, reasoning, vision capabilities for each model
- **Priority Management**: Supports model priority settings from 1-100

### 🔍 Intelligent Search System
- **Multi-engine Support**: Google, Bing, Yahoo, DuckDuckGo, Startpage, SearX
- **Automatic Switching**: Automatically switches to other available engines when engines fail
- **Health Monitoring**: Real-time monitoring of engine status, automatically disables failed engines
- **Failover**: Fully automated failover mechanism

### 🔧 MCP (Model Context Protocol) Support (New in v1.1)
- **Protocol Standard**: Supports open MCP standard, connecting external tools and data sources
- **Multi-server Management**: Simultaneously connect to multiple MCP servers with unified tool management
- **Preset Servers**: Built-in common server configurations for file system, database, search, etc.
- **Dynamic Tool Loading**: Automatically discover and load MCP tools, seamlessly integrate into planning system
- **Health Checks**: Automatically monitor server status, support disconnection and reconnection
- **Conflict Resolution**: Intelligently handle same-name tool conflicts, ensure system stability

### 🛠️ Powerful Features
- **Dynamic Task Planning**: Decompose complex tasks into executable steps
- **Multimodal Processing**: Unified processing of text and images
- **Pluggable Tools**: Extend functionality through simple Python functions
- **Persistent Sessions**: Support context memory and error correction

## 🚀 Quick Start

### Method 1: Docker Deployment (Recommended)

**The simplest deployment method, no need to configure Python environment**

```bash
# 1. Clone repository
git clone https://github.com/MR-MaoJiu/IntelliCLI.git
cd IntelliCLI

# 2. Initialize environment
make init

# 3. Edit API keys (optional)
nano .env

# 4. One-click startup
make quick-start

# 5. Enter interactive session
make session
```

### Method 2: Global Installation

```bash
# 1. Clone repository
git clone https://github.com/MR-MaoJiu/IntelliCLI.git
cd IntelliCLI

# 2. Run installation script
./install.sh  # Unix/Linux/macOS
# or
install.bat   # Windows

# 3. Start using
intellicli session
```

### Method 3: Development Mode

```bash
# 1. Clone repository
git clone https://github.com/MR-MaoJiu/IntelliCLI.git
cd IntelliCLI

# 2. Install in development mode
pip install -e .[dev]

# 3. Start using
intellicli session
```

### Method 4: Local Run

```bash
# 1. Clone repository
git clone https://github.com/MR-MaoJiu/IntelliCLI.git
cd IntelliCLI

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run
python main.py session
```

## ⚙️ Configuration

### First Run

Regardless of the method used, the first run will automatically start the **configuration wizard** to guide you through:

1. **Select model providers**: Ollama, Google Gemini, OpenAI, Claude, DeepSeek
2. **Configure model information**: Alias, model name, server address, etc.
3. **Set model capabilities**: General, code, reasoning, vision tags
4. **Set model priority**: Priority range 1-100, controls model selection
5. **Select primary model**: Default model to use
6. **Configure search engines**: Web search functionality (optional)
7. **Configure review functionality**: Task review and automatic improvement (optional)

### Environment Variable Configuration

Configure API keys in `.env` file or environment variables:

```bash
# Model API keys
GEMINI_API_KEY=your_gemini_key
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_claude_key
DEEPSEEK_API_KEY=your_deepseek_key

# Search engine API keys
GOOGLE_SEARCH_API_KEY=your_google_key
GOOGLE_SEARCH_ENGINE_ID=your_engine_id
BING_SEARCH_API_KEY=your_bing_key
```

### Configuration Example

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

# Task review functionality configuration
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

## 📖 Usage

### Docker Deployment Commands

```bash
make session        # Start interactive session
make status         # View service status
make logs           # View logs
make restart        # Restart service
make stop           # Stop service
make config         # Configuration wizard
make help           # View all commands
```

### Global Installation Commands

```bash
# Basic commands
intellicli session          # Start interactive session
intellicli chat "question"  # Single conversation
intellicli task "task"      # Execute complex task
intellicli task --review "task"  # Execute task with review enabled

# Model management
intellicli models           # Display available models
intellicli config           # Display current configuration
intellicli config-wizard    # Reconfigure
intellicli config-edit      # Edit configuration file directly
intellicli config-reset     # Reset configuration

# Review functionality
intellicli review           # Review recent tasks
intellicli review --goal "task goal"  # Review specific task
intellicli history          # View task history
intellicli review-config    # Configure review functionality

# MCP server management
intellicli mcp-config       # Configure MCP servers
intellicli mcp-status       # View MCP server status
intellicli mcp-tools        # Display all available MCP tools
intellicli mcp-refresh      # Refresh MCP tool list

# Search functionality
intellicli search-config    # Configure search engines
intellicli search-status    # Search engine status
intellicli search-test      # Test search functionality
intellicli search-health    # Search engine health report
```

### Smart Routing Examples

The system automatically selects the most appropriate model based on task type:

```bash
# Image tasks → Automatically select models with vision capability
"Help me analyze the content of this screenshot"

# Code tasks → Automatically select high-priority models with code capability
"Write a Python function to calculate Fibonacci sequence"

# Reasoning tasks → Automatically select models with reasoning capability
"Analyze the time complexity of this algorithm"

# Documentation tasks → Automatically select models with code+reasoning capability
"Generate README documentation for this project"

# Search tasks → Automatically select search engines
"Search for the latest Python development news"
```

### Task Review Examples (New in v1.1)

```bash
# In interactive session
intellicli session
> Create a Python web application
> review     # Review the task just completed
> history    # View task history

# Command line mode
intellicli task --review "Create a Python web application"
intellicli review --goal "Python web application"
intellicli history
```

## 🏗️ Project Structure

```
IntelliCLI/
├── main.py                    # Main entry point
├── pyproject.toml            # Project configuration and dependencies
├── requirements.txt          # Python dependencies
├── config.yaml.template      # Configuration file template
├── config.yaml               # Runtime configuration file
├── install.sh               # Unix/Linux/macOS installation script
├── install.bat              # Windows installation script
├── docker-deploy.sh         # Docker deployment script
├── Dockerfile               # Docker image configuration
├── docker-compose.yml       # Docker service orchestration
├── Makefile                 # Shortcut command set
├── env.example              # Environment variable configuration example
├── README.md                # Project documentation (Chinese)
├── README_EN.md             # Project documentation (English)
├── /scripts/                # Script tools
│   └── install.py           # Python installation script
├── /docs/                   # Documentation directory
│   ├── MCP_GUIDE.md         # MCP User Guide (Chinese)
│   └── MCP_GUIDE_EN.md      # MCP User Guide (English)
├── /intellicli/             # Main package directory
│   ├── __init__.py          # Package initialization
│   ├── cli.py               # Command line interface main entry
│   │
│   ├── /agent/              # Intelligent agent module
│   │   ├── __init__.py      # Agent package initialization
│   │   ├── agent.py         # Intelligent agent main class (New in v1.1)
│   │   ├── planner.py       # Task planner
│   │   ├── executor.py      # Task executor
│   │   ├── model_router.py  # Intelligent model router (Enhanced in v1.1)
│   │   └── task_reviewer.py # Task review analyzer (New in v1.1)
│   │
│   ├── /config/             # Configuration management module
│   │   ├── __init__.py      # Configuration package initialization
│   │   ├── model_config.py  # Model configuration management (Enhanced in v1.1)
│   │   └── search_config.py # Search engine configuration management
│   │
│   ├── /mcp/                # MCP (Model Context Protocol) module (New in v1.1)
│   │   ├── __init__.py      # MCP package initialization
│   │   ├── mcp_client.py    # MCP client implementation
│   │   └── mcp_tool_manager.py # MCP tool manager
│   │
│   ├── /models/             # Model client module
│   │   ├── __init__.py      # Model package initialization
│   │   ├── base_llm.py      # Model base interface definition
│   │   ├── ollama_client.py # Ollama local model client
│   │   ├── gemini_client.py # Google Gemini client
│   │   ├── openai_client.py # OpenAI model client
│   │   ├── claude_client.py # Anthropic Claude client
│   │   ├── deepseek_client.py # DeepSeek model client
│   │   └── multimodal_manager.py # Multimodal processing manager
│   │
│   ├── /tools/              # Tool module (Fully AI-enhanced in v1.1)
│   │   ├── __init__.py      # Tool package initialization
│   │   ├── file_system.py   # File system operation tools
│   │   ├── shell.py         # Shell command execution tools
│   │   ├── system_operations.py # System operation tools
│   │   ├── git_operations.py # Git version control tools
│   │   ├── web_search.py    # Intelligent web search tools
│   │   ├── python_analyzer.py # Python code analysis tools
│   │   ├── code_analyzer.py # AI code analysis tools (Enhanced in v1.1)
│   │   ├── document_manager.py # AI document management tools (Enhanced in v1.1)
│   │   ├── image_processor.py # AI image processing tools (Enhanced in v1.1)
│   │   └── content_integrator.py # Smart content integration tools
│   │
│   └── /ui/                 # User interface module
│       ├── __init__.py      # UI package initialization
│       └── display.py       # Modern CLI interface
│
└── /intellicli.egg-info/    # Package installation info (auto-generated)
```

### 📁 Directory Description

**Core Modules**:
- `/agent/` - Intelligent agent system, responsible for task planning, execution, and review
- `/models/` - Multiple LLM model clients, supporting unified interface calls
- `/tools/` - Rich tool ecosystem, supporting file, code, image, network operations
- `/config/` - Flexible configuration management, supporting model, search, MCP configurations
- `/mcp/` - MCP protocol implementation, extending external tools and data sources
- `/ui/` - Modern user interface, providing friendly interaction experience

**Documentation and Configuration**:
- `/docs/` - Detailed usage documentation and guides
- `/scripts/` - Installation and deployment scripts
- `config.yaml.template` - Configuration file template
- `env.example` - Environment variable configuration example

**Deployment Related**:
- `Dockerfile` - Containerized deployment configuration
- `docker-compose.yml` - Multi-service orchestration
- `Makefile` - Convenient management commands

## 🔧 Advanced Features

### Model Capability Routing

IntelliCLI's intelligent routing system is completely based on user configuration, supporting the following capability tags:

- **general**: General conversation and text processing
- **code**: Code generation and programming tasks
- **reasoning**: Complex reasoning and analysis tasks
- **vision**: Image and visual-related tasks

**Routing Strategy Priority**:
1. **Visual Tasks** (Priority: 10) - Image analysis, screenshot processing
2. **Code Generation** (Priority: 9) - Programming, code analysis
3. **Documentation Generation** (Priority: 8) - Technical documentation, API documentation
4. **Content Processing** (Priority: 7) - Content integration, format conversion
5. **Web Search** (Priority: 6) - Information retrieval
6. **Complex Reasoning** (Priority: 5) - Analysis, decision support
7. **System Operations** (Priority: 4) - File management, system commands
8. **General Tasks** (Priority: 1) - Default tasks

### Task Review Functionality

**Automatic Analysis**:
- Task success rate statistics
- Problem identification and classification
- Improvement suggestion generation
- Supplementary plan creation

**Configuration Options**:
- `enabled`: Whether to enable review functionality
- `auto_review`: Whether to automatically review
- `review_threshold`: Review threshold (0.0-1.0)
- `max_iterations`: Maximum improvement iterations

### AI-Enhanced Tool System

**Smart Image Processing**:
- `analyze_image_style()` - AI style analysis
- `generate_image_tags()` - Smart tag generation
- `compare_images()` - Image comparison analysis

**Smart Document Management**:
- `generate_technical_documentation()` - Technical documentation generation
- `analyze_project_architecture()` - Project architecture analysis
- `generate_project_readme()` - AI README generation

**Smart Code Analysis**:
- `analyze_code_with_ai()` - Multi-dimensional code analysis
- `generate_code_documentation()` - Code documentation generation
- `suggest_code_improvements()` - Improvement suggestions
- `explain_code_logic()` - Code logic explanation

### MCP (Model Context Protocol) Integration

**Supported MCP Servers**:
- **File System Server** - Secure file operation tools
- **PostgreSQL Database** - Database query and operations
- **Brave Search** - Web search functionality extension
- **Google Maps** - Maps and location services
- **Test Server** - Complete MCP functionality demonstration

**Configuration Example**:
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

**MCP Tool Integration**:
- Automatically discover MCP tools during task planning phase
- Unified management with built-in tools, seamless invocation
- Support automatic resolution of tool name conflicts
- Real-time health checks and automatic reconnection

**Quick Start with MCP**:
```bash
# 1. Install MCP servers
npm install -g @modelcontextprotocol/server-everything

# 2. Configure IntelliCLI
intellicli mcp-config

# 3. View status and available tools
intellicli mcp-status
intellicli mcp-tools

# 4. Use in tasks
intellicli task "Use filesystem tools to create project structure"
```

**Detailed Documentation**:
- 📖 [MCP User Guide](docs/MCP_GUIDE_EN.md) - Complete configuration and usage instructions

### Search Engine Priority

1. **Google** - Requires API, highest quality
2. **Bing** - Requires API, high quality
3. **Yahoo** - Free, high reliability
4. **DuckDuckGo** - Free, limited
5. **Startpage** - Free, privacy protection
6. **SearX** - Free, unstable

### Session Mode Commands

**Basic Commands**:
- `help` - Display help information
- `models` - View available models
- `clear` - Clear session memory
- `exit` - Exit session

**Review Commands** (New in v1.1):
- `review` - Review recent tasks
- `history` - View task history

## 🌟 New Feature Showcase

### Dual-layer Model Architecture

```bash
# Primary model handles task planning
intellicli task "Create a Python web application"

# Execution process automatically selects specialized models:
# 1. Planning phase: Use primary model (claude_primary)
# 2. Code generation: Use code model (deepseek_coder)
# 3. Documentation generation: Use reasoning model (claude_primary)
# 4. Image processing: Use vision model (llava_vision)
```

### Task Review Experience

```bash
# Execute task with review enabled
intellicli task --review "Deploy a Docker application"

# Automatic analysis after task completion:
# ✅ Task completed successfully!
# 🔍 Starting review analysis...
# 📊 Overall score: 85/100
# 🎯 Goal achievement: 90%
# ⚠️ Found 2 issues
# 💡 Improvement suggestion: Add health check configuration
```

### Configuration-driven Model Selection

```bash
# Method 1: Use configuration wizard
intellicli config-wizard

# Method 2: Edit configuration file directly
intellicli config-edit

# Define model capabilities and priorities in configuration file
models:
  providers:
    - alias: claude_primary
      capabilities: ["general", "code", "reasoning", "vision"]
      priority: 90
    - alias: deepseek_coder
      capabilities: ["code", "reasoning"]
      priority: 85

# System automatically selects most appropriate model based on configuration
# Code tasks → deepseek_coder (specialized + high priority)
# Vision tasks → claude_primary (only model with vision capability)
```

### MCP Tool Extension

```bash
# Configure filesystem MCP server
intellicli mcp-config
# Select filesystem server, specify allowed access directories

# Use MCP tools for file operations
intellicli task "List all Python files in the project directory"

# Planner automatically selects appropriate tools:
# 1. Planning phase: Use primary model to analyze task
# 2. Execution phase: Call MCP filesystem tools
# 3. Result processing: Use primary model to organize output

# View MCP server status
intellicli mcp-status
# ✅ filesystem: Connected, tool count: 12
# ✅ postgres: Connected, tool count: 8
```

## ❓ FAQ

### Configuration Related
- **Q**: How to set model priority?
- **A**: Set priority values 1-100 in configuration wizard, or edit the `priority` field in `config.yaml`

- **Q**: What to do if model routing is inaccurate?
- **A**: Check the model's `capabilities` configuration, ensure proper model capability annotation

- **Q**: How to add new model providers?
- **A**: Run `intellicli config-wizard` to reconfigure

- **Q**: How to change the primary model?
- **A**: Edit the `primary` field in `config.yaml` or re-run the configuration wizard

- **Q**: How to edit configuration file directly?
- **A**: Run `intellicli config-edit` which automatically opens the system default editor, supports VS Code, Cursor, etc.

- **Q**: What to do with configuration file format errors?
- **A**: Use `intellicli config` to validate configuration file, note YAML format indentation (use spaces, not tabs)

### Review Functionality Related
- **Q**: How to enable task review?
- **A**: Run `intellicli review-config` or enable in configuration wizard

- **Q**: What does review analysis include?
- **A**: Success rate statistics, problem identification, improvement suggestions, supplementary plans, etc.

- **Q**: How to view historical tasks?
- **A**: Use `intellicli history` command or type `history` in session

### Search Related
- **Q**: What to do if search functionality doesn't work?
- **A**: Use `intellicli search-status` to check status, `intellicli search-test` to test functionality

- **Q**: How to configure search engine API?
- **A**: Run `intellicli search-config` or set corresponding environment variables

### MCP Related
- **Q**: How to configure MCP servers?
- **A**: Run `intellicli mcp-config` to start configuration wizard, or see [MCP User Guide](docs/MCP_GUIDE_EN.md)

- **Q**: What to do if PostgreSQL server connection fails?
- **A**: Check database connection URL format, ensure using `postgresql://user:password@host:port/database` format

- **Q**: Why don't MCP tools show in planning?
- **A**: Use `intellicli mcp-status` to check server status, `intellicli mcp-refresh` to refresh tool list

- **Q**: How to install MCP servers?
- **A**: Use npm global installation, such as `npm install -g @modelcontextprotocol/server-filesystem`

### Docker Related
- **Q**: How to configure API keys in Docker?
- **A**: Edit `.env` file, then run `make restart`

- **Q**: What to do if Docker container fails to start?
- **A**: Use `make logs` to view error information, `make status` to check status

### Other Issues
- **Q**: Which operating systems are supported?
- **A**: Supports Windows, macOS, and Linux

- **Q**: Which image formats are supported?
- **A**: Supports PNG, JPG, JPEG, GIF, BMP, TIFF, WebP

## 🗑️ Uninstall

### Docker Deployment Uninstall
```bash
make stop     # Stop services
make cleanup  # Clean up resources
```

### Local Installation Uninstall
```bash
pip uninstall intellicli
# or
python scripts/install.py uninstall
```

## 📝 Changelog

### v1.1.0
- 🧠 **Dual-layer Model Architecture**: Primary model drives planning, specialized models execute tasks
- 🔄 **Task Review Functionality**: Intelligent analysis of execution results, automatic improvement suggestions
- ⚙️ **Configuration-driven Routing**: Completely based on user-configured model capability routing
- 🔧 **MCP Protocol Support**: Complete Model Context Protocol integration, expanding tool ecosystem
- 🛠️ **AI-Enhanced Tools**: Comprehensive AI enhancement for image processing, document management, code analysis
- 📊 **Priority System**: Support model priority settings, precise selection strategy control
- 🎯 **Smart Routing Optimization**: 8 professional task types, dynamic model selection
- 📝 **Configuration Editor**: New `config-edit` command, supports direct configuration file editing
- 📈 **Performance Improvements**: Optimized routing algorithms, improved task execution efficiency

### v1.0.0
- 🎉 First stable release
- 🤖 Intelligent model routing system
- 📝 Dynamic task planning
- 🔧 Pluggable tool system

## 📞 Contact Us

- 📧 Email: lovemaojiu@gmail.com
- 🐛 Issue Reports: [GitHub Issues](https://github.com/MR-MaoJiu/IntelliCLI/issues)

## 📄 License

This project is licensed under the MIT License. See the LICENSE file for details.

---

*Version: 1.1.1*  
*Last Updated: July 2025*

**Links:**
- [🇨🇳 中文版本](README.md)
- [📖 MCP User Guide](docs/MCP_GUIDE_EN.md)
- [📖 MCP 使用指南](docs/MCP_GUIDE.md) 