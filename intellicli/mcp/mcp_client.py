"""
MCP (Model Context Protocol) 客户端
提供与 MCP 服务器的连接和通信功能
"""

import json
import subprocess
import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import time

logger = logging.getLogger(__name__)

@dataclass
class MCPServerConfig:
    """MCP 服务器配置"""
    name: str
    command: List[str]
    args: List[str] = None
    env: Dict[str, str] = None
    timeout: int = 30
    auto_restart: bool = True
    description: str = ""
    enabled: bool = True

@dataclass
class MCPTool:
    """MCP 工具信息"""
    name: str
    description: str
    parameters: Dict[str, Any]
    server_name: str
    input_schema: Dict[str, Any] = None

class MCPClient:
    """MCP 客户端"""
    
    def __init__(self, server_config: MCPServerConfig):
        self.server_config = server_config
        self.process = None
        self.is_connected = False
        self.tools = {}
        self.resources = {}
        self.last_heartbeat = None
        self.request_id = 0
        
    def get_next_request_id(self) -> int:
        """获取下一个请求ID"""
        self.request_id += 1
        return self.request_id
    
    def start_server(self) -> bool:
        """启动 MCP 服务器"""
        try:
            if self.process and self.process.poll() is None:
                logger.info(f"MCP 服务器 {self.server_config.name} 已在运行")
                return True
            
            # 构建完整命令
            cmd = self.server_config.command.copy()
            if self.server_config.args:
                cmd.extend(self.server_config.args)
            
            # 设置环境变量
            import os
            env = os.environ.copy()
            if self.server_config.env:
                env.update(self.server_config.env)
            
            logger.info(f"启动 MCP 服务器: {' '.join(cmd)}")
            
            # 启动进程
            self.process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
                bufsize=0
            )
            
            # 等待服务器启动并检查状态
            max_wait_time = 10  # 最多等待10秒
            check_interval = 0.5  # 每0.5秒检查一次
            waited_time = 0
            
            while waited_time < max_wait_time:
                time.sleep(check_interval)
                waited_time += check_interval
                
                # 检查进程是否还在运行
                if self.process.poll() is not None:
                    stderr_output = ""
                    if self.process.stderr:
                        stderr_output = self.process.stderr.read()
                    logger.error(f"MCP 服务器 {self.server_config.name} 启动失败: {stderr_output}")
                    return False
                
                # 如果已经等待了足够的时间，认为启动成功
                if waited_time >= 2.0:
                    break
            
            logger.info(f"MCP 服务器 {self.server_config.name} 启动成功")
            return True
            
        except FileNotFoundError as e:
            logger.error(f"MCP 服务器命令未找到 {self.server_config.name}: {e}")
            logger.info(f"请确保已安装相应的 MCP 服务器: {' '.join(self.server_config.command)}")
            return False
        except Exception as e:
            logger.error(f"启动 MCP 服务器 {self.server_config.name} 时出错: {e}")
            return False
    
    def stop_server(self):
        """停止 MCP 服务器"""
        try:
            if self.process:
                self.process.terminate()
                # 等待进程结束
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                    self.process.wait()
                
                logger.info(f"MCP 服务器 {self.server_config.name} 已停止")
                self.process = None
                self.is_connected = False
                
        except Exception as e:
            logger.error(f"停止 MCP 服务器 {self.server_config.name} 时出错: {e}")
    
    def send_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """发送请求到 MCP 服务器"""
        if not self.process or self.process.poll() is not None:
            raise RuntimeError(f"MCP 服务器 {self.server_config.name} 未运行")
        
        request_id = self.get_next_request_id()
        request = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params or {}
        }
        
        try:
            # 发送请求
            request_json = json.dumps(request) + "\n"
            self.process.stdin.write(request_json)
            self.process.stdin.flush()
            
            # 等待并读取响应，添加超时机制
            import select
            import sys
            
            # 设置超时时间（秒）
            timeout = self.server_config.timeout
            
            if sys.platform != 'win32':
                # Unix/Linux 系统使用 select
                ready, _, _ = select.select([self.process.stdout], [], [], timeout)
                if not ready:
                    raise RuntimeError(f"等待 MCP 服务器响应超时 ({timeout}秒)")
                
                response_line = self.process.stdout.readline().strip()
            else:
                # Windows 系统直接读取，依赖进程超时
                response_line = self.process.stdout.readline().strip()
            
            if not response_line:
                # 检查进程是否还在运行
                if self.process.poll() is not None:
                    stderr_output = self.process.stderr.read() if self.process.stderr else "无错误信息"
                    raise RuntimeError(f"MCP 服务器进程已终止，错误信息: {stderr_output}")
                else:
                    raise RuntimeError("未收到响应")
            
            try:
                response = json.loads(response_line)
            except json.JSONDecodeError as e:
                logger.error(f"MCP 服务器返回无效 JSON: {response_line}")
                raise RuntimeError(f"MCP 服务器返回无效 JSON: {e}")
            
            # 检查错误
            if "error" in response:
                error = response["error"]
                raise RuntimeError(f"MCP 错误: {error.get('message', 'Unknown error')}")
            
            return response.get("result", {})
            
        except Exception as e:
            logger.error(f"发送请求到 MCP 服务器 {self.server_config.name} 时出错: {e}")
            raise
    
    def initialize(self) -> bool:
        """初始化 MCP 连接"""
        try:
            # 发送初始化请求
            init_params = {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                    "resources": {}
                },
                "clientInfo": {
                    "name": "IntelliCLI",
                    "version": "1.1.0"
                }
            }
            
            result = self.send_request("initialize", init_params)
            
            # 发送 initialized 通知
            self.send_notification("notifications/initialized")
            
            self.is_connected = True
            logger.info(f"MCP 服务器 {self.server_config.name} 初始化成功")
            
            return True
            
        except Exception as e:
            logger.error(f"初始化 MCP 服务器 {self.server_config.name} 时出错: {e}")
            return False
    
    def send_notification(self, method: str, params: Dict[str, Any] = None):
        """发送通知到 MCP 服务器"""
        if not self.process or self.process.poll() is not None:
            return
        
        notification = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {}
        }
        
        try:
            notification_json = json.dumps(notification) + "\n"
            self.process.stdin.write(notification_json)
            self.process.stdin.flush()
        except Exception as e:
            logger.error(f"发送通知到 MCP 服务器 {self.server_config.name} 时出错: {e}")
    
    def list_tools(self) -> List[MCPTool]:
        """获取可用工具列表"""
        try:
            result = self.send_request("tools/list")
            tools = []
            
            for tool_info in result.get("tools", []):
                tool = MCPTool(
                    name=tool_info["name"],
                    description=tool_info.get("description", ""),
                    parameters=tool_info.get("inputSchema", {}).get("properties", {}),
                    server_name=self.server_config.name,
                    input_schema=tool_info.get("inputSchema", {})
                )
                tools.append(tool)
                self.tools[tool.name] = tool
            
            logger.info(f"从 MCP 服务器 {self.server_config.name} 获取到 {len(tools)} 个工具")
            return tools
            
        except Exception as e:
            logger.error(f"获取 MCP 工具列表时出错: {e}")
            return []
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """调用 MCP 工具"""
        try:
            if tool_name not in self.tools:
                raise ValueError(f"工具 {tool_name} 不存在")
            
            params = {
                "name": tool_name,
                "arguments": arguments
            }
            
            result = self.send_request("tools/call", params)
            
            # 处理结果
            if "content" in result:
                content = result["content"]
                if isinstance(content, list) and len(content) > 0:
                    # 返回第一个内容项的文本
                    return content[0].get("text", str(content[0]))
                else:
                    return str(content)
            else:
                return result
            
        except Exception as e:
            logger.error(f"调用 MCP 工具 {tool_name} 时出错: {e}")
            raise
    
    def ping(self) -> bool:
        """检查服务器连接状态"""
        try:
            if not self.process or self.process.poll() is not None:
                return False
            
            # 尝试发送 ping 请求，如果不支持则使用 tools/list
            try:
                self.send_request("ping")
            except RuntimeError as e:
                if "Unknown method" in str(e) or "method not found" in str(e).lower():
                    # 如果不支持 ping，使用 tools/list 作为健康检查
                    self.send_request("tools/list")
                else:
                    raise
            
            self.last_heartbeat = datetime.now()
            return True
            
        except Exception as e:
            logger.debug(f"MCP 服务器 {self.server_config.name} ping 失败: {e}")
            return False
    
    def get_server_info(self) -> Dict[str, Any]:
        """获取服务器信息"""
        return {
            "name": self.server_config.name,
            "description": self.server_config.description,
            "enabled": self.server_config.enabled,
            "connected": self.is_connected,
            "tools_count": len(self.tools),
            "process_running": self.process and self.process.poll() is None,
            "last_heartbeat": self.last_heartbeat.isoformat() if self.last_heartbeat else None
        }
    
    def connect(self) -> bool:
        """连接到 MCP 服务器"""
        try:
            if not self.server_config.enabled:
                logger.info(f"MCP 服务器 {self.server_config.name} 已禁用")
                return False
            
            # 启动服务器
            if not self.start_server():
                return False
            
            # 初始化连接
            if not self.initialize():
                self.stop_server()
                return False
            
            # 获取工具列表
            self.list_tools()
            
            return True
            
        except Exception as e:
            logger.error(f"连接到 MCP 服务器 {self.server_config.name} 时出错: {e}")
            return False
    
    def disconnect(self):
        """断开与 MCP 服务器的连接"""
        self.stop_server()
        self.tools.clear()
        self.is_connected = False
    
    def __del__(self):
        """析构函数"""
        self.disconnect() 