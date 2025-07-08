"""
智能模型路由器
根据任务类型和内容特征，自动选择最合适的模型
"""

import re
from typing import Dict, List, Any, Optional
from ..models.base_llm import BaseLLM
from ..models.multimodal_manager import multimodal_manager

class ModelRouter:
    """智能模型路由器，根据任务特征选择最合适的模型"""
    
    def __init__(self, model_clients: Dict[str, BaseLLM], config: Dict[str, Any]):
        """
        初始化模型路由器
        
        Args:
            model_clients: 模型别名到客户端的映射
            config: 配置信息
        """
        self.model_clients = model_clients
        self.config = config
        self.routing_rules = self._build_routing_rules()
        
        # 注册模型到多模态管理器
        self._register_models_to_multimodal_manager()
    
    def _build_routing_rules(self) -> List[Dict[str, Any]]:
        """动态构建路由规则，基于实际可用的模型"""
        return [
            {
                "name": "vision_tasks",
                "description": "图像和视觉相关任务",
                "patterns": [
                    r"图像|图片|照片|截图|png|jpg|jpeg|gif|识别.*图|看.*图",
                    r"视觉|visual|image|photo|screenshot|识别屏幕|分析图片",
                    r"generate_vision|vision_model|多模态|multimodal"
                ],
                "required_capabilities": ["vision"]
            },
            {
                "name": "code_generation",
                "description": "代码生成和编程任务",
                "patterns": [
                    r"代码|编程|函数|class|def|import|编写.*代码",
                    r"python|javascript|html|css|java|cpp|代码分析",
                    r"写.*程序|创建.*脚本|生成.*代码|程序设计"
                ],
                "required_capabilities": ["code"]
            },
            {
                "name": "complex_reasoning",
                "description": "复杂推理和分析任务",
                "patterns": [
                    r"分析|推理|解决.*问题|复杂.*任务|策略|规划",
                    r"比较|评估|建议|方案|解决方案|深入分析"
                ],
                "required_capabilities": ["reasoning"]
            },
            {
                "name": "general_tasks",
                "description": "一般任务和对话",
                "patterns": [
                    r".*"  # 匹配所有内容，作为默认规则
                ],
                "required_capabilities": ["general"]
            }
        ]
    
    def route_task(self, task_description: str, task_context: Dict[str, Any] = None) -> str:
        """
        根据任务描述和上下文选择最合适的模型
        
        Args:
            task_description: 任务描述
            task_context: 任务上下文信息
            
        Returns:
            选择的模型别名
        """
        task_context = task_context or {}
        
        # 检查是否有明确的模型指定
        if "preferred_model" in task_context:
            preferred = task_context["preferred_model"]
            if preferred in self.model_clients:
                return preferred
        
        # 检查是否涉及文件操作且包含图像文件
        if "file_paths" in task_context:
            image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff']
            for path in task_context["file_paths"]:
                if any(path.lower().endswith(ext) for ext in image_extensions):
                    return self._select_model_by_capability(["vision"])
        
        # 根据任务描述匹配路由规则
        for rule in self.routing_rules:
            for pattern in rule["patterns"]:
                if re.search(pattern, task_description, re.IGNORECASE):
                    # 找到匹配的规则，根据所需能力选择最合适的模型
                    required_capabilities = rule["required_capabilities"]
                    return self._select_model_by_capability(required_capabilities)
        
        # 如果没有匹配的规则，返回默认的主模型
        primary_model = self.config.get("models", {}).get("primary")
        if primary_model and primary_model in self.model_clients:
            return primary_model
        
        # 最后的后备选择
        return list(self.model_clients.keys())[0] if self.model_clients else None
    
    def _select_model_by_capability(self, required_capabilities: List[str]) -> str:
        """根据所需能力选择最合适的模型"""
        # 获取所有具有所需能力的模型
        suitable_models = []
        
        for model_alias in self.model_clients:
            model_capabilities = self._get_model_capabilities(model_alias)
            if any(capability in model_capabilities for capability in required_capabilities):
                suitable_models.append({
                    'alias': model_alias,
                    'capabilities': model_capabilities,
                    'priority': self._calculate_model_priority(model_alias, required_capabilities)
                })
        
        if suitable_models:
            # 按优先级排序，选择最合适的模型
            suitable_models.sort(key=lambda x: x['priority'], reverse=True)
            return suitable_models[0]['alias']
        
        # 如果没有找到具有确切能力的模型，使用启发式规则
        fallback_model = self._select_fallback_model(required_capabilities)
        if fallback_model:
            return fallback_model
        
        # 最后的后备选择：返回主模型或第一个可用模型
        primary_model = self.config.get("models", {}).get("primary")
        if primary_model and primary_model in self.model_clients:
            return primary_model
        
        return list(self.model_clients.keys())[0] if self.model_clients else None
    
    def _calculate_model_priority(self, model_alias: str, required_capabilities: List[str]) -> int:
        """计算模型对于特定能力需求的优先级"""
        priority = 0
        alias_lower = model_alias.lower()
        
        # 基于模型类型的基础优先级
        model_type_priorities = {
            'claude': 90,     # Claude 通常在推理和文本质量方面表现优秀
            'openai': 85,     # OpenAI 模型通常表现均衡
            'gpt': 85,        # GPT 系列模型
            'gemini': 80,     # Google Gemini 模型
            'deepseek': 75,   # DeepSeek 在代码方面表现出色
            'gemma': 70,      # Gemma 模型
            'llava': 65,      # LLaVA 主要用于视觉任务
            'llama': 60,      # LLaMA 基础模型
        }
        
        for model_type, base_priority in model_type_priorities.items():
            if model_type in alias_lower:
                priority += base_priority
                break
        
        # 根据特定能力需求调整优先级
        for capability in required_capabilities:
            if capability == "vision":
                if any(keyword in alias_lower for keyword in ['llava', 'vision', 'claude', 'gpt-4']):
                    priority += 20
            elif capability == "code":
                if any(keyword in alias_lower for keyword in ['deepseek', 'code', 'coder', 'claude', 'gpt-4']):
                    priority += 15
            elif capability == "reasoning":
                if any(keyword in alias_lower for keyword in ['claude', 'gpt-4', 'gemini', 'reasoning']):
                    priority += 15
        
        # 检查是否是主模型（给予额外优先级）
        primary_model = self.config.get("models", {}).get("primary")
        if model_alias == primary_model:
            priority += 10
        
        return priority
    
    def _select_fallback_model(self, required_capabilities: List[str]) -> Optional[str]:
        """当没有找到具有确切能力的模型时，使用启发式规则选择后备模型"""
        capability_keywords = {
            "vision": ["llava", "vision", "claude", "openai", "gpt", "gemini"],
            "code": ["deepseek", "code", "coder", "claude", "openai", "gpt", "gemini", "gemma"],
            "reasoning": ["claude", "openai", "gpt", "gemini", "deepseek", "gemma"],
            "general": ["claude", "openai", "gpt", "gemini", "deepseek", "gemma", "llama"]
        }
        
        for capability in required_capabilities:
            if capability in capability_keywords:
                for keyword in capability_keywords[capability]:
                    for model_alias in self.model_clients:
                        if keyword in model_alias.lower():
                            return model_alias
        
        return None
    
    def get_model_client(self, model_alias: str) -> Optional[BaseLLM]:
        """获取指定模型的客户端"""
        return self.model_clients.get(model_alias)
    
    def get_routing_info(self, task_description: str) -> Dict[str, Any]:
        """获取任务路由信息，用于调试和日志"""
        selected_model = self.route_task(task_description)
        
        # 找到匹配的规则
        matched_rule = None
        for rule in self.routing_rules:
            for pattern in rule["patterns"]:
                if re.search(pattern, task_description, re.IGNORECASE):
                    matched_rule = rule
                    break
            if matched_rule:
                break
        
        return {
            "task_description": task_description,
            "selected_model": selected_model,
            "matched_rule": matched_rule["name"] if matched_rule else "default",
            "rule_description": matched_rule["description"] if matched_rule else "默认规则",
            "available_models": list(self.model_clients.keys())
        }
    
    def list_available_models(self) -> Dict[str, Dict[str, Any]]:
        """列出所有可用模型及其信息"""
        models_info = {}
        for alias, client in self.model_clients.items():
            models_info[alias] = {
                "model_name": client.model_name,
                "provider": client.__class__.__name__,
                "capabilities": self._get_model_capabilities(alias)
            }
        return models_info
    
    def _get_model_capabilities(self, model_alias: str) -> List[str]:
        """获取模型的能力列表"""
        # 首先尝试从配置文件获取能力
        if "models" in self.config and "providers" in self.config["models"]:
            for provider in self.config["models"]["providers"]:
                if provider.get("alias") == model_alias:
                    capabilities = provider.get("capabilities", [])
                    if capabilities:
                        return capabilities
    
    def _register_models_to_multimodal_manager(self):
        """将模型注册到多模态管理器"""
        for alias, client in self.model_clients.items():
            capabilities = self._get_model_capabilities(alias)
            
            if 'vision' in capabilities:
                multimodal_manager.register_vision_model(alias, client)
            else:
                multimodal_manager.register_text_model(alias, client)
    
    def process_multimodal_task(self, task_description: str, context: Dict[str, Any] = None) -> str:
        """处理多模态任务"""
        return multimodal_manager.process_multimodal_input(task_description, context)
    
    def analyze_task_modality(self, task_description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """分析任务的模态类型"""
        return multimodal_manager.analyze_input(task_description, context)
        
        # 如果配置中没有指定能力，使用启发式规则
        capabilities = ["general"]
        
        alias_lower = model_alias.lower()
        if "llava" in alias_lower or "vision" in alias_lower:
            capabilities.append("vision")
        if "gemini" in alias_lower:
            capabilities.extend(["code", "reasoning", "vision"])
        if "gemma" in alias_lower or "llama" in alias_lower:
            capabilities.extend(["code", "reasoning"])
        if "deepseek" in alias_lower:
            capabilities.extend(["code", "reasoning"])
        if "claude" in alias_lower:
            capabilities.extend(["code", "reasoning", "vision"])
        if "openai" in alias_lower or "gpt" in alias_lower:
            capabilities.extend(["code", "reasoning", "vision"])
        
        return capabilities 