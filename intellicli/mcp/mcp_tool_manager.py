"""
MCP 工具管理器
管理多个 MCP 服务器连接和工具的统一接口
"""

import logging
from typing import Dict, List, Any, Optional, Union
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import time
from datetime import datetime, timedelta

from .mcp_client import MCPClient, MCPServerConfig, MCPTool

logger = logging.getLogger(__name__)

class MCPToolManager:
    """MCP 工具管理器"""
    
    def __init__(self, server_configs: List[MCPServerConfig] = None):
        self.server_configs = server_configs or []
        self.clients: Dict[str, MCPClient] = {}
        self.all_tools: Dict[str, MCPTool] = {}
        self.server_status: Dict[str, Dict[str, Any]] = {}
        self.health_check_interval = 30  # 健康检查间隔（秒）
        self.health_check_thread = None
        self.health_check_running = False
        self.connection_lock = threading.Lock()
        
        # 为每个服务器配置初始化状态
        for server_config in self.server_configs:
            self.server_status[server_config.name] = {
                "config": server_config,
                "connected": False,
                "last_check": None,
                "error": None,
                "tools_count": 0
            }
        
    def add_server(self, server_config: MCPServerConfig):
        """添加 MCP 服务器配置"""
        self.server_configs.append(server_config)
        self.server_status[server_config.name] = {
            "config": server_config,
            "connected": False,
            "last_check": None,
            "error": None,
            "tools_count": 0
        }
        logger.info(f"添加了 MCP 服务器配置: {server_config.name}")
    
    def remove_server(self, server_name: str):
        """移除 MCP 服务器配置"""
        # 断开连接
        if server_name in self.clients:
            self.clients[server_name].disconnect()
            del self.clients[server_name]
        
        # 移除工具
        tools_to_remove = [name for name, tool in self.all_tools.items() 
                          if tool.server_name == server_name]
        for tool_name in tools_to_remove:
            del self.all_tools[tool_name]
        
        # 移除配置
        self.server_configs = [config for config in self.server_configs 
                              if config.name != server_name]
        
        if server_name in self.server_status:
            del self.server_status[server_name]
        
        logger.info(f"移除了 MCP 服务器: {server_name}")
    
    def connect_all_servers(self) -> Dict[str, bool]:
        """连接所有 MCP 服务器"""
        results = {}
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_server = {
                executor.submit(self._connect_server, config): config.name 
                for config in self.server_configs
            }
            
            for future in as_completed(future_to_server):
                server_name = future_to_server[future]
                try:
                    success = future.result()
                    results[server_name] = success
                    self.server_status[server_name]["connected"] = success
                    self.server_status[server_name]["last_check"] = datetime.now()
                    
                    if success:
                        logger.info(f"成功连接到 MCP 服务器: {server_name}")
                    else:
                        logger.error(f"连接到 MCP 服务器失败: {server_name}")
                        
                except Exception as e:
                    logger.error(f"连接到 MCP 服务器 {server_name} 时出错: {e}")
                    results[server_name] = False
                    self.server_status[server_name]["connected"] = False
                    self.server_status[server_name]["error"] = str(e)
        
        return results
    
    def _connect_server(self, server_config: MCPServerConfig) -> bool:
        """连接单个 MCP 服务器"""
        try:
            with self.connection_lock:
                if server_config.name in self.clients:
                    # 如果已经连接，先断开
                    self.clients[server_config.name].disconnect()
                
                # 创建新的客户端
                client = MCPClient(server_config)
                
                # 连接服务器
                if client.connect():
                    self.clients[server_config.name] = client
                    
                    # 更新工具信息
                    self._update_tools_from_server(server_config.name)
                    
                    return True
                else:
                    return False
                    
        except Exception as e:
            logger.error(f"连接 MCP 服务器 {server_config.name} 时出错: {e}")
            return False
    
    def _update_tools_from_server(self, server_name: str):
        """从服务器更新工具信息"""
        if server_name not in self.clients:
            return
        
        client = self.clients[server_name]
        
        # 移除该服务器的旧工具
        tools_to_remove = [name for name, tool in self.all_tools.items() 
                          if tool.server_name == server_name]
        for tool_name in tools_to_remove:
            del self.all_tools[tool_name]
        
        # 添加新工具
        tools = client.list_tools()
        for tool in tools:
            # 处理工具名称冲突
            tool_name = tool.name
            if tool_name in self.all_tools:
                # 如果工具名称冲突，添加服务器名称前缀
                tool_name = f"{server_name}_{tool.name}"
                tool.name = tool_name
            
            self.all_tools[tool_name] = tool
        
        # 更新状态
        self.server_status[server_name]["tools_count"] = len(tools)
        logger.info(f"从 MCP 服务器 {server_name} 更新了 {len(tools)} 个工具")
    
    def disconnect_all_servers(self):
        """断开所有 MCP 服务器连接"""
        for client in self.clients.values():
            client.disconnect()
        self.clients.clear()
        self.all_tools.clear()
        
        # 更新状态
        for server_name in self.server_status:
            self.server_status[server_name]["connected"] = False
            self.server_status[server_name]["tools_count"] = 0
        
        logger.info("已断开所有 MCP 服务器连接")
    
    def get_all_tools(self) -> List[Dict[str, Any]]:
        """获取所有 MCP 工具信息（兼容执行器格式）"""
        tool_info_list = []
        
        for tool_name, tool in self.all_tools.items():
            # 转换为执行器期望的格式
            parameters = []
            
            if tool.input_schema and "properties" in tool.input_schema:
                required_fields = tool.input_schema.get("required", [])
                
                for param_name, param_info in tool.input_schema["properties"].items():
                    param_data = {
                        "name": param_name,
                        "type": param_info.get("type", "string"),
                        "required": param_name in required_fields,
                        "description": param_info.get("description", "")
                    }
                    parameters.append(param_data)
            
            tool_info = {
                "name": tool_name,
                "description": f"[MCP:{tool.server_name}] {tool.description}",
                "parameters": parameters,
                "server_name": tool.server_name,
                "is_mcp_tool": True
            }
            
            tool_info_list.append(tool_info)
        
        return tool_info_list
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """调用 MCP 工具"""
        if tool_name not in self.all_tools:
            raise ValueError(f"MCP 工具 {tool_name} 不存在")
        
        tool = self.all_tools[tool_name]
        server_name = tool.server_name
        
        if server_name not in self.clients:
            raise RuntimeError(f"MCP 服务器 {server_name} 未连接")
        
        client = self.clients[server_name]
        
        # 调用工具
        return client.call_tool(tool.name, arguments)
    
    def get_server_status(self) -> Dict[str, Dict[str, Any]]:
        """获取所有服务器状态"""
        status = {}
        
        for server_name, server_info in self.server_status.items():
            client_info = {}
            if server_name in self.clients:
                client_info = self.clients[server_name].get_server_info()
            
            status[server_name] = {
                **server_info,
                **client_info
            }
        
        return status
    
    def start_health_check(self):
        """启动健康检查"""
        if self.health_check_running:
            return
        
        self.health_check_running = True
        self.health_check_thread = threading.Thread(target=self._health_check_loop)
        self.health_check_thread.daemon = True
        self.health_check_thread.start()
        logger.info("启动了 MCP 服务器健康检查")
    
    def stop_health_check(self):
        """停止健康检查"""
        self.health_check_running = False
        if self.health_check_thread:
            self.health_check_thread.join()
        logger.info("停止了 MCP 服务器健康检查")
    
    def _health_check_loop(self):
        """健康检查循环"""
        while self.health_check_running:
            try:
                self._perform_health_check()
                time.sleep(self.health_check_interval)
            except Exception as e:
                logger.error(f"健康检查时出错: {e}")
                time.sleep(5)  # 出错时短暂休息
    
    def _perform_health_check(self):
        """执行健康检查"""
        for server_name, client in self.clients.items():
            try:
                if client.ping():
                    self.server_status[server_name]["connected"] = True
                    self.server_status[server_name]["error"] = None
                else:
                    self.server_status[server_name]["connected"] = False
                    self.server_status[server_name]["error"] = "Ping failed"
                    
                    # 尝试重新连接
                    if client.server_config.auto_restart:
                        logger.info(f"尝试重新连接 MCP 服务器: {server_name}")
                        if self._connect_server(client.server_config):
                            logger.info(f"成功重新连接 MCP 服务器: {server_name}")
                        else:
                            logger.error(f"重新连接 MCP 服务器失败: {server_name}")
                
                self.server_status[server_name]["last_check"] = datetime.now()
                
            except Exception as e:
                logger.error(f"检查 MCP 服务器 {server_name} 健康状态时出错: {e}")
                self.server_status[server_name]["connected"] = False
                self.server_status[server_name]["error"] = str(e)
    
    def get_tool_by_name(self, tool_name: str) -> Optional[MCPTool]:
        """根据名称获取工具"""
        return self.all_tools.get(tool_name)
    
    def get_tools_by_server(self, server_name: str) -> List[MCPTool]:
        """获取指定服务器的工具"""
        return [tool for tool in self.all_tools.values() 
                if tool.server_name == server_name]
    
    def is_mcp_tool(self, tool_name: str) -> bool:
        """检查是否是 MCP 工具"""
        return tool_name in self.all_tools
    
    def get_available_servers(self) -> List[str]:
        """获取可用的服务器列表"""
        return [name for name, status in self.server_status.items() 
                if status["connected"]]
    
    def refresh_tools(self):
        """刷新所有工具信息"""
        for server_name in self.clients:
            self._update_tools_from_server(server_name)
        logger.info("已刷新所有 MCP 工具信息")
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        total_servers = len(self.server_configs)
        connected_servers = len(self.get_available_servers())
        total_tools = len(self.all_tools)
        
        tools_by_server = {}
        for tool in self.all_tools.values():
            server_name = tool.server_name
            if server_name not in tools_by_server:
                tools_by_server[server_name] = 0
            tools_by_server[server_name] += 1
        
        return {
            "total_servers": total_servers,
            "connected_servers": connected_servers,
            "total_tools": total_tools,
            "tools_by_server": tools_by_server,
            "health_check_running": self.health_check_running
        }
    
    def __del__(self):
        """析构函数"""
        self.stop_health_check()
        self.disconnect_all_servers() 