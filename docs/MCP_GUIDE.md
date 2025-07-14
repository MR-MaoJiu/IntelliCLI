# MCP (Model Context Protocol) 使用指南

[🇨🇳 中文版本](MCP_GUIDE.md) | [🇺🇸 English Version](MCP_GUIDE_EN.md) | [📖 主要文档](../README.md) | [📖 Main Documentation](../README_EN.md)

## 概述

MCP (Model Context Protocol) 是一个开放标准，允许AI助手与外部数据源和工具安全地连接。IntelliCLI 完全支持 MCP，能够动态加载和使用 MCP 服务器提供的工具。

## 功能特性

### ✅ 核心功能
- **多服务器支持**：同时连接多个 MCP 服务器
- **动态工具加载**：自动发现和加载 MCP 工具
- **智能规划集成**：规划阶段可以使用 MCP 工具
- **工具名称冲突解决**：自动处理同名工具冲突
- **健康检查**：自动监控服务器状态，支持自动重启
- **并行连接**：高效的并行服务器连接管理

### 🔧 配置功能
- **交互式配置向导**：用户友好的配置界面
- **预设服务器**：内置常用 MCP 服务器配置
- **自定义服务器**：支持添加任意 MCP 服务器
- **独立配置管理**：可单独配置 MCP 功能

## 快速开始

### 1. 配置 MCP 服务器

```bash
# 配置 MCP 服务器
intellicli mcp-config
```

### 2. 查看 MCP 状态

```bash
# 查看 MCP 服务器状态
intellicli mcp-status
```

### 3. 刷新 MCP 工具

```bash
# 刷新 MCP 工具列表
intellicli mcp-refresh
```

### 4. 使用 MCP 工具

```bash
# 执行任务时会自动使用 MCP 工具
intellicli task "使用文件系统工具创建一个新文件"
```

## 预设 MCP 服务器

### 1. 文件系统服务器
- **名称**: filesystem
- **功能**: 提供文件系统操作工具
- **命令**: `npx @modelcontextprotocol/server-filesystem`
- **参数**: 允许访问的目录路径
- **示例**: `["$HOME/Documents"]`

### 2. Brave 搜索服务器
- **名称**: brave_search
- **功能**: 提供Brave搜索API访问
- **命令**: `npx @modelcontextprotocol/server-brave-search`
- **环境变量**: `BRAVE_API_KEY`

### 3. PostgreSQL 数据库服务器
- **名称**: postgres
- **功能**: 提供PostgreSQL数据库操作工具
- **命令**: `npx @modelcontextprotocol/server-postgres`
- **参数**: 数据库连接URL
- **示例**: `postgresql://postgres:password@localhost:5432/mydb`

### 4. Google Maps 服务器
- **名称**: google_maps
- **功能**: 提供Google Maps API访问工具
- **命令**: `npx @modelcontextprotocol/server-google-maps`
- **环境变量**: `GOOGLE_MAPS_API_KEY`

### 5. 完整功能测试服务器
- **名称**: everything
- **功能**: 用于测试MCP协议所有功能
- **命令**: `npx @modelcontextprotocol/server-everything`
- **特点**: 包含示例工具、资源和提示，适合学习和测试

## 配置示例

### 文件系统服务器配置
```yaml
mcp_servers:
  servers:
    - name: filesystem
      description: "文件系统操作"
      command: ["npx", "@modelcontextprotocol/server-filesystem"]
      args: ["/Users/username/Documents", "/Users/username/Projects"]
      env: {}
      enabled: true
```

### Brave 搜索服务器配置
```yaml
mcp_servers:
  servers:
    - name: brave_search
      description: "网络搜索功能"
      command: ["npx", "@modelcontextprotocol/server-brave-search"]
      args: []
      env:
        BRAVE_API_KEY: "your_brave_api_key_here"
      enabled: true
```

### PostgreSQL 数据库服务器配置
```yaml
mcp_servers:
  servers:
    - name: postgres
      description: "数据库操作"
      command: ["npx", "@modelcontextprotocol/server-postgres"]
      args: ["postgresql://postgres:password@localhost:5432/mydb"]
      env: {}
      enabled: true
```

### 完整功能测试服务器配置（推荐用于学习）
```yaml
mcp_servers:
  servers:
    - name: everything
      description: "MCP功能测试"
      command: ["npx", "@modelcontextprotocol/server-everything"]
      args: []
      env: {}
      enabled: true
```

## 使用示例

### 使用文件系统工具

