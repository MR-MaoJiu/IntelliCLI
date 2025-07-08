"""
网络搜索工具模块
支持多种搜索引擎的网络搜索功能，具备智能切换和回退机制
"""

import os
import yaml
import requests
import re
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

# 搜索引擎健康状态管理
class SearchEngineHealth:
    """搜索引擎健康状态管理器"""
    
    def __init__(self):
        self.health_status = {}
        self.failure_counts = {}
        self.last_success = {}
        self.blacklist_until = {}
    
    def record_success(self, engine: str):
        """记录搜索成功"""
        self.health_status[engine] = True
        self.failure_counts[engine] = 0
        self.last_success[engine] = datetime.now()
        # 移除黑名单
        if engine in self.blacklist_until:
            del self.blacklist_until[engine]
    
    def record_failure(self, engine: str):
        """记录搜索失败"""
        self.failure_counts[engine] = self.failure_counts.get(engine, 0) + 1
        self.health_status[engine] = False
        
        # 连续失败3次后加入黑名单5分钟
        if self.failure_counts[engine] >= 3:
            self.blacklist_until[engine] = datetime.now() + timedelta(minutes=5)
    
    def is_available(self, engine: str) -> bool:
        """检查引擎是否可用"""
        # 检查是否在黑名单中
        if engine in self.blacklist_until:
            if datetime.now() < self.blacklist_until[engine]:
                return False
            else:
                # 黑名单过期，移除
                del self.blacklist_until[engine]
        
        return True
    
    def get_engine_priority(self, engine: str) -> int:
        """获取引擎优先级（数字越小优先级越高）"""
        # 基础优先级
        base_priority = {
            "yahoo": 1,      # 当前最可靠
            "google": 2,     # 需要API但很可靠
            "bing": 3,       # 需要API
            "duckduckgo": 4, # 受限制
            "startpage": 5,  # 受限制
            "searx": 6       # 不稳定
        }.get(engine, 10)
        
        # 根据失败次数调整优先级
        failure_penalty = self.failure_counts.get(engine, 0) * 2
        
        # 根据最后成功时间调整优先级
        time_penalty = 0
        if engine in self.last_success:
            hours_since_success = (datetime.now() - self.last_success[engine]).total_seconds() / 3600
            time_penalty = int(hours_since_success / 24)  # 每天增加1点优先级惩罚
        
        return base_priority + failure_penalty + time_penalty

# 全局健康状态管理器
search_health = SearchEngineHealth()

def _load_search_config() -> Dict[str, Any]:
    """加载搜索引擎配置"""
    config_path = "config.yaml"
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f) or {}
            return config.get("search_engines", {}).get("engines", {})
        except Exception:
            return {}
    return {}

def _get_api_key(engine: str, config_key: str, env_var: str = None) -> Optional[str]:
    """获取API密钥，优先从配置文件读取，然后从环境变量"""
    # 首先尝试从配置文件获取
    config = _load_search_config()
    engine_config = config.get(engine, {})
    if engine_config.get(config_key):
        return engine_config[config_key]
    
    # 然后尝试从环境变量获取
    if env_var:
        return os.getenv(env_var)
    
    return None

def get_available_engines() -> List[str]:
    """获取当前可用的搜索引擎列表，按优先级排序"""
    config_status = check_search_config()
    available_engines = []
    
    for engine, info in config_status.items():
        if info["available"] and search_health.is_available(engine):
            available_engines.append(engine)
    
    # 按优先级排序
    available_engines.sort(key=lambda x: search_health.get_engine_priority(x))
    
    return available_engines

