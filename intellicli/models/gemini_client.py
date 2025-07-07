import os
import google.generativeai as genai
from typing import List, Dict, Any
from .base_llm import BaseLLM

class GeminiClient(BaseLLM):
    """
    用于与 Google Gemini API 交互的客户端。
    """

    def __init__(self, model_name: str, api_key: str = None):
        """
        初始化 Gemini 客户端。

        Args:
            model_name (str): 要使用的 Gemini 模型名称 (例如, 'gemini-1.5-pro-latest')。
            api_key (str, optional): API 密钥。如果未提供，将从
                                     GEMINI_API_KEY 环境变量中读取。
        """
        super().__init__(model_name)
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("未提供 Gemini API 密钥。请设置 GEMINI_API_KEY 环境变量。")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)

    def generate(self, prompt: str, **kwargs) -> str:
        """
        从 Gemini 模型生成文本响应。
        """
        try:
            response = self.model.generate_content(prompt, generation_config=genai.types.GenerationConfig(**kwargs))
            return response.text
        except Exception as e:
            print(f"调用 Gemini API 时出错: {e}")
            return f"错误: {e}"

    def generate_with_tools(self, prompt: str, tools: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """
        使用 Gemini API 的原生函数调用支持生成可能包含工具调用的响应。
        """
        try:
            response = self.model.generate_content(
                prompt, 
                tools=tools,
                generation_config=genai.types.GenerationConfig(**kwargs)
            )
            # 这部分需要扩展以正确处理响应并提取工具调用。
            # 目前，我们只返回原始响应部分。
            return {"parts": response.parts}
        except Exception as e:
            print(f"调用 Gemini API 工具时出错: {e}")
            return {"error": str(e)}

    def generate_vision(self, prompt: str, image_path: str, **kwargs) -> str:
        """
        使用 Gemini Vision 模型根据图像生成响应。
        """
        import PIL.Image
        try:
            img = PIL.Image.open(image_path)
            response = self.model.generate_content([prompt, img], generation_config=genai.types.GenerationConfig(**kwargs))
            return response.text
        except FileNotFoundError:
            return f"错误: 未找到图像文件: {image_path}"
        except Exception as e:
            print(f"调用 Gemini Vision API 时出错: {e}")
            return f"错误: {e}"