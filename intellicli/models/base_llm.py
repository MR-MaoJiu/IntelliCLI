from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseLLM(ABC):
    """
    所有大型语言模型的抽象基类 (Abstract Base Class)。
    该类定义了所有模型客户端必须实现的通用接口。
    """

    @abstractmethod
    def __init__(self, model_name: str, **kwargs):
        """
        初始化模型客户端。

        Args:
            model_name (str): 要使用的模型的名称。
            **kwargs: 用于模型提供商的其他关键字参数 (例如, api_key)。
        """
        self.model_name = model_name

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """
        根据给定的提示生成文本响应。

        Args:
            prompt (str): 模型的输入提示。
            **kwargs: 额外的生成参数 (例如, temperature, max_tokens)。

        Returns:
            str: 生成的文本。
        """
        pass

    @abstractmethod
    def generate_with_tools(self, prompt: str, tools: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """
        根据提供的工具生成可能包含工具调用的响应。

        Args:
            prompt (str): 输入提示。
            tools (List[Dict[str, Any]]): 特定格式的可用工具列表
                                         (例如, OpenAI函数调用格式)。
            **kwargs: 额外的生成参数。

        Returns:
            Dict[str, Any]: 包含模型响应的字典，可能是
                            文本响应或工具调用。
        """
        pass

    @abstractmethod
    def generate_vision(self, prompt: str, image_path: str, **kwargs) -> str:
        """
        根据提示和图像生成文本响应。

        Args:
            prompt (str): 提示的文本部分。
            image_path (str): 图像文件的路径。
            **kwargs: 额外的生成参数。

        Returns:
            str: 描述或分析图像的生成文本。
        """
        pass