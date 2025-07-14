# MCP (Model Context Protocol) User Guide

[🇺🇸 English Version](MCP_GUIDE_EN.md) | [🇨🇳 中文版本](MCP_GUIDE.md) | [📖 Main Documentation](../README_EN.md) | [📖 主要文档](../README.md)

## Overview

MCP (Model Context Protocol) is an open standard that allows AI assistants to securely connect with external data sources and tools. IntelliCLI fully supports MCP and can dynamically load and use tools provided by MCP servers.

## Features

### ✅ Core Features
- **Multi-server Support**: Connect to multiple MCP servers simultaneously
- **Dynamic Tool Loading**: Automatically discover and load MCP tools
- **Smart Planning Integration**: Use MCP tools during planning phase
- **Tool Name Conflict Resolution**: Automatically handle same-name tool conflicts
- **Health Checks**: Automatically monitor server status with auto-restart support
- **Parallel Connection**: Efficient parallel server connection management

### 🔧 Configuration Features
- **Interactive Configuration Wizard**: User-friendly configuration interface
- **Preset Servers**: Built-in common MCP server configurations
- **Custom Servers**: Support for adding arbitrary MCP servers
- **Independent Configuration Management**: Separate MCP functionality configuration

## Quick Start

### 1. Configure MCP Servers

```bash
# Configure MCP servers
intellicli mcp-config
```

### 2. View MCP Status

```bash
# View MCP server status
intellicli mcp-status
```

### 3. Refresh MCP Tools

```bash
# Refresh MCP tool list
intellicli mcp-refresh
```

### 4. Use MCP Tools

```bash
# MCP tools are automatically used when executing tasks
intellicli task "Use filesystem tools to create a new file"
```

## Preset MCP Servers

### 1. Filesystem Server
- **Name**: filesystem
- **Function**: Provides file system operation tools
- **Command**: `npx @modelcontextprotocol/server-filesystem`
- **Parameters**: Directory paths allowed for access
- **Example**: `["$HOME/Documents"]`

### 2. Brave Search Server
- **Name**: brave_search
- **Function**: Provides Brave search API access
- **Command**: `npx @modelcontextprotocol/server-brave-search`
- **Environment Variables**: `BRAVE_API_KEY`

### 3. PostgreSQL Database Server
- **Name**: postgres
- **Function**: Provides PostgreSQL database operation tools
- **Command**: `npx @modelcontextprotocol/server-postgres`
- **Parameters**: Database connection URL
- **Example**: `postgresql://postgres:password@localhost:5432/mydb`

### 4. Google Maps Server
- **Name**: google_maps
- **Function**: Provides Google Maps API access tools
- **Command**: `npx @modelcontextprotocol/server-google-maps`
- **Environment Variables**: `GOOGLE_MAPS_API_KEY`

### 5. Everything Test Server
- **Name**: everything
- **Function**: Used for testing all MCP protocol features
- **Command**: `npx @modelcontextprotocol/server-everything`
- **Features**: Includes example tools, resources, and prompts, suitable for learning and testing

## Configuration Examples

### Filesystem Server Configuration
```yaml
mcp_servers:
  servers:
    - name: filesystem
      description: "File system operations"
      command: ["npx", "@modelcontextprotocol/server-filesystem"]
      args: ["/Users/username/Documents", "/Users/username/Projects"]
      env: {}
      enabled: true
```

### Brave Search Server Configuration
```yaml
mcp_servers:
  servers:
    - name: brave_search
      description: "Web search functionality"
      command: ["npx", "@modelcontextprotocol/server-brave-search"]
      args: []
      env:
        BRAVE_API_KEY: "your_brave_api_key_here"
      enabled: true
```

### PostgreSQL Database Server Configuration
```yaml
mcp_servers:
  servers:
    - name: postgres
      description: "Database operations"
      command: ["npx", "@modelcontextprotocol/server-postgres"]
      args: ["postgresql://postgres:password@localhost:5432/mydb"]
      env: {}
      enabled: true
```

### Everything Test Server Configuration (Recommended for Learning)
```yaml
mcp_servers:
  servers:
    - name: everything
      description: "MCP functionality testing"
      command: ["npx", "@modelcontextprotocol/server-everything"]
      args: []
      env: {}
      enabled: true
```

## Usage Examples

### Using Filesystem Tools