def web_search(query: str, search_engine: str = "auto", max_results: int = 5, lang: str = "zh-cn") -> Dict[str, Any]:
    """
    执行网络搜索并返回结果，支持智能引擎切换
    
    Args:
        query: 搜索查询关键词
        search_engine: 搜索引擎 ("auto", "duckduckgo", "google", "bing", "searx", "yahoo", "startpage")
        max_results: 最大结果数量
        lang: 语言代码
    
    Returns:
        包含搜索结果的字典
    """
    if not query or not query.strip():
        return {"error": "搜索查询不能为空"}
    
    query = query.strip()
    max_results = max(1, min(max_results, 20))
    
    # 获取可用引擎列表
    available_engines = get_available_engines()
    
    if not available_engines:
        return {"error": "当前没有可用的搜索引擎"}
    
    # 确定要尝试的引擎列表
    engines_to_try = []
    
    if search_engine == "auto":
        # 自动模式：尝试所有可用引擎
        engines_to_try = available_engines
        print(f"🔍 自动搜索模式，将按优先级尝试: {', '.join(engines_to_try)}")
    else:
        # 指定引擎模式：首先尝试指定引擎，失败后尝试其他引擎
        if search_engine in available_engines:
            engines_to_try = [search_engine] + [e for e in available_engines if e != search_engine]
        else:
            engines_to_try = available_engines
            print(f"⚠️ 指定的搜索引擎 {search_engine} 不可用，自动切换到可用引擎")
    
    # 尝试每个引擎
    last_error = None
    for i, engine in enumerate(engines_to_try):
        try:
            print(f"🔍 尝试搜索引擎: {engine} ({i+1}/{len(engines_to_try)})")
            
            # 执行搜索
            result = _execute_search(engine, query, max_results, lang)
            
            if "error" not in result and result.get("total_results", 0) > 0:
                # 搜索成功
                search_health.record_success(engine)
                result["search_info"] = {
                    "engine_used": engine,
                    "attempt_number": i + 1,
                    "total_attempts": len(engines_to_try),
                    "auto_switched": i > 0 or search_engine == "auto"
                }
                print(f"✅ 搜索成功，使用引擎: {engine}")
                return result
            else:
                # 搜索失败
                search_health.record_failure(engine)
                last_error = result.get("error", "未知错误")
                print(f"❌ {engine} 搜索失败: {last_error}")
                
                # 如果不是最后一个引擎，继续尝试下一个
                if i < len(engines_to_try) - 1:
                    print(f"🔄 切换到下一个搜索引擎...")
                    time.sleep(1)  # 短暂延迟避免过快请求
                    continue
                
        except Exception as e:
            search_health.record_failure(engine)
            last_error = str(e)
            print(f"❌ {engine} 搜索异常: {last_error}")
            
            if i < len(engines_to_try) - 1:
                print(f"🔄 切换到下一个搜索引擎...")
                time.sleep(1)
                continue
    
    # 所有引擎都失败了
    return {
        "error": f"所有搜索引擎都无法使用。最后错误: {last_error}",
        "search_info": {
            "engines_tried": engines_to_try,
            "total_attempts": len(engines_to_try),
            "all_failed": True
        }
    }

def _execute_search(engine: str, query: str, max_results: int, lang: str) -> Dict[str, Any]:
    """执行具体的搜索操作"""
    try:
        if engine == "duckduckgo":
            return _search_duckduckgo(query, max_results, lang)
        elif engine == "google":
            return _search_google(query, max_results, lang)
        elif engine == "bing":
            return _search_bing(query, max_results, lang)
        elif engine == "searx":
            return _search_searx(query, max_results, lang)
        elif engine == "yahoo":
            return _search_yahoo(query, max_results, lang)
        elif engine == "startpage":
            return _search_startpage(query, max_results, lang)
        else:
            return {"error": f"不支持的搜索引擎: {engine}"}
    except Exception as e:
        return {"error": f"搜索过程中出错: {str(e)}"}

def _search_duckduckgo(query: str, max_results: int, lang: str) -> Dict[str, Any]:
    """DuckDuckGo搜索 - 使用多种方法"""
    # 首先尝试官方API
    try:
        api_result = _search_duckduckgo_api(query, max_results, lang)
        if "error" not in api_result and api_result.get("total_results", 0) > 0:
            return api_result
    except Exception as e:
        print(f"DuckDuckGo API搜索失败: {e}")
    
    # 然后尝试HTML搜索
    try:
        html_result = _search_duckduckgo_html(query, max_results, lang)
        if "error" not in html_result and html_result.get("total_results", 0) > 0:
            return html_result
    except Exception as e:
        print(f"DuckDuckGo HTML搜索失败: {e}")
    
    # 最后尝试Lite版本搜索
    try:
        lite_result = _search_duckduckgo_lite(query, max_results, lang)
        if "error" not in lite_result and lite_result.get("total_results", 0) > 0:
            return lite_result
    except Exception as e:
        print(f"DuckDuckGo Lite搜索失败: {e}")
    
    # 所有方法都失败了
    return {"error": "DuckDuckGo搜索失败：所有搜索方法都无法访问或返回结果"}

