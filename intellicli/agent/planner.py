import json
from typing import List, Dict, Any

class Planner:
    """
    规划器负责将复杂的用户请求分解为一系列可操作的步骤 ("待办事项列表")。
    """

    def __init__(self, model_client):
        """
        使用模型客户端初始化规划器。

        Args:
            model_client: 继承自 BaseLLM 的类实例。
        """
        self.model_client = model_client

    def create_plan(self, goal: str, tools: List[Dict[str, Any]], max_retries: int = 3) -> List[Dict[str, Any]]:
        """
        生成实现目标的逐步计划。如果模型未返回有效的 JSON 计划，它将重试最多
        `max_retries` 次。
        """
        # 构建详细的工具说明
        tool_descriptions = []
        for tool in tools:
            tool_name = tool['name']
            tool_desc = tool.get('description', '无描述')
            
            # 构建参数信息
            param_info = []
            for param in tool.get('parameters', []):
                param_name = param['name']
                param_type = param.get('type', 'Any')
                required = param.get('required', True)
                required_marker = " (必需)" if required else " (可选)"
                param_info.append(f"  - {param_name}: {param_type}{required_marker}")
            
            if param_info:
                tool_descriptions.append(f"- {tool_name}: {tool_desc}\n" + "\n".join(param_info))
            else:
                tool_descriptions.append(f"- {tool_name}: {tool_desc}")
        
        prompt = f"""
您是一位智能的任务规划代理。您的任务是将一个高级目标分解为一系列精确、可执行的步骤。
您必须只用有效的 JSON 任务数组进行响应。不要包含任何其他文本、解释或 Markdown 格式。

**目标:**
{goal}

**可用工具及其参数:**
{chr(10).join(tool_descriptions)}

**关键规则:**
1. 仔细分析目标，选择最合适的工具
2. 使用正确的参数名称（如上所示）
3. 确保参数类型正确
4. 创建逻辑清晰的步骤序列
5. 如果步骤需要前一步的输出，使用 "<PREVIOUS_STEP_OUTPUT>" 作为占位符

**JSON 格式要求:**
- 每个步骤包含: "step" (整数), "tool" (工具名), "arguments" (参数字典)
- 参数名称必须与上述工具定义完全匹配
- 只使用上述列出的工具

**响应示例:**
```json
[
    {{
        "step": 1,
        "tool": "list_directory",
        "arguments": {{
            "path": "."
        }}
    }},
    {{
        "step": 2,
        "tool": "write_file",
        "arguments": {{
            "path": "/path/to/file.txt",
            "content": "文件内容"
        }}
    }}
]
```

**您的响应必须仅是 JSON 数组，不要包含任何其他内容。**
"""
        
        for attempt in range(max_retries):
            print(f"规划尝试 {attempt + 1}/{max_retries}...")
            response_text = self.model_client.generate(prompt)
            
            # 清理响应以仅提取 JSON 部分
            try:
                # 查找 JSON 数组的开始位置
                json_start = response_text.find('[')
                # 查找 JSON 数组的结束位置
                json_end = response_text.rfind(']') + 1
                
                if json_start != -1 and json_end != 0:
                    clean_response = response_text[json_start:json_end]
                    plan = json.loads(clean_response)
                    
                    # 验证计划格式
                    if self._validate_plan(plan, tools):
                        return plan
                    else:
                        print("生成的计划格式或内容不正确。")
                else:
                    print("响应中未找到有效的 JSON 数组。")
            except (json.JSONDecodeError, IndexError) as e:
                print(f"尝试 {attempt + 1} 失败: 无法从响应中解析出有效的 JSON。错误: {e}")
                print(f"原始响应: {response_text[:500]}...")
                continue

        print("错误: 模型在多次尝试后未能生成有效的计划。")
        return []

    def _validate_plan(self, plan: List[Dict[str, Any]], tools: List[Dict[str, Any]]) -> bool:
        """
        验证计划的格式和内容是否正确。
        """
        if not isinstance(plan, list):
            print("计划不是列表格式")
            return False
        
        if len(plan) == 0:
            print("计划为空")
            return False
        
        # 创建工具名称到工具信息的映射
        tool_map = {tool['name']: tool for tool in tools}
        
        for i, step in enumerate(plan):
            step_num = i + 1
            
            if not isinstance(step, dict):
                print(f"步骤 {step_num} 不是字典格式")
                return False
            
            required_keys = ['step', 'tool', 'arguments']
            if not all(key in step for key in required_keys):
                print(f"步骤 {step_num} 缺少必要的键: {required_keys}")
                return False
            
            tool_name = step['tool']
            if tool_name not in tool_map:
                print(f"步骤 {step_num} 使用了不存在的工具: {tool_name}")
                return False
            
            if not isinstance(step['arguments'], dict):
                print(f"步骤 {step_num} 的参数不是字典格式")
                return False
            
            # 验证参数名称
            tool_info = tool_map[tool_name]
            expected_params = {p['name']: p for p in tool_info.get('parameters', [])}
            provided_params = set(step['arguments'].keys())
            
            # 检查无效参数
            invalid_params = provided_params - set(expected_params.keys())
            if invalid_params:
                print(f"步骤 {step_num} 工具 {tool_name} 包含无效参数: {invalid_params}")
                print(f"  期望参数: {list(expected_params.keys())}")
                return False
            
            # 检查必需参数是否提供
            required_params = {name for name, info in expected_params.items() if info.get('required', True)}
            missing_params = required_params - provided_params
            if missing_params:
                print(f"步骤 {step_num} 工具 {tool_name} 缺少必需参数: {missing_params}")
                return False
        
        return True