```bash
# 创建文件并写入内容
intellicli task "使用文件系统工具在Documents目录下创建一个名为hello.txt的文件，内容为Hello World"

# 读取文件内容
intellicli task "读取Documents目录下的hello.txt文件内容"

# 列出目录内容
intellicli task "列出Documents目录下的所有文件"
```

### 使用搜索工具

```bash
# 搜索信息
intellicli task "使用Brave搜索Python编程最佳实践"

# 搜索并整理信息
intellicli task "搜索机器学习入门教程，并整理成markdown格式"
```

### 使用数据库工具

```bash
# 查询数据库
intellicli task "从SQLite数据库中查询所有用户信息"

# 创建表
intellicli task "在SQLite数据库中创建一个名为products的表"
```

## 工具命名规则

当多个 MCP 服务器提供同名工具时，系统会自动添加服务器名称前缀：

- 原始工具名：`read_file`
- 冲突解决后：`filesystem_read_file`

## 故障排除

### 1. 服务器连接失败

```bash
# 检查 MCP 状态
intellicli mcp-status

# 常见原因：
# - 服务器命令不存在（如 npx 未安装）
# - 环境变量未设置
# - 参数路径不正确
# - 网络连接问题
```

### 2. 工具不可用

```bash
# 刷新工具列表
intellicli mcp-refresh

# 检查服务器状态
intellicli mcp-status
```

### 3. 权限问题

```bash
# 确保文件系统服务器有访问指定目录的权限
# 确保 API 密钥有足够的权限
```

## 配置文件结构

MCP 配置存储在 `config.yaml` 文件中：

```yaml
mcp_servers:
  servers:
    - name: mcp_filesystem
      description: 文件系统服务器
      command: ["npx", "@modelcontextprotocol/server-filesystem"]
      args: ["/Users/username/Documents"]
      env: {}
      enabled: true
      auto_restart: true
    - name: mcp_brave_search
      description: Brave搜索服务器
      command: ["npx", "@modelcontextprotocol/server-brave-search"]
      args: []
      env:
        BRAVE_API_KEY: "your_api_key_here"
      enabled: true
      auto_restart: true
```

## 最佳实践

### 1. 服务器配置
- 使用描述性的服务器名称
- 启用自动重启功能
- 定期检查服务器状态

### 2. 安全考虑
- 文件系统服务器只授权必要的目录访问
- 妥善保管 API 密钥
- 定期更新 MCP 服务器

### 3. 性能优化
- 避免配置过多的服务器
- 禁用不常用的服务器
- 定期清理无用的工具

## 高级功能

### 1. 健康检查
- 自动监控服务器状态
- 连接断开时自动重启
- 实时状态报告

### 2. 工具管理
- 动态工具发现
- 工具名称冲突解决
- 工具统计和分析

### 3. 并发处理
- 并行服务器连接
- 线程安全的工具调用
- 连接池管理

## 开发者指南

### 创建自定义 MCP 服务器

```python
# 示例：简单的 MCP 服务器
import json
import sys

def handle_request(request):
    if request["method"] == "tools/list":
        return {
            "tools": [
                {
                    "name": "custom_tool",
                    "description": "自定义工具",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "input": {"type": "string"}
                        }
                    }
                }
            ]
        }
    # ... 其他方法处理

# 主循环
while True:
    line = sys.stdin.readline()
    if not line:
        break
    
    request = json.loads(line)
    response = handle_request(request)
    
    print(json.dumps(response))
    sys.stdout.flush()
```

### 集成到 IntelliCLI

1. 将服务器脚本保存为 `my_server.py`
2. 使用 `intellicli mcp-config` 添加自定义服务器
3. 启动命令：`python my_server.py`

## 常见问题

### Q: MCP 服务器启动失败怎么办？
A: 检查命令是否正确，环境变量是否设置，参数路径是否存在。

### Q: 如何禁用某个 MCP 服务器？
A: 重新运行 `intellicli mcp-config`，在配置中将对应服务器设置为禁用。

### Q: MCP 工具和内置工具有什么区别？
A: MCP 工具来自外部服务器，功能更丰富；内置工具是 IntelliCLI 自带的基础工具。

### Q: 可以同时使用多个搜索服务器吗？
A: 可以，系统会自动处理工具名称冲突。

## 更多资源

- [MCP 官方文档](https://modelcontextprotocol.io/)
- [MCP 服务器列表](https://github.com/modelcontextprotocol/servers)

---

*最后更新：2025年7月*

**相关链接:**
- [🇨🇳 中文版本](MCP_GUIDE.md)
- [🇺🇸 English Version](MCP_GUIDE_EN.md)
- [📖 主要文档](../README.md)
- [📖 Main Documentation](../README_EN.md) 