def _search_duckduckgo_api(query: str, max_results: int, lang: str) -> Dict[str, Any]:
    """使用DuckDuckGo的Instant Answer API"""
    try:
        search_url = "https://api.duckduckgo.com/"
        params = {
            "q": query,
            "format": "json",
            "no_html": "1",
            "skip_disambig": "1",
            "no_redirect": "1"
        }
        
        response = requests.get(search_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = []
        
        # 处理即时答案
        if data.get("AbstractText"):
            results.append({
                "title": data.get("Heading", "DuckDuckGo即时答案"),
                "snippet": data.get("AbstractText"),
                "url": data.get("AbstractURL", ""),
                "source": "DuckDuckGo即时答案"
            })
        
        # 处理相关主题
        if data.get("RelatedTopics"):
            for topic in data.get("RelatedTopics", [])[:max_results-len(results)]:
                if isinstance(topic, dict) and topic.get("Text"):
                    results.append({
                        "title": topic.get("FirstURL", "").split("/")[-1].replace("_", " "),
                        "snippet": topic.get("Text"),
                        "url": topic.get("FirstURL", ""),
                        "source": "DuckDuckGo相关主题"
                    })
        
        return {
            "query": query,
            "search_engine": "DuckDuckGo API",
            "total_results": len(results),
            "results": results[:max_results]
        }
        
    except Exception as e:
        return {"error": f"DuckDuckGo API搜索失败: {str(e)}"}

def _search_duckduckgo_html(query: str, max_results: int, lang: str) -> Dict[str, Any]:
    """DuckDuckGo HTML搜索方法 - 真实搜索实现"""
    try:
        from bs4 import BeautifulSoup
        
        # 使用DuckDuckGo的HTML版本，绕过JavaScript
        search_url = "https://html.duckduckgo.com/html/"
        
        # 构建POST请求数据
        data = {
            "q": query,
            "b": "",  # 起始结果编号
            "kl": "cn-zh" if lang.startswith("zh") else "us-en"
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": "https://duckduckgo.com/"
        }
        
        # 发送POST请求到HTML版本
        response = requests.post(search_url, data=data, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        results = []
        
        # DuckDuckGo HTML版本的搜索结果结构
        # 查找搜索结果链接
        result_links = soup.find_all('a', class_='result__a')
        
        for link in result_links:
            try:
                title = link.get_text().strip()
                url = link.get('href')
                
                if not title or not url or len(title) < 3:
                    continue
                
                # 查找对应的描述
                snippet = ""
                # 尝试找到这个链接所在的结果容器
                result_container = link.find_parent(['div'], class_=re.compile(r'result'))
                if result_container:
                    snippet_elem = result_container.find(['a'], class_='result__snippet')
                    if snippet_elem:
                        snippet = snippet_elem.get_text().strip()
                
                if not snippet:
                    snippet = f"来自 {url} 的搜索结果"
                
                results.append({
                    "title": title,
                    "snippet": snippet,
                    "url": url,
                    "source": "DuckDuckGo"
                })
                
                if len(results) >= max_results:
                    break
                    
            except Exception as e:
                continue
        
        if not results:
            return {"error": "DuckDuckGo HTML搜索未返回任何结果"}
        
        return {
            "query": query,
            "search_engine": "DuckDuckGo",
            "total_results": len(results),
            "results": results
        }
        
    except ImportError:
        return {"error": "需要安装beautifulsoup4库: pip install beautifulsoup4"}
    except requests.exceptions.RequestException as e:
        return {"error": f"DuckDuckGo网络请求失败: {str(e)}"}
    except Exception as e:
        return {"error": f"DuckDuckGo HTML搜索失败: {str(e)}"}

def _search_duckduckgo_lite(query: str, max_results: int, lang: str) -> Dict[str, Any]:
    """DuckDuckGo Lite搜索 - 备用方法"""
    try:
        from bs4 import BeautifulSoup
        
        # 直接使用DuckDuckGo的搜索API端点
        search_url = "https://duckduckgo.com/html/"
        
        # 使用GET请求
        params = {
            "q": query,
            "kl": "cn-zh" if lang.startswith("zh") else "us-en",
            "s": "0",  # 起始位置
            "dc": str(max_results)  # 结果数量
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Referer": "https://duckduckgo.com/"
        }
        
        response = requests.get(search_url, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        results = []
        
        # 查找结果链接 - 使用更通用的选择器
        result_links = soup.find_all('a', href=True)
        
        for link in result_links:
            try:
                href = link.get('href')
                title = link.get_text().strip()
                
                # 过滤掉导航链接和无效链接
                if (not href or not title or 
                    href.startswith('/') or 
                    href.startswith('#') or
                    'duckduckgo.com' in href or
                    len(title) < 5 or
                    title in ['DuckDuckGo', 'Settings', 'Privacy', 'Terms']):
                    continue
                
                # 查找描述
                snippet = ""
                parent = link.find_parent(['div', 'td', 'tr'])
                if parent:
                    # 获取父容器的所有文本
                    all_text = parent.get_text()
                    text_parts = [part.strip() for part in all_text.split('\n') if part.strip()]
                    
                    # 找到标题后的描述文本
                    for i, part in enumerate(text_parts):
                        if title in part and i + 1 < len(text_parts):
                            next_part = text_parts[i + 1]
                            if len(next_part) > 20 and next_part != title:
                                snippet = next_part[:300]
                                break
                
                if not snippet:
                    snippet = f"来自 {href} 的搜索结果"
                
                results.append({
                    "title": title,
                    "snippet": snippet,
                    "url": href,
                    "source": "DuckDuckGo"
                })
                
                if len(results) >= max_results:
                    break
                    
            except Exception as e:
                continue
        
        if not results:
            return {"error": "DuckDuckGo Lite搜索未返回任何有效结果"}
        
        return {
            "query": query,
            "search_engine": "DuckDuckGo Lite",
            "total_results": len(results),
            "results": results
        }
        
    except ImportError:
        return {"error": "需要安装beautifulsoup4库: pip install beautifulsoup4"}
    except requests.exceptions.RequestException as e:
        return {"error": f"DuckDuckGo Lite网络请求失败: {str(e)}"}
    except Exception as e:
        return {"error": f"DuckDuckGo Lite搜索失败: {str(e)}"}

def _search_yahoo(query: str, max_results: int, lang: str) -> Dict[str, Any]:
    """Yahoo搜索 - 真实搜索实现"""
    try:
        from bs4 import BeautifulSoup
        
        search_url = "https://search.yahoo.com/search"
        params = {
            "p": query,
            "ei": "UTF-8",
            "fl": "0",
            "vl": "lang_" + ("zh-cn" if lang.startswith("zh") else "en")
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Referer": "https://search.yahoo.com/"
        }
        
        response = requests.get(search_url, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        results = []
        
        # Yahoo搜索结果通常在特定的CSS选择器中
        result_containers = soup.find_all(['div'], class_=re.compile(r'algo|result'))
        
        for container in result_containers:
            try:
                # 查找标题链接
                title_link = container.find('a', href=True)
                if not title_link:
                    continue
                
                title = title_link.get_text().strip()
                url = title_link.get('href')
                
                if not title or not url:
                    continue
                
                # 查找描述
                snippet = ""
                snippet_elem = container.find(['p', 'div'], class_=re.compile(r'compText|abstract'))
                if snippet_elem:
                    snippet = snippet_elem.get_text().strip()
                
                if not snippet:
                    snippet = f"来自 {url} 的Yahoo搜索结果"
                
                results.append({
                    "title": title,
                    "snippet": snippet,
                    "url": url,
                    "source": "Yahoo"
                })
                
                if len(results) >= max_results:
                    break
                    
            except Exception as e:
                continue
        
        if not results:
            return {"error": "Yahoo搜索未返回任何结果"}
        
        return {
            "query": query,
            "search_engine": "Yahoo",
            "total_results": len(results),
            "results": results
        }
        
    except ImportError:
        return {"error": "需要安装beautifulsoup4库: pip install beautifulsoup4"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Yahoo搜索网络请求失败: {str(e)}"}
    except Exception as e:
        return {"error": f"Yahoo搜索失败: {str(e)}"}

def _search_startpage(query: str, max_results: int, lang: str) -> Dict[str, Any]:
    """Startpage搜索 - 真实搜索实现"""
    try:
        from bs4 import BeautifulSoup
        
        search_url = "https://www.startpage.com/sp/search"
        params = {
            "query": query,
            "language": "chinese" if lang.startswith("zh") else "english",
            "family_filter": "off"
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Referer": "https://www.startpage.com/"
        }
        
        response = requests.get(search_url, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        results = []
        
        # Startpage搜索结果结构
        result_containers = soup.find_all(['div'], class_=re.compile(r'w-gl__result'))
        
        for container in result_containers:
            try:
                # 查找标题链接
                title_link = container.find('a', href=True)
                if not title_link:
                    continue
                
                title = title_link.get_text().strip()
                url = title_link.get('href')
                
                if not title or not url:
                    continue
                
                # 查找描述
                snippet = ""
                snippet_elem = container.find(['p', 'div'], class_=re.compile(r'w-gl__description'))
                if snippet_elem:
                    snippet = snippet_elem.get_text().strip()
                
                if not snippet:
                    snippet = f"来自 {url} 的Startpage搜索结果"
                
                results.append({
                    "title": title,
                    "snippet": snippet,
                    "url": url,
                    "source": "Startpage"
                })
                
                if len(results) >= max_results:
                    break
                    
            except Exception as e:
                continue
        
        if not results:
            return {"error": "Startpage搜索未返回任何结果"}
        
        return {
            "query": query,
            "search_engine": "Startpage",
            "total_results": len(results),
            "results": results
        }
        
    except ImportError:
        return {"error": "需要安装beautifulsoup4库: pip install beautifulsoup4"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Startpage搜索网络请求失败: {str(e)}"}
    except Exception as e:
        return {"error": f"Startpage搜索失败: {str(e)}"}

def _search_google(query: str, max_results: int, lang: str) -> Dict[str, Any]:
    """使用Google Custom Search API"""
    api_key = _get_api_key("google", "api_key", "GOOGLE_SEARCH_API_KEY")
    search_engine_id = _get_api_key("google", "search_engine_id", "GOOGLE_SEARCH_ENGINE_ID")
    
    if not api_key or not search_engine_id:
        return {
            "error": "Google搜索需要配置API密钥和搜索引擎ID。请在配置向导中设置或使用环境变量: GOOGLE_SEARCH_API_KEY 和 GOOGLE_SEARCH_ENGINE_ID"
        }
    
    try:
        search_url = "https://customsearch.googleapis.com/customsearch/v1"
        params = {
            "key": api_key,
            "cx": search_engine_id,
            "q": query,
            "num": min(max_results, 10),
            "lr": f"lang_{lang.split('-')[0]}" if lang else "lang_zh"
        }
        
        response = requests.get(search_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = []
        if "items" in data:
            for item in data["items"]:
                results.append({
                    "title": item.get("title", ""),
                    "snippet": item.get("snippet", ""),
                    "url": item.get("link", ""),
                    "source": "Google"
                })
        
        return {
            "query": query,
            "search_engine": "Google",
            "total_results": len(results),
            "estimated_total": data.get("searchInformation", {}).get("totalResults", "未知"),
            "results": results
        }
        
    except Exception as e:
        return {"error": f"Google搜索失败: {str(e)}"}

def _search_bing(query: str, max_results: int, lang: str) -> Dict[str, Any]:
    """使用Bing Search API"""
    api_key = _get_api_key("bing", "api_key", "BING_SEARCH_API_KEY")
    
    if not api_key:
        return {"error": "Bing搜索需要配置API密钥。请在配置向导中设置或使用环境变量: BING_SEARCH_API_KEY"}
    
    try:
        search_url = "https://api.bing.microsoft.com/v7.0/search"
        headers = {"Ocp-Apim-Subscription-Key": api_key}
        params = {
            "q": query,
            "count": min(max_results, 20),
            "mkt": "zh-CN" if lang.startswith("zh") else "en-US"
        }
        
        response = requests.get(search_url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = []
        if "webPages" in data and "value" in data["webPages"]:
            for item in data["webPages"]["value"]:
                results.append({
                    "title": item.get("name", ""),
                    "snippet": item.get("snippet", ""),
                    "url": item.get("url", ""),
                    "source": "Bing"
                })
        
        return {
            "query": query,
            "search_engine": "Bing",
            "total_results": len(results),
            "estimated_total": data.get("webPages", {}).get("totalEstimatedMatches", "未知"),
            "results": results
        }
        
    except Exception as e:
        return {"error": f"Bing搜索失败: {str(e)}"}

def _search_searx(query: str, max_results: int, lang: str) -> Dict[str, Any]:
    """使用SearX开源搜索引擎"""
    # 使用公开的SearX实例
    searx_instances = [
        "https://searx.be",
        "https://search.sapti.me",
        "https://searx.xyz",
        "https://searx.tiekoetter.com"
    ]
    
    for instance in searx_instances:
        try:
            search_url = f"{instance}/search"
            params = {
                "q": query,
                "format": "json",
                "language": lang,
                "pageno": 1
            }
            
            response = requests.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = []
            if "results" in data:
                for item in data["results"][:max_results]:
                    results.append({
                        "title": item.get("title", ""),
                        "snippet": item.get("content", ""),
                        "url": item.get("url", ""),
                        "source": f"SearX ({instance})"
                    })
            
            return {
                "query": query,
                "search_engine": f"SearX ({instance})",
                "total_results": len(results),
                "results": results
            }
            
        except Exception:
            continue  # 尝试下一个实例
    
    return {"error": "所有SearX实例都无法访问"}

def quick_search(query: str, max_results: int = 3) -> str:
    """
    快速搜索，返回格式化的文本结果
    
    Args:
        query: 搜索查询
        max_results: 最大结果数量
    
    Returns:
        格式化的搜索结果文本
    """
    result = web_search(query, max_results=max_results)
    
    if "error" in result:
        return f"搜索出错: {result['error']}"
    
    if not result.get("results"):
        return f"没有找到关于 '{query}' 的搜索结果"
    
    output = [f"🔍 搜索结果 - '{query}' (共{result['total_results']}条)"]
    output.append("=" * 50)
    
    for i, item in enumerate(result["results"], 1):
        output.append(f"\n{i}. {item['title']}")
        output.append(f"   {item['snippet']}")
        output.append(f"   🔗 {item['url']}")
        if item.get("source"):
            output.append(f"   📰 来源: {item['source']}")
    
    return "\n".join(output)

def search_news(query: str, max_results: int = 5) -> Dict[str, Any]:
    """
    搜索新闻信息
    
    Args:
        query: 新闻查询关键词
        max_results: 最大结果数量
    
    Returns:
        新闻搜索结果
    """
    # 添加新闻相关的搜索词
    news_query = f"{query} 新闻 最新"
    return web_search(news_query, max_results=max_results)

def search_academic(query: str, max_results: int = 5) -> Dict[str, Any]:
    """
    搜索学术信息
    
    Args:
        query: 学术查询关键词
        max_results: 最大结果数量
    
    Returns:
        学术搜索结果
    """
    # 添加学术相关的搜索词
    academic_query = f"{query} 研究 论文 学术"
    return web_search(academic_query, max_results=max_results)

def get_search_engines() -> List[str]:
    """
    获取支持的搜索引擎列表
    
    Returns:
        支持的搜索引擎名称列表
    """
    return ["duckduckgo", "google", "bing", "searx"]

def check_search_config() -> Dict[str, Any]:
    """
    检查搜索配置状态，结合健康状态管理
    
    Returns:
        配置状态信息
    """
    config_status = {}
    
    # DuckDuckGo - 由于反爬虫机制，实际可用性有限
    duckduckgo_available = search_health.is_available("duckduckgo")
    config_status["duckduckgo"] = {
        "available": duckduckgo_available,
        "note": "免费搜索引擎，但受反爬虫机制限制" + ("，当前被暂时禁用" if not duckduckgo_available else ""),
        "source": "内置支持（受限）",
        "priority": search_health.get_engine_priority("duckduckgo"),
        "failure_count": search_health.failure_counts.get("duckduckgo", 0)
    }
    
    # Yahoo - 实际测试可用
    yahoo_available = search_health.is_available("yahoo")
    config_status["yahoo"] = {
        "available": yahoo_available,
        "note": "Yahoo免费搜索引擎，实际可用" + ("，当前被暂时禁用" if not yahoo_available else ""),
        "source": "内置支持",
        "priority": search_health.get_engine_priority("yahoo"),
        "failure_count": search_health.failure_counts.get("yahoo", 0)
    }
    
    # Startpage - 受限制
    startpage_available = search_health.is_available("startpage")
    config_status["startpage"] = {
        "available": startpage_available,
        "note": "隐私保护搜索引擎，受访问限制" + ("，当前被暂时禁用" if not startpage_available else ""),
        "source": "内置支持（受限）",
        "priority": search_health.get_engine_priority("startpage"),
        "failure_count": search_health.failure_counts.get("startpage", 0)
    }
    
    # Google - 需要API密钥
    google_api_key = _get_api_key("google", "api_key", "GOOGLE_SEARCH_API_KEY")
    google_engine_id = _get_api_key("google", "search_engine_id", "GOOGLE_SEARCH_ENGINE_ID")
    google_configured = bool(google_api_key and google_engine_id)
    google_available = google_configured and search_health.is_available("google")
    
    config_status["google"] = {
        "available": google_available,
        "note": ("已配置API密钥" if google_configured else "需要 API Key 和 Search Engine ID") + 
                ("，当前被暂时禁用" if google_configured and not google_available else ""),
        "source": "配置文件" if _load_search_config().get("google") else ("环境变量" if google_configured else "未配置"),
        "priority": search_health.get_engine_priority("google"),
        "failure_count": search_health.failure_counts.get("google", 0)
    }
    
    # Bing - 需要API密钥
    bing_api_key = _get_api_key("bing", "api_key", "BING_SEARCH_API_KEY")
    bing_configured = bool(bing_api_key)
    bing_available = bing_configured and search_health.is_available("bing")
    
    config_status["bing"] = {
        "available": bing_available,
        "note": ("已配置API密钥" if bing_configured else "需要 API Key") +
                ("，当前被暂时禁用" if bing_configured and not bing_available else ""),
        "source": "配置文件" if _load_search_config().get("bing") else ("环境变量" if bing_configured else "未配置"),
        "priority": search_health.get_engine_priority("bing"),
        "failure_count": search_health.failure_counts.get("bing", 0)
    }
    
    # SearX - 公开实例通常不稳定
    searx_available = search_health.is_available("searx")
    config_status["searx"] = {
        "available": searx_available,
        "note": "使用公开实例，连接不稳定" + ("，当前被暂时禁用" if not searx_available else ""),
        "source": "内置支持（不稳定）",
        "priority": search_health.get_engine_priority("searx"),
        "failure_count": search_health.failure_counts.get("searx", 0)
    }
    
    return config_status

def get_search_health_report() -> Dict[str, Any]:
    """获取搜索引擎健康状态报告"""
    available_engines = get_available_engines()
    
    report = {
        "available_engines": available_engines,
        "total_available": len(available_engines),
        "engine_priorities": {engine: search_health.get_engine_priority(engine) for engine in available_engines},
        "failure_counts": dict(search_health.failure_counts),
        "blacklisted_engines": [],
        "last_success": {}
    }
    
    # 检查黑名单引擎
    current_time = datetime.now()
    for engine, blacklist_time in search_health.blacklist_until.items():
        if current_time < blacklist_time:
            remaining_minutes = int((blacklist_time - current_time).total_seconds() / 60)
            report["blacklisted_engines"].append({
                "engine": engine,
                "remaining_minutes": remaining_minutes
            })
    
    # 最后成功时间
    for engine, success_time in search_health.last_success.items():
        hours_ago = int((current_time - success_time).total_seconds() / 3600)
        report["last_success"][engine] = f"{hours_ago}小时前" if hours_ago > 0 else "刚刚"
    
    return report 