"""
搜索引擎配置管理模块
提供独立的搜索引擎配置向导和管理功能
"""

import os
import yaml
from typing import Dict, List, Any, Optional
from ..ui.display import ui
import time

class SearchConfigManager:
    """搜索引擎配置管理器"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.search_engines_info = {
            "google": {
                "name": "Google Custom Search",
                "description": "Google自定义搜索API - 高质量搜索结果",
                "required_fields": ["api_key", "search_engine_id"],
                "setup_url": "https://console.cloud.google.com/",
                "enabled": False
            },
            "bing": {
                "name": "Bing Search API",
                "description": "微软Bing搜索API - 集成微软生态",
                "required_fields": ["api_key"],
                "setup_url": "https://portal.azure.com/",
                "enabled": False
            },
            "duckduckgo": {
                "name": "DuckDuckGo",
                "description": "DuckDuckGo免费搜索 - 注重隐私保护",
                "required_fields": [],
                "enabled": True,
                "default": True,
                "free": True
            },
            "searx": {
                "name": "SearX",
                "description": "SearX开源搜索引擎 - 聚合多个搜索源",
                "required_fields": [],
                "enabled": True,
                "free": True
            }
        }
    
    def run_config_wizard(self):
        """运行搜索配置向导"""
        print("\n🔍 IntelliCLI 搜索引擎配置向导")
        print("=" * 50)
        
        while True:
            print("\n请选择操作:")
            print("1. 查看搜索引擎状态")
            print("2. 配置搜索引擎")
            print("3. 测试搜索功能")
            print("4. 重置搜索配置")
            print("5. 退出")
            
            choice = input("\n请选择 (1-5): ").strip()
            
            if choice == "1":
                self._show_search_status()
                input("\n按回车键继续...")
            elif choice == "2":
                self._configure_search_engines()
            elif choice == "3":
                self._test_search()
            elif choice == "4":
                self._reset_search_config()
            elif choice == "5":
                print("\n👋 配置完成！")
                break
            else:
                print("❌ 无效选择，请重试")
                time.sleep(1)
    
    def _show_current_status(self):
        """显示当前配置状态"""
        ui.print_section_header("当前搜索引擎状态", "📊")
        
        current_config = self._load_current_config()
        
        for engine_key, engine_info in self.search_engines_info.items():
            engine_config = current_config.get(engine_key, {})
            is_configured = engine_config.get("enabled", False)
            
            if engine_info.get("free"):
                status = "✅ 免费可用"
            elif is_configured:
                status = "✅ 已配置"
            else:
                status = "❌ 未配置"
            
            ui.print_info(f"• {engine_info['name']}: {status}")
            ui.print_info(f"  {engine_info['description']}")
            
            if engine_info.get("required_fields") and not is_configured:
                ui.print_info(f"  需要配置: {', '.join(engine_info['required_fields'])}")
        
        ui.print_info("")
    
    def _configure_google(self):
        """配置Google搜索"""
        ui.print_section_header("配置 Google Custom Search", "🔧")
        ui.print_info("Google Custom Search 提供高质量的搜索结果")
        ui.print_info("配置步骤:")
        ui.print_info("1. 访问 https://console.cloud.google.com/")
        ui.print_info("2. 创建项目或选择现有项目")
        ui.print_info("3. 启用 Custom Search API")
        ui.print_info("4. 创建 API 密钥")
        ui.print_info("5. 在 https://cse.google.com/ 创建自定义搜索引擎")
        ui.print_info("")
        
        api_key = ui.get_user_input("请输入 Google Search API Key (留空跳过):")
        if not api_key:
            ui.print_info("跳过 Google 搜索配置")
            return
        
        search_engine_id = ui.get_user_input("请输入 Custom Search Engine ID:")
        if not search_engine_id:
            ui.print_warning("Custom Search Engine ID 不能为空，配置取消")
            return
        
        # 保存配置
        self._save_engine_config("google", {
            "enabled": True,
            "api_key": api_key,
            "search_engine_id": search_engine_id
        })
        
        ui.print_success("✅ Google 搜索配置完成！")
    
    def _configure_bing(self):
        """配置Bing搜索"""
        ui.print_section_header("配置 Bing Search API", "🔧")
        ui.print_info("Bing Search API 与微软生态系统集成")
        ui.print_info("配置步骤:")
        ui.print_info("1. 访问 https://portal.azure.com/")
        ui.print_info("2. 创建 Bing Search v7 资源")
        ui.print_info("3. 获取 API 密钥")
        ui.print_info("")
        
        api_key = ui.get_user_input("请输入 Bing Search API Key (留空跳过):")
        if not api_key:
            ui.print_info("跳过 Bing 搜索配置")
            return
        
        # 保存配置
        self._save_engine_config("bing", {
            "enabled": True,
            "api_key": api_key
        })
        
        ui.print_success("✅ Bing 搜索配置完成！")
    
    def _show_all_engines_status(self):
        """显示所有搜索引擎的详细状态"""
        ui.print_section_header("搜索引擎详细状态", "📋")
        
        from ..tools.web_search import check_search_config
        config_status = check_search_config()
        
        for engine, info in config_status.items():
            status_icon = "✅" if info["available"] else "❌"
            ui.print_info(f"{status_icon} {engine.upper()}")
            ui.print_info(f"   状态: {'可用' if info['available'] else '不可用'}")
            ui.print_info(f"   说明: {info['note']}")
            ui.print_info(f"   配置来源: {info['source']}")
            ui.print_info("")
    
    def _show_search_status(self):
        """显示搜索引擎状态"""
        from ..tools.web_search import check_search_config
        
        print("\n🔍 搜索引擎配置状态")
        print("=" * 50)
        
        config_status = check_search_config()
        
        for engine, info in config_status.items():
            status = "✅ 可用" if info["available"] else "❌ 不可用"
            engine_name = {
                "duckduckgo": "DuckDuckGo",
                "google": "Google",
                "bing": "Bing",
                "searx": "SearX",
                "yahoo": "Yahoo",
                "startpage": "Startpage"
            }.get(engine, engine.title())
            
            print(f"{engine_name:12} {status:8} - {info['note']}")
            print(f"{'':12} {'':8}   来源: {info['source']}")
            print()
        
        print("💡 提示:")
        print("- DuckDuckGo、Yahoo、Startpage 和 SearX 是免费搜索引擎")
        print("- Google 和 Bing 需要 API 密钥，但提供更准确的结果")
        print("- 使用 'search-config' 命令可以配置 API 密钥")
        print()

    def _configure_search_engines(self):
        """配置搜索引擎"""
        print("\n🔧 搜索引擎配置")
        print("=" * 50)
        
        # 显示当前状态
        self._show_search_status()
        
        print("可配置的搜索引擎:")
        print("1. Google (需要 API Key)")
        print("2. Bing (需要 API Key)")
        print("3. 查看免费搜索引擎")
        print("4. 测试搜索功能")
        print("5. 返回主菜单")
        
        choice = input("\n请选择 (1-5): ").strip()
        
        if choice == "1":
            self._configure_google()
        elif choice == "2":
            self._configure_bing()
        elif choice == "3":
            self._show_free_engines()
        elif choice == "4":
            self._test_search()
        elif choice == "5":
            return
        else:
            print("❌ 无效选择")
            time.sleep(1)
            self._configure_search_engines()

    def _show_free_engines(self):
        """显示免费搜索引擎信息"""
        print("\n🆓 免费搜索引擎")
        print("=" * 50)
        
        engines = [
            {
                "name": "DuckDuckGo",
                "description": "隐私保护搜索引擎，无需配置",
                "features": ["隐私保护", "无广告", "全球搜索"],
                "url": "https://duckduckgo.com"
            },
            {
                "name": "Yahoo",
                "description": "老牌搜索引擎，免费使用",
                "features": ["新闻搜索", "图片搜索", "全面搜索"],
                "url": "https://search.yahoo.com"
            },
            {
                "name": "Startpage",
                "description": "匿名搜索，保护隐私",
                "features": ["匿名搜索", "Google结果", "隐私保护"],
                "url": "https://www.startpage.com"
            },
            {
                "name": "SearX",
                "description": "开源搜索引擎，聚合多个搜索源",
                "features": ["开源", "聚合搜索", "可自定义"],
                "url": "https://searx.org"
            }
        ]
        
        for engine in engines:
            print(f"🔍 {engine['name']}")
            print(f"   描述: {engine['description']}")
            print(f"   特性: {', '.join(engine['features'])}")
            print(f"   网址: {engine['url']}")
            print()
        
        print("💡 这些搜索引擎都已内置支持，无需额外配置！")
        print("   您可以直接使用 IntelliCLI 的搜索功能。")
        
        input("\n按回车键继续...")
        self._configure_search_engines()

    def _test_search(self):
        """测试搜索功能"""
        print("\n🧪 搜索功能测试")
        print("=" * 50)
        
        from ..tools.web_search import web_search
        
        test_query = input("请输入测试查询 (默认: 'Python编程'): ").strip()
        if not test_query:
            test_query = "Python编程"
        
        print(f"\n正在测试搜索: {test_query}")
        print("=" * 30)
        
        # 测试可用的搜索引擎
        engines_to_test = ["duckduckgo", "yahoo", "startpage"]
        
        for engine in engines_to_test:
            print(f"\n🔍 测试 {engine.title()}...")
            try:
                result = web_search(test_query, search_engine=engine, max_results=2)
                
                if "error" in result:
                    print(f"❌ {engine.title()} 测试失败: {result['error']}")
                else:
                    print(f"✅ {engine.title()} 测试成功")
                    print(f"   找到 {result.get('total_results', 0)} 个结果")
                    if result.get('results'):
                        first_result = result['results'][0]
                        print(f"   标题: {first_result.get('title', 'N/A')[:50]}...")
                        
            except Exception as e:
                print(f"❌ {engine.title()} 测试出错: {e}")
        
        input("\n按回车键继续...")
        self._configure_search_engines()
    
    def _reset_search_config(self):
        """重置搜索配置"""
        ui.print_section_header("重置搜索配置", "🔄")
        ui.print_warning("这将删除所有已配置的搜索引擎设置")
        
        confirm = ui.get_user_input("确认重置搜索配置？(y/N)").lower()
        if confirm in ['y', 'yes', '是']:
            # 重置为默认配置
            default_config = {
                "duckduckgo": {"enabled": True, "default": True},
                "searx": {"enabled": True}
            }
            
            self._save_search_config(default_config)
            ui.print_success("✅ 搜索配置已重置为默认设置")
        else:
            ui.print_info("取消重置操作")
    
    def _load_current_config(self) -> Dict[str, Any]:
        """加载当前搜索配置"""
        if not os.path.exists(self.config_path):
            return {}
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f) or {}
            return config.get("search_engines", {}).get("engines", {})
        except Exception:
            return {}
    
    def _save_engine_config(self, engine: str, config: Dict[str, Any]):
        """保存单个搜索引擎配置"""
        # 加载完整配置
        full_config = {}
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    full_config = yaml.safe_load(f) or {}
            except Exception:
                pass
        
        # 确保搜索引擎配置结构存在
        if "search_engines" not in full_config:
            full_config["search_engines"] = {"engines": {}}
        if "engines" not in full_config["search_engines"]:
            full_config["search_engines"]["engines"] = {}
        
        # 更新指定引擎配置
        full_config["search_engines"]["engines"][engine] = config
        
        # 保存配置
        self._save_full_config(full_config)
    
    def _save_search_config(self, search_config: Dict[str, Any]):
        """保存完整搜索配置"""
        # 加载完整配置
        full_config = {}
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    full_config = yaml.safe_load(f) or {}
            except Exception:
                pass
        
        # 更新搜索引擎配置
        full_config["search_engines"] = {"engines": search_config}
        
        # 保存配置
        self._save_full_config(full_config)
    
    def _save_full_config(self, config: Dict[str, Any]):
        """保存完整配置到文件"""
        try:
            # 确保配置目录存在
            os.makedirs(os.path.dirname(self.config_path) if os.path.dirname(self.config_path) else '.', exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True, indent=2)
        except Exception as e:
            ui.print_error(f"❌ 保存配置失败: {e}")
    
    def show_search_config(self):
        """显示当前搜索配置"""
        ui.print_section_header("搜索引擎配置", "🔍")
        
        from ..tools.web_search import check_search_config
        config_status = check_search_config()
        
        for engine, info in config_status.items():
            status_icon = "✅" if info["available"] else "❌"
            engine_name = {
                "duckduckgo": "DuckDuckGo",
                "google": "Google",
                "bing": "Bing",
                "searx": "SearX",
                "yahoo": "Yahoo",
                "startpage": "Startpage"
            }.get(engine, engine.title())
            
            ui.print_info(f"{status_icon} {engine_name}")
            ui.print_info(f"   状态: {'可用' if info['available'] else '不可用'}")
            ui.print_info(f"   说明: {info['note']}")
            ui.print_info(f"   配置来源: {info['source']}")
            ui.print_info("")
    
    def has_valid_search_config(self) -> bool:
        """检查是否有有效的搜索配置"""
        current_config = self._load_current_config()
        
        # 至少需要有一个启用的搜索引擎
        return any(config.get("enabled", False) for config in current_config.values())

# 全局搜索配置管理器实例
search_config_manager = SearchConfigManager() 