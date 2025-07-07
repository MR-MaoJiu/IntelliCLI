"""
图像处理工具 - 支持图像分析和多模态功能
"""

import base64
import os
from typing import Dict, Any, List, Optional
from PIL import Image
import io

class ImageProcessor:
    """图像处理和分析工具"""
    
    def __init__(self):
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']
    
    def is_image_file(self, file_path: str) -> bool:
        """检查文件是否是支持的图像格式"""
        if not os.path.exists(file_path):
            return False
        
        file_ext = os.path.splitext(file_path)[1].lower()
        return file_ext in self.supported_formats
    
    def get_image_info(self, file_path: str) -> Dict[str, Any]:
        """获取图像基本信息"""
        if not self.is_image_file(file_path):
            return {"error": "不是支持的图像文件"}
        
        try:
            with Image.open(file_path) as img:
                return {
                    "width": img.width,
                    "height": img.height,
                    "format": img.format,
                    "mode": img.mode,
                    "size": os.path.getsize(file_path),
                    "file_path": file_path
                }
        except Exception as e:
            return {"error": f"读取图像时出错: {e}"}
    
    def encode_image_to_base64(self, file_path: str) -> str:
        """将图像编码为 base64 字符串"""
        if not self.is_image_file(file_path):
            raise ValueError(f"不是支持的图像文件: {file_path}")
        
        try:
            with open(file_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                return encoded_string
        except Exception as e:
            raise Exception(f"编码图像时出错: {e}")
    
    def resize_image(self, file_path: str, max_size: int = 1024) -> str:
        """调整图像大小以适应模型输入限制"""
        if not self.is_image_file(file_path):
            raise ValueError(f"不是支持的图像文件: {file_path}")
        
        try:
            with Image.open(file_path) as img:
                # 如果图像已经足够小，直接返回原文件
                if max(img.width, img.height) <= max_size:
                    return file_path
                
                # 计算新尺寸
                ratio = max_size / max(img.width, img.height)
                new_width = int(img.width * ratio)
                new_height = int(img.height * ratio)
                
                # 调整尺寸
                resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # 生成临时文件名
                base_name = os.path.splitext(file_path)[0]
                ext = os.path.splitext(file_path)[1]
                temp_path = f"{base_name}_resized{ext}"
                
                # 保存调整后的图像
                resized_img.save(temp_path, quality=85, optimize=True)
                
                return temp_path
        except Exception as e:
            raise Exception(f"调整图像大小时出错: {e}")
    
    def find_images_in_directory(self, directory: str) -> List[str]:
        """查找目录中的所有图像文件"""
        images = []
        
        if not os.path.exists(directory):
            return images
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                if self.is_image_file(file_path):
                    images.append(file_path)
        
        return images
    
    def analyze_image_with_model(self, image_path: str, prompt: str, model_client) -> str:
        """使用多模态模型分析图像"""
        if not self.is_image_file(image_path):
            return f"错误: {image_path} 不是支持的图像文件"
        
        try:
            # 检查模型是否支持视觉功能
            if hasattr(model_client, 'generate_vision'):
                # 调整图像大小以适应模型限制
                processed_path = self.resize_image(image_path)
                
                # 使用视觉生成功能
                result = model_client.generate_vision(prompt, processed_path)
                
                # 如果是临时文件，清理
                if processed_path != image_path and os.path.exists(processed_path):
                    os.remove(processed_path)
                
                return result
            else:
                return "错误: 模型不支持视觉功能"
        except Exception as e:
            return f"分析图像时出错: {e}"

# 全局图像处理器实例
image_processor = ImageProcessor()

# 工具函数
def analyze_image(image_path: str, prompt: str = "请描述这张图片的内容") -> str:
    """分析图像内容"""
    from ..models.ollama_client import OllamaClient
    
    # 检查图像文件
    if not image_processor.is_image_file(image_path):
        return f"错误: {image_path} 不是支持的图像文件"
    
    # 获取图像信息
    info = image_processor.get_image_info(image_path)
    if "error" in info:
        return info["error"]
    
    # 这里需要从配置中获取视觉模型
    # 暂时使用硬编码的模型名称
    try:
        # 创建视觉模型客户端
        vision_client = OllamaClient("llava:34b")
        
        # 分析图像
        result = image_processor.analyze_image_with_model(image_path, prompt, vision_client)
        
        return f"图像信息: {info['width']}x{info['height']} {info['format']}\n\n分析结果:\n{result}"
    except Exception as e:
        return f"分析图像时出错: {e}"

def get_image_info(image_path: str) -> str:
    """获取图像基本信息"""
    info = image_processor.get_image_info(image_path)
    
    if "error" in info:
        return info["error"]
    
    return f"""图像信息:
- 文件路径: {info['file_path']}
- 尺寸: {info['width']} x {info['height']} 像素
- 格式: {info['format']}
- 颜色模式: {info['mode']}
- 文件大小: {info['size']} 字节
"""

def find_images(directory: str = ".") -> str:
    """查找目录中的图像文件"""
    images = image_processor.find_images_in_directory(directory)
    
    if not images:
        return f"在目录 '{directory}' 中未找到图像文件"
    
    result = f"在目录 '{directory}' 中找到 {len(images)} 个图像文件:\n"
    for img in images:
        result += f"- {img}\n"
    
    return result

def describe_image(image_path: str) -> str:
    """描述图像内容"""
    return analyze_image(image_path, "请详细描述这张图片的内容，包括主要物体、颜色、场景等")

def extract_text_from_image(image_path: str) -> str:
    """从图像中提取文本"""
    return analyze_image(image_path, "请识别并提取这张图片中的所有文本内容")

def identify_objects_in_image(image_path: str) -> str:
    """识别图像中的物体"""
    return analyze_image(image_path, "请识别这张图片中的所有物体和元素，并列出它们") 