```bash
# Create file and write content
intellicli task "Use filesystem tools to create a file named hello.txt in the Documents directory with content 'Hello World'"

# Read file content
intellicli task "Read the content of hello.txt file in the Documents directory"

# List directory contents
intellicli task "List all files in the Documents directory"
```

### Using Search Tools

```bash
# Search for information
intellicli task "Use Brave search to find Python programming best practices"

# Search and organize information
intellicli task "Search for machine learning tutorials and organize them in markdown format"
```

### Using Database Tools

```bash
# Query database
intellicli task "Query all user information from the SQLite database"

# Create table
intellicli task "Create a table named products in the SQLite database"
```

## Tool Naming Rules

When multiple MCP servers provide tools with the same name, the system automatically adds server name prefixes:

- Original tool name: `read_file`
- After conflict resolution: `filesystem_read_file`

## Troubleshooting

### 1. Server Connection Failed

```bash
# Check MCP status
intellicli mcp-status

# Common causes:
# - Server command doesn't exist (e.g., npx not installed)
# - Environment variables not set
# - Incorrect parameter paths
# - Network connection issues
```

### 2. Tools Not Available

```bash
# Refresh tool list
intellicli mcp-refresh

# Check server status
intellicli mcp-status
```

### 3. Permission Issues

```bash
# Ensure filesystem server has access to specified directories
# Ensure API keys have sufficient permissions
```

## Configuration File Structure

MCP configuration is stored in the `config.yaml` file:

```yaml
mcp_servers:
  servers:
    - name: mcp_filesystem
      description: Filesystem server
      command: ["npx", "@modelcontextprotocol/server-filesystem"]
      args: ["/Users/username/Documents"]
      env: {}
      enabled: true
      auto_restart: true
    - name: mcp_brave_search
      description: Brave search server
      command: ["npx", "@modelcontextprotocol/server-brave-search"]
      args: []
      env:
        BRAVE_API_KEY: "your_api_key_here"
      enabled: true
      auto_restart: true
```

## Best Practices

### 1. Server Configuration
- Use descriptive server names
- Enable auto-restart functionality
- Regularly check server status

### 2. Security Considerations
- Only authorize necessary directory access for filesystem servers
- Properly secure API keys
- Regularly update MCP servers

### 3. Performance Optimization
- Avoid configuring too many servers
- Disable unused servers
- Regularly clean up unused tools

## Advanced Features

### 1. Health Checks
- Automatic server status monitoring
- Auto-restart on connection loss
- Real-time status reporting

### 2. Tool Management
- Dynamic tool discovery
- Tool name conflict resolution
- Tool statistics and analysis

### 3. Concurrent Processing
- Parallel server connections
- Thread-safe tool calls
- Connection pool management

## Developer Guide

### Creating Custom MCP Servers

```python
# Example: Simple MCP server
import json
import sys

def handle_request(request):
    if request["method"] == "tools/list":
        return {
            "tools": [
                {
                    "name": "custom_tool",
                    "description": "Custom tool",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "input": {"type": "string"}
                        }
                    }
                }
            ]
        }
    # ... handle other methods

# Main loop
while True:
    line = sys.stdin.readline()
    if not line:
        break
    
    request = json.loads(line)
    response = handle_request(request)
    
    print(json.dumps(response))
    sys.stdout.flush()
```

### Integration with IntelliCLI

1. Save the server script as `my_server.py`
2. Use `intellicli mcp-config` to add custom server
3. Startup command: `python my_server.py`

## Frequently Asked Questions

### Q: What to do if MCP server fails to start?
A: Check if the command is correct, environment variables are set, and parameter paths exist.

### Q: How to disable a specific MCP server?
A: Re-run `intellicli mcp-config` and disable the corresponding server in configuration.

### Q: What's the difference between MCP tools and built-in tools?
A: MCP tools come from external servers with richer functionality; built-in tools are basic tools that come with IntelliCLI.

### Q: Can I use multiple search servers simultaneously?
A: Yes, the system automatically handles tool name conflicts.

## More Resources

- [MCP Official Documentation](https://modelcontextprotocol.io/)
- [MCP Server List](https://github.com/modelcontextprotocol/servers)

---

*Last Updated: July 2025*

**Links:**
- [🇺🇸 English Version](MCP_GUIDE_EN.md)
- [🇨🇳 中文版本](MCP_GUIDE.md)
- [📖 Main Documentation](../README_EN.md)
- [📖 主要文档](../README.md) 