"""
智能模型路由器
根据任务类型和内容特征，自动选择最合适的模型
"""

import re
from typing import Dict, List, Any, Optional
from ..models.base_llm import BaseLLM
from ..models.multimodal_manager import multimodal_manager
from datetime import datetime

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
                    r"图像|图片|照片|截图|png|jpg|jpeg|gif|识别.*图|看.*图|分析.*图",
                    r"视觉|visual|image|photo|screenshot|识别屏幕|分析图片",
                    r"generate_vision|vision_model|多模态|multimodal|describe_image|analyze_image|extract_text_from_image|identify_objects",
                    r"compare_images|analyze_image_style|generate_image_tags"
                ],
                "required_capabilities": ["vision"],
                "priority": 10
            },
            {
                "name": "code_generation",
                "description": "代码生成和编程任务",
                "patterns": [
                    r"代码|编程|函数|class|def|import|编写.*代码|生成.*代码",
                    r"python|javascript|html|css|java|cpp|代码分析|programming|coding",
                    r"写.*程序|创建.*脚本|程序设计|软件开发",
                    r"analyze_code_quality|find_security_issues|analyze_project_structure|extract_api_documentation"
                ],
                "required_capabilities": ["code"],
                "priority": 9
            },
            {
                "name": "document_generation",
                "description": "文档生成和技术写作任务",
                "patterns": [
                    r"文档|README|说明书|技术文档|API文档|用户手册",
                    r"generate_project_readme|extract_api_documentation|generate_technical_doc",
                    r"写.*文档|生成.*文档|技术写作|文档编写",
                    r"analyze_project_architecture|documentation|manual|guide"
                ],
                "required_capabilities": ["code", "reasoning"],
                "priority": 8
            },
            {
                "name": "content_processing",
                "description": "内容处理和整合任务",
                "patterns": [
                    r"整合|总结|摘要|提取|转换|分析内容|内容处理",
                    r"integrate_content|summarize_content|extract_information|transform_format",
                    r"内容整合|信息提取|格式转换|数据处理"
                ],
                "required_capabilities": ["reasoning"],
                "priority": 7
            },
            {
                "name": "web_search",
                "description": "网络搜索和信息检索任务",
                "patterns": [
                    r"搜索|查找|检索|web_search|search_news|search_academic",
                    r"网络搜索|信息检索|查询|找.*信息|搜索.*信息",
                    r"google|百度|搜索引擎|search"
                ],
                "required_capabilities": ["general"],
                "priority": 6
            },
            {
                "name": "complex_reasoning",
                "description": "复杂推理和分析任务",
                "patterns": [
                    r"分析|推理|解决.*问题|复杂.*任务|策略|规划",
                    r"比较|评估|建议|方案|解决方案|深入分析",
                    r"逻辑推理|问题解决|决策支持|战略分析"
                ],
                "required_capabilities": ["reasoning"],
                "priority": 5
            },
            {
                "name": "system_operations",
                "description": "系统操作和文件管理任务",
                "patterns": [
                    r"文件|目录|系统|操作|管理|shell|命令行",
                    r"open_file|list_directory|write_file|read_file|run_shell_command",
                    r"文件操作|系统操作|目录管理|命令执行"
                ],
                "required_capabilities": ["general"],
                "priority": 4
            },
            {
                "name": "general_tasks",
                "description": "一般任务和对话",
                "patterns": [
                    r".*"  # 匹配所有内容，作为默认规则
                ],
                "required_capabilities": ["general"],
                "priority": 1
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
        
        # 根据任务描述匹配路由规则，按优先级排序
        sorted_rules = sorted(self.routing_rules, key=lambda x: x.get("priority", 0), reverse=True)
        
        for rule in sorted_rules:
            for pattern in rule["patterns"]:
                if re.search(pattern, task_description, re.IGNORECASE):
                    # 找到匹配的规则，根据所需能力选择最合适的模型
                    required_capabilities = rule["required_capabilities"]
                    selected_model = self._select_model_by_capability(required_capabilities)
                    
                    # 记录路由信息用于调试
                    self._log_routing_decision(task_description, rule, selected_model)
                    
                    return selected_model
        
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
            
            # 检查模型是否具有所需能力
            capability_match_score = 0
            for capability in required_capabilities:
                if capability in model_capabilities:
                    capability_match_score += 1
            
            if capability_match_score > 0:
                suitable_models.append({
                    'alias': model_alias,
                    'capabilities': model_capabilities,
                    'capability_match_score': capability_match_score,
                    'priority': self._calculate_model_priority(model_alias, required_capabilities)
                })
        
        if suitable_models:
            # 按能力匹配度和优先级排序，选择最合适的模型
            suitable_models.sort(key=lambda x: (x['capability_match_score'], x['priority']), reverse=True)
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
        
        # 获取模型的实际配置能力
        model_capabilities = self._get_model_capabilities(model_alias)
        
        # 从配置中获取模型的优先级设置
        model_priority = 50  # 默认优先级
        if "models" in self.config and "providers" in self.config["models"]:
            for provider in self.config["models"]["providers"]:
                if provider.get("alias") == model_alias:
                    model_priority = provider.get("priority", 50)
                    break
        
        priority += model_priority
        
        # 根据能力匹配度调整优先级
        capability_bonus = {
            "vision": 25,
            "code": 20,
            "reasoning": 15,
            "general": 10
        }
        
        for capability in required_capabilities:
            if capability in model_capabilities:
                priority += capability_bonus.get(capability, 5)
        
        # 检查是否是主模型（给予额外优先级）
        primary_model = self.config.get("models", {}).get("primary")
        if model_alias == primary_model:
            priority += 10
        
        return priority
    
    def _select_fallback_model(self, required_capabilities: List[str]) -> Optional[str]:
        """当没有找到具有确切能力的模型时，选择部分匹配的模型作为后备"""
        fallback_candidates = []
        
        # 寻找具有部分匹配能力的模型
        for model_alias in self.model_clients:
            model_capabilities = self._get_model_capabilities(model_alias)
            
            # 计算能力匹配度
            match_count = sum(1 for cap in required_capabilities if cap in model_capabilities)
            
            if match_count > 0:
                fallback_candidates.append({
                    'alias': model_alias,
                    'match_count': match_count,
                    'priority': self._calculate_model_priority(model_alias, required_capabilities)
                })
        
        if fallback_candidates:
            # 选择匹配度最高、优先级最高的模型
            fallback_candidates.sort(key=lambda x: (x['match_count'], x['priority']), reverse=True)
            return fallback_candidates[0]['alias']
        
        return None
    
    def _log_routing_decision(self, task_description: str, rule: Dict[str, Any], selected_model: str):
        """记录路由决策信息用于调试"""
        # 这里可以添加日志记录逻辑
        # 目前只是一个占位符，可以根据需要实现
        pass
    
    def get_enhanced_routing_info(self, task_description: str, task_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """获取增强的任务路由信息，用于调试和分析"""
        task_context = task_context or {}
        selected_model = self.route_task(task_description, task_context)
        
        # 找到匹配的规则
        matched_rule = None
        sorted_rules = sorted(self.routing_rules, key=lambda x: x.get("priority", 0), reverse=True)
        
        for rule in sorted_rules:
            for pattern in rule["patterns"]:
                if re.search(pattern, task_description, re.IGNORECASE):
                    matched_rule = rule
                    break
            if matched_rule:
                break
        
        # 获取模型信息
        selected_model_info = None
        if selected_model in self.model_clients:
            client = self.model_clients[selected_model]
            selected_model_info = {
                "alias": selected_model,
                "model_name": client.model_name,
                "provider": client.__class__.__name__,
                "capabilities": self._get_model_capabilities(selected_model)
            }
        
        return {
            "task_description": task_description,
            "task_context": task_context,
            "selected_model": selected_model,
            "selected_model_info": selected_model_info,
            "matched_rule": matched_rule["name"] if matched_rule else "default",
            "rule_description": matched_rule["description"] if matched_rule else "默认规则",
            "rule_priority": matched_rule.get("priority", 0) if matched_rule else 0,
            "available_models": list(self.model_clients.keys()),
            "routing_timestamp": datetime.now().isoformat()
        }
    
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
        # 从配置文件获取能力
        if "models" in self.config and "providers" in self.config["models"]:
            for provider in self.config["models"]["providers"]:
                if provider.get("alias") == model_alias:
                    capabilities = provider.get("capabilities", [])
                    if capabilities:
                        return capabilities
        
        # 如果配置中没有指定能力，返回基础通用能力
        # 这种情况下应该提醒用户完善配置
        return ["general"]
    
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
    
    def validate_routing_rules(self) -> Dict[str, Any]:
        """验证路由规则的完整性和有效性"""
        validation_results = {
            "valid": True,
            "issues": [],
            "warnings": [],
            "statistics": {
                "total_rules": len(self.routing_rules),
                "rules_by_priority": {},
                "models_by_capability": {}
            }
        }
        
        # 统计规则优先级分布
        for rule in self.routing_rules:
            priority = rule.get("priority", 0)
            if priority not in validation_results["statistics"]["rules_by_priority"]:
                validation_results["statistics"]["rules_by_priority"][priority] = 0
            validation_results["statistics"]["rules_by_priority"][priority] += 1
        
        # 统计模型能力分布并检查配置完整性
        models_with_minimal_config = []
        for model_alias in self.model_clients:
            capabilities = self._get_model_capabilities(model_alias)
            
            # 检查是否只有基础general能力
            if capabilities == ["general"]:
                models_with_minimal_config.append(model_alias)
                validation_results["warnings"].append(
                    f"模型 '{model_alias}' 只配置了基础能力，建议完善能力配置以获得更好的路由效果"
                )
            
            for capability in capabilities:
                if capability not in validation_results["statistics"]["models_by_capability"]:
                    validation_results["statistics"]["models_by_capability"][capability] = []
                validation_results["statistics"]["models_by_capability"][capability].append(model_alias)
        
        # 检查每个规则是否有对应的模型可以处理
        for rule in self.routing_rules:
            required_capabilities = rule.get("required_capabilities", [])
            has_suitable_model = False
            
            for model_alias in self.model_clients:
                model_capabilities = self._get_model_capabilities(model_alias)
                if all(cap in model_capabilities for cap in required_capabilities):
                    has_suitable_model = True
                    break
            
            if not has_suitable_model:
                validation_results["valid"] = False
                validation_results["issues"].append(
                    f"规则 '{rule['name']}' 需要能力 {required_capabilities}，但没有模型具备这些能力"
                )
        
        return validation_results
    
    def get_routing_statistics(self) -> Dict[str, Any]:
        """获取路由统计信息"""
        return {
            "total_models": len(self.model_clients),
            "total_rules": len(self.routing_rules),
            "models_by_provider": self._get_models_by_provider(),
            "capabilities_coverage": self._get_capabilities_coverage(),
            "rule_priority_distribution": self._get_rule_priority_distribution()
        }
    
    def _get_models_by_provider(self) -> Dict[str, List[str]]:
        """获取按提供商分组的模型列表"""
        providers = {}
        for alias, client in self.model_clients.items():
            provider_name = client.__class__.__name__
            if provider_name not in providers:
                providers[provider_name] = []
            providers[provider_name].append(alias)
        return providers
    
    def _get_capabilities_coverage(self) -> Dict[str, List[str]]:
        """获取能力覆盖情况"""
        coverage = {}
        for model_alias in self.model_clients:
            capabilities = self._get_model_capabilities(model_alias)
            for capability in capabilities:
                if capability not in coverage:
                    coverage[capability] = []
                coverage[capability].append(model_alias)
        return coverage
    
    def _get_rule_priority_distribution(self) -> Dict[int, int]:
        """获取规则优先级分布"""
        distribution = {}
        for rule in self.routing_rules:
            priority = rule.get("priority", 0)
            if priority not in distribution:
                distribution[priority] = 0
            distribution[priority] += 1
        return distribution 