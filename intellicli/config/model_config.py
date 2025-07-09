"""
模型配置管理模块
提供交互式模型配置向导和配置验证功能
"""

import os
import yaml
import json
from typing import Dict, List, Any, Optional
from ..ui.display import ui

class ModelConfigManager:
    """模型配置管理器"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.providers_info = {
            "ollama": {
                "name": "Ollama",
                "description": "本地或远程 Ollama 服务",
                "required_fields": ["model_name", "base_url"],
                "optional_fields": [],
                "default_base_url": "http://localhost:11434",
                "supported_capabilities": ["general", "code", "reasoning", "vision"]
            },
            "gemini": {
                "name": "Google Gemini",
                "description": "Google Gemini API 服务",
                "required_fields": ["model_name"],
                "optional_fields": ["api_key"],
                "env_var": "GEMINI_API_KEY",
                "supported_capabilities": ["general", "code", "reasoning", "vision"]
            },
            "openai": {
                "name": "OpenAI",
                "description": "OpenAI API 服务 (ChatGPT)",
                "required_fields": ["model_name"],
                "optional_fields": ["api_key", "base_url"],
                "env_var": "OPENAI_API_KEY",
                "supported_capabilities": ["general", "code", "reasoning", "vision"]
            },
            "deepseek": {
                "name": "DeepSeek",
                "description": "DeepSeek API 服务",
                "required_fields": ["model_name"],
                "optional_fields": ["api_key", "base_url"],
                "env_var": "DEEPSEEK_API_KEY",
                "default_base_url": "https://api.deepseek.com",
                "supported_capabilities": ["general", "code", "reasoning"]
            },
            "claude": {
                "name": "Anthropic Claude",
                "description": "Anthropic Claude API 服务",
                "required_fields": ["model_name"],
                "optional_fields": ["api_key"],
                "env_var": "ANTHROPIC_API_KEY",
                "supported_capabilities": ["general", "code", "reasoning", "vision"]
            }
        }
        
        self.capability_descriptions = {
            "general": "通用对话和文本处理",
            "code": "代码生成和编程任务",
            "reasoning": "复杂推理和分析任务",
            "vision": "图像和视觉相关任务"
        }
        
        # 搜索引擎配置信息
        self.search_engines_info = {
            "google": {
                "name": "Google Custom Search",
                "description": "Google自定义搜索API",
                "required_fields": ["api_key", "search_engine_id"],
                "config_keys": ["google_search_api_key", "google_search_engine_id"],
                "enabled": False
            },
            "bing": {
                "name": "Bing Search API",
                "description": "微软Bing搜索API",
                "required_fields": ["api_key"],
                "config_keys": ["bing_search_api_key"],
                "enabled": False
            },
            "duckduckgo": {
                "name": "DuckDuckGo",
                "description": "DuckDuckGo免费搜索（无需配置）",
                "required_fields": [],
                "config_keys": [],
                "enabled": True,
                "default": True
            },
            "searx": {
                "name": "SearX",
                "description": "SearX开源搜索引擎（使用公开实例）",
                "required_fields": [],
                "config_keys": [],
                "enabled": True
            }
        }
    
    def has_valid_config(self) -> bool:
        """检查是否有有效的模型配置"""
        if not os.path.exists(self.config_path):
            return False
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # 检查是否有模型配置
            if 'models' not in config:
                return False
            
            models_config = config['models']
            if 'providers' not in models_config or not models_config['providers']:
                return False
            
            # 检查是否至少有一个有效的模型
            providers = models_config['providers']
            return len(providers) > 0 and all(
                'alias' in p and 'provider' in p and 'model_name' in p 
                for p in providers
            )
        except Exception:
            return False
    
    def run_config_wizard(self):
        """运行交互式配置向导"""
        ui.print_section_header("模型配置向导", "🛠️")
        
        ui.print_info("欢迎使用 IntelliCLI 模型配置向导！")
        ui.print_info("我们将帮助您配置AI模型以获得最佳体验。")
        ui.print_info("")
        
        models = []
        
        while True:
            ui.print_section_header(f"配置模型 #{len(models) + 1}", "🤖")
            
            # 选择供应商
            provider = self._select_provider()
            if not provider:
                break
            
            # 配置模型详情
            model_config = self._configure_model(provider)
            if model_config:
                models.append(model_config)
                ui.print_success(f"✅ 已添加模型: {model_config['alias']}")
            
            # 询问是否继续添加
            if len(models) > 0:
                ui.print_info("")
                continue_adding = ui.get_user_input("是否添加更多模型？(y/N)").lower()
                if continue_adding not in ['y', 'yes', '是']:
                    break
        
        if not models:
            ui.print_error("❌ 未配置任何模型，无法继续")
            return False
        
        # 选择主模型
        primary_model = self._select_primary_model(models)
        
        # 配置搜索引擎（可选）
        search_config = self._configure_search_engines()
        
        # 生成完整配置（复盘功能可通过 review-config 命令单独配置）
        config = self._generate_config(models, primary_model, search_config)
        
        # 保存配置
        return self._save_config(config)
    
    def _select_provider(self) -> Optional[str]:
        """选择模型供应商"""
        ui.print_info("📋 可用的模型供应商:")
        
        providers = list(self.providers_info.keys())
        for i, provider_key in enumerate(providers, 1):
            provider_info = self.providers_info[provider_key]
            ui.print_info(f"   {i}. {provider_info['name']} - {provider_info['description']}")
        
        ui.print_info(f"   {len(providers) + 1}. 完成配置")
        ui.print_info("")
        
        while True:
            choice = ui.get_user_input("请选择供应商 (输入数字)")
            
            try:
                choice_num = int(choice)
                if 1 <= choice_num <= len(providers):
                    return providers[choice_num - 1]
                elif choice_num == len(providers) + 1:
                    return None
                else:
                    ui.print_error(f"请输入 1-{len(providers) + 1} 之间的数字")
            except ValueError:
                ui.print_error("请输入有效的数字")
    
    def _configure_model(self, provider: str) -> Optional[Dict[str, Any]]:
        """配置单个模型"""
        provider_info = self.providers_info[provider]
        
        ui.print_info(f"🔧 配置 {provider_info['name']} 模型")
        ui.print_info("")
        
        model_config = {
            "provider": provider
        }
        
        # 模型别名
        while True:
            alias = ui.get_user_input("模型别名 (用于标识此模型)")
            if alias and alias.replace('_', '').replace('-', '').isalnum():
                model_config["alias"] = alias
                break
            ui.print_error("别名只能包含字母、数字、下划线和连字符")
        
        # 模型名称
        model_name = ui.get_user_input("模型名称 (如: gemma3:27b, gpt-4)")
        if not model_name:
            ui.print_error("模型名称不能为空")
            return None
        model_config["model_name"] = model_name
        
        # 供应商特定配置
        if provider == "ollama":
            default_url = provider_info["default_base_url"]
            base_url = ui.get_user_input(f"Ollama 服务器地址 (默认: {default_url})")
            model_config["base_url"] = base_url if base_url else default_url
        
        elif provider == "gemini":
            api_key = ui.get_user_input("Gemini API Key (可留空，将使用环境变量 GEMINI_API_KEY)")
            if api_key:
                model_config["api_key"] = api_key
        
        elif provider == "openai":
            api_key = ui.get_user_input("OpenAI API Key (可留空，将使用环境变量 OPENAI_API_KEY)")
            if api_key:
                model_config["api_key"] = api_key
            
            # 可选的自定义API端点
            base_url = ui.get_user_input("自定义API端点 (可留空，使用默认OpenAI端点)")
            if base_url:
                model_config["base_url"] = base_url
        
        elif provider == "deepseek":
            api_key = ui.get_user_input("DeepSeek API Key (可留空，将使用环境变量 DEEPSEEK_API_KEY)")
            if api_key:
                model_config["api_key"] = api_key
            
            # 可选的自定义API端点
            default_url = provider_info.get("default_base_url", "https://api.deepseek.com")
            base_url = ui.get_user_input(f"DeepSeek API端点 (默认: {default_url})")
            if base_url:
                model_config["base_url"] = base_url
        
        elif provider == "claude":
            api_key = ui.get_user_input("Claude API Key (可留空，将使用环境变量 ANTHROPIC_API_KEY)")
            if api_key:
                model_config["api_key"] = api_key
        
        # 模型能力配置
        capabilities = self._configure_capabilities(provider)
        model_config["capabilities"] = capabilities
        
        # 模型优先级配置
        priority = self._configure_model_priority()
        model_config["priority"] = priority
        
        return model_config
    
    def _configure_capabilities(self, provider: str) -> List[str]:
        """配置模型能力"""
        provider_info = self.providers_info[provider]
        supported = provider_info["supported_capabilities"]
        
        ui.print_info("🎯 请选择该模型的能力 (可多选):")
        
        for i, capability in enumerate(supported, 1):
            description = self.capability_descriptions[capability]
            ui.print_info(f"   {i}. {capability} - {description}")
        
        ui.print_info("")
        ui.print_info("💡 输入数字，用逗号分隔 (如: 1,2,3) 或 'all' 选择全部")
        
        while True:
            choice = ui.get_user_input("选择能力")
            
            if choice.lower() == 'all':
                return supported.copy()
            
            try:
                choices = [int(x.strip()) for x in choice.split(',')]
                if all(1 <= c <= len(supported) for c in choices):
                    return [supported[c-1] for c in choices]
                else:
                    ui.print_error(f"请输入 1-{len(supported)} 之间的数字")
            except ValueError:
                ui.print_error("请输入有效的数字或 'all'")
    
    def _configure_model_priority(self) -> int:
        """配置模型优先级"""
        ui.print_info("")
        ui.print_info("⚖️ 设置模型优先级:")
        ui.print_info("   优先级用于在多个模型都满足任务需求时决定选择顺序")
        ui.print_info("   数值越高优先级越高，建议范围: 1-100")
        ui.print_info("   默认优先级: 50")
        ui.print_info("")
        
        while True:
            priority_input = ui.get_user_input("模型优先级 (1-100, 默认: 50)")
            
            if not priority_input:
                return 50
            
            try:
                priority = int(priority_input)
                if 1 <= priority <= 100:
                    return priority
                else:
                    ui.print_error("优先级必须在 1-100 之间")
            except ValueError:
                ui.print_error("请输入有效的数字")
    
    def _select_primary_model(self, models: List[Dict[str, Any]]) -> str:
        """选择主模型"""
        if len(models) == 1:
            return models[0]["alias"]
        
        ui.print_section_header("选择主模型", "🎯")
        ui.print_info("请选择主要使用的模型 (用于一般任务):")
        ui.print_info("")
        
        for i, model in enumerate(models, 1):
            capabilities = ", ".join(model["capabilities"])
            ui.print_info(f"   {i}. {model['alias']} ({model['provider']}) - {capabilities}")
        
        while True:
            choice = ui.get_user_input("请选择主模型 (输入数字)")
            try:
                choice_num = int(choice)
                if 1 <= choice_num <= len(models):
                    return models[choice_num - 1]["alias"]
                else:
                    ui.print_error(f"请输入 1-{len(models)} 之间的数字")
            except ValueError:
                ui.print_error("请输入有效的数字")
    
    def _configure_search_engines(self) -> Dict[str, Any]:
        """配置搜索引擎"""
        ui.print_section_header("搜索引擎配置 (可选)", "🔍")
        ui.print_info("配置搜索引擎以启用网络搜索功能")
        ui.print_info("如果跳过此步骤，将使用DuckDuckGo作为默认搜索引擎")
        ui.print_info("")
        
        configure_search = ui.get_user_input("是否配置搜索引擎？(y/N)").lower()
        if configure_search not in ['y', 'yes', '是']:
            return {"engines": {}}
        
        search_config = {"engines": {}}
        
        # 显示可配置的搜索引擎
        ui.print_info("📋 可配置的搜索引擎:")
        configurable_engines = {k: v for k, v in self.search_engines_info.items() 
                               if v.get("required_fields")}
        
        for key, info in configurable_engines.items():
            ui.print_info(f"   • {info['name']} - {info['description']}")
        
        ui.print_info("")
        
        for engine_key, engine_info in configurable_engines.items():
            ui.print_info(f"🔧 配置 {engine_info['name']}")
            configure_engine = ui.get_user_input(f"是否配置 {engine_info['name']}？(y/N)").lower()
            
            if configure_engine in ['y', 'yes', '是']:
                engine_config = {}
                
                if engine_key == "google":
                    api_key = ui.get_user_input("Google Search API Key:")
                    search_engine_id = ui.get_user_input("Google Custom Search Engine ID:")
                    
                    if api_key and search_engine_id:
                        engine_config = {
                            "api_key": api_key,
                            "search_engine_id": search_engine_id,
                            "enabled": True
                        }
                        ui.print_success(f"✅ 已配置 {engine_info['name']}")
                    else:
                        ui.print_warning("⚠️ API Key 和 Search Engine ID 都不能为空，跳过配置")
                
                elif engine_key == "bing":
                    api_key = ui.get_user_input("Bing Search API Key:")
                    
                    if api_key:
                        engine_config = {
                            "api_key": api_key,
                            "enabled": True
                        }
                        ui.print_success(f"✅ 已配置 {engine_info['name']}")
                    else:
                        ui.print_warning("⚠️ API Key 不能为空，跳过配置")
                
                if engine_config:
                    search_config["engines"][engine_key] = engine_config
            
            ui.print_info("")
        
        # 总是启用免费搜索引擎
        search_config["engines"]["duckduckgo"] = {"enabled": True, "default": True}
        search_config["engines"]["searx"] = {"enabled": True}
        
        return search_config
    
    def _configure_task_review(self) -> Dict[str, Any]:
        """配置任务复盘功能"""
        ui.print_section_header("任务复盘功能配置", "📋")
        ui.print_info("任务复盘功能可以在任务完成后自动分析执行结果，")
        ui.print_info("识别问题并提供改进建议。")
        ui.print_info("")
        
        # 询问是否启用复盘功能
        enable_review = ui.get_user_input("是否启用任务复盘功能？(y/N)").lower()
        
        if enable_review not in ['y', 'yes', '是']:
            ui.print_info("已跳过任务复盘功能配置")
            return {"enabled": False}
        
        review_config = {"enabled": True}
        
        # 询问是否自动复盘
        auto_review = ui.get_user_input("是否在任务完成后自动进行复盘？(y/N)").lower()
        review_config["auto_review"] = auto_review in ['y', 'yes', '是']
        
        # 配置复盘阈值
        ui.print_info("")
        ui.print_info("复盘阈值：当任务成功率低于此值时触发复盘（0.0-1.0）")
        while True:
            threshold_input = ui.get_user_input("请输入复盘阈值 (默认: 0.8):")
            if not threshold_input:
                review_config["review_threshold"] = 0.8
                break
            try:
                threshold = float(threshold_input)
                if 0.0 <= threshold <= 1.0:
                    review_config["review_threshold"] = threshold
                    break
                else:
                    ui.print_error("阈值必须在 0.0-1.0 之间")
            except ValueError:
                ui.print_error("请输入有效的数字")
        
        # 配置最大迭代次数
        ui.print_info("")
        ui.print_info("最大迭代次数：复盘改进的最大循环次数")
        while True:
            iterations_input = ui.get_user_input("请输入最大迭代次数 (默认: 3):")
            if not iterations_input:
                review_config["max_iterations"] = 3
                break
            try:
                iterations = int(iterations_input)
                if iterations > 0:
                    review_config["max_iterations"] = iterations
                    break
                else:
                    ui.print_error("迭代次数必须大于 0")
            except ValueError:
                ui.print_error("请输入有效的整数")
        
        ui.print_success("✅ 任务复盘功能配置完成")
        ui.print_info(f"   启用状态: {'是' if review_config['enabled'] else '否'}")
        ui.print_info(f"   自动复盘: {'是' if review_config['auto_review'] else '否'}")
        ui.print_info(f"   复盘阈值: {review_config['review_threshold']}")
        ui.print_info(f"   最大迭代: {review_config['max_iterations']}")
        ui.print_info("")
        
        return review_config
    
    def configure_review_only(self):
        """单独配置复盘功能"""
        ui.print_section_header("复盘功能配置", "🔍")
        
        if not os.path.exists(self.config_path):
            ui.print_error("❌ 配置文件不存在，请先运行 config-wizard 配置基本模型")
            return False
        
        try:
            # 读取现有配置
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
        except Exception as e:
            ui.print_error(f"❌ 读取配置文件失败: {e}")
            return False
        
        # 显示当前复盘配置状态
        current_review = config.get('task_review', {})
        ui.print_info("📋 当前复盘功能状态:")
        ui.print_info(f"   启用状态: {'是' if current_review.get('enabled', False) else '否'}")
        ui.print_info(f"   自动复盘: {'是' if current_review.get('auto_review', False) else '否'}")
        ui.print_info(f"   复盘阈值: {current_review.get('review_threshold', 0.8)}")
        ui.print_info(f"   最大迭代: {current_review.get('max_iterations', 3)}")
        ui.print_info("")
        
        # 配置新的复盘设置
        review_config = self._configure_task_review()
        
        # 更新配置
        config['task_review'] = review_config
        
        # 保存配置
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True, indent=2)
            
            ui.print_success("✅ 复盘功能配置已更新！")
            ui.print_info("")
            ui.print_info("📋 新的复盘功能配置:")
            ui.print_info(f"   启用状态: {'是' if review_config['enabled'] else '否'}")
            ui.print_info(f"   自动复盘: {'是' if review_config.get('auto_review', False) else '否'}")
            ui.print_info(f"   复盘阈值: {review_config.get('review_threshold', 0.8)}")
            ui.print_info(f"   最大迭代: {review_config.get('max_iterations', 3)}")
            return True
        except Exception as e:
            ui.print_error(f"❌ 保存配置失败: {e}")
            return False
    
    def _generate_config(self, models: List[Dict[str, Any]], primary_model: str, search_config: Dict[str, Any] = None, review_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """生成完整配置"""
        config = {
            "models": {
                "primary": primary_model,
                "providers": models
            },
            "tools": {
                "file_system": {"enabled": True},
                "shell": {"enabled": True},
                "system_operations": {"enabled": True},
                "python_analyzer": {"enabled": True},
                "web_search": {"enabled": True}
            },
            "logging": {
                "level": "INFO"
            }
        }
        
        # 只有在提供了review_config时才添加复盘配置
        if review_config is not None:
            config["task_review"] = review_config
        else:
            # 默认的复盘配置（禁用状态）
            config["task_review"] = {
                "enabled": False,
                "auto_review": False,
                "review_threshold": 0.8,
                "max_iterations": 3
            }
        
        # 添加搜索引擎配置
        if search_config and search_config.get("engines"):
            config["search_engines"] = search_config
        else:
            # 默认搜索引擎配置
            config["search_engines"] = {
                "engines": {
                    "duckduckgo": {"enabled": True, "default": True},
                    "searx": {"enabled": True}
                }
            }
        
        return config
    
    def _save_config(self, config: Dict[str, Any]) -> bool:
        """保存配置到文件"""
        try:
            # 确保配置目录存在
            os.makedirs(os.path.dirname(self.config_path) if os.path.dirname(self.config_path) else '.', exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True, indent=2)
            
            ui.print_success(f"✅ 配置已保存到: {self.config_path}")
            return True
        except Exception as e:
            ui.print_error(f"❌ 保存配置失败: {e}")
            return False
    
    def validate_config(self) -> bool:
        """验证配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # 基本结构验证
            if 'models' not in config:
                ui.print_error("配置文件缺少 'models' 部分")
                return False
            
            models_config = config['models']
            if 'providers' not in models_config:
                ui.print_error("配置文件缺少 'providers' 部分")
                return False
            
            if 'primary' not in models_config:
                ui.print_error("配置文件缺少 'primary' 模型设置")
                return False
            
            # 验证每个模型配置
            providers = models_config['providers']
            primary = models_config['primary']
            
            if not any(p.get('alias') == primary for p in providers):
                ui.print_error(f"主模型 '{primary}' 在配置中未找到")
                return False
            
            for provider in providers:
                if not self._validate_provider_config(provider):
                    return False
            
            ui.print_success("✅ 配置文件验证通过")
            return True
            
        except Exception as e:
            ui.print_error(f"❌ 配置文件验证失败: {e}")
            return False
    
    def _validate_provider_config(self, provider: Dict[str, Any]) -> bool:
        """验证单个供应商配置"""
        required_fields = ['alias', 'provider', 'model_name']
        
        for field in required_fields:
            if field not in provider:
                ui.print_error(f"模型配置缺少必需字段: {field}")
                return False
        
        provider_type = provider['provider']
        if provider_type not in self.providers_info:
            ui.print_error(f"不支持的供应商: {provider_type}")
            return False
        
        # 供应商特定验证
        provider_info = self.providers_info[provider_type]
        for field in provider_info['required_fields']:
            if field not in provider:
                ui.print_error(f"{provider_type} 模型配置缺少必需字段: {field}")
                return False
        
        # 验证可选的优先级字段
        if 'priority' in provider:
            priority = provider['priority']
            if not isinstance(priority, int) or not (1 <= priority <= 100):
                ui.print_error(f"模型 {provider.get('alias', '未知')} 的优先级必须是 1-100 之间的整数")
                return False
        
        # 验证能力字段
        if 'capabilities' in provider:
            capabilities = provider['capabilities']
            if not isinstance(capabilities, list):
                ui.print_error(f"模型 {provider.get('alias', '未知')} 的能力字段必须是列表")
                return False
        
        return True
    
    def show_current_config(self):
        """显示当前配置"""
        if not os.path.exists(self.config_path):
            ui.print_warning("配置文件不存在")
            return
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            ui.print_section_header("当前模型配置", "⚙️")
            
            if 'models' in config and 'providers' in config['models']:
                primary = config['models'].get('primary', '未设置')
                ui.print_info(f"🎯 主模型: {primary}")
                ui.print_info("")
                
                for provider in config['models']['providers']:
                    alias = provider.get('alias', '未知')
                    provider_type = provider.get('provider', '未知')
                    model_name = provider.get('model_name', '未知')
                    capabilities = provider.get('capabilities', [])
                    priority = provider.get('priority', 50)
                    
                    ui.print_info(f"🤖 {alias}")
                    ui.print_info(f"   供应商: {provider_type}")
                    ui.print_info(f"   模型: {model_name}")
                    ui.print_info(f"   能力: {', '.join(capabilities)}")
                    ui.print_info(f"   优先级: {priority}")
                    
                    if provider_type == 'ollama' and 'base_url' in provider:
                        ui.print_info(f"   服务器: {provider['base_url']}")
                    
                    ui.print_info("")
            else:
                ui.print_warning("配置文件格式不正确")
            
            # 显示复盘功能配置
            if 'task_review' in config:
                review_config = config['task_review']
                ui.print_info("📋 复盘功能配置:")
                ui.print_info(f"   启用状态: {'是' if review_config.get('enabled', False) else '否'}")
                ui.print_info(f"   自动复盘: {'是' if review_config.get('auto_review', False) else '否'}")
                ui.print_info(f"   复盘阈值: {review_config.get('review_threshold', 0.8)}")
                ui.print_info(f"   最大迭代: {review_config.get('max_iterations', 3)}")
                ui.print_info("")
            else:
                ui.print_info("📋 复盘功能配置:")
                ui.print_info("   启用状态: 否 (未配置)")
                ui.print_info("")
                
        except Exception as e:
            ui.print_error(f"读取配置失败: {e}")
    
    def reconfigure(self):
        """重新配置"""
        ui.print_section_header("重新配置模型", "🔄")
        
        if os.path.exists(self.config_path):
            ui.print_warning("当前配置将被覆盖")
            confirm = ui.get_user_input("确认重新配置？(y/N)").lower()
            if confirm not in ['y', 'yes', '是']:
                ui.print_info("已取消重新配置")
                return False
        
        return self.run_config_wizard() 