"""
图像处理工具 - 支持图像分析和多模态功能
"""

import base64
import os
from typing import Dict, Any, List, Optional
from PIL import Image
import io

# 全局模型客户端变量
_global_model_client = None

def set_model_client(model_client):
    """设置全局模型客户端"""
    global _global_model_client
    _global_model_client = model_client

def get_model_client():
    """获取当前的模型客户端"""
    return _global_model_client

class ImageProcessor:
    """图像处理工具类"""
    
    def __init__(self):
        self.supported_formats = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp']
        self.model_client = None

    def set_model_client(self, model_client):
        """设置图像处理使用的模型客户端"""
        self.model_client = model_client

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
    
    def analyze_image_with_model(self, image_path: str, prompt: str, model_client=None) -> str:
        """使用指定的模型客户端分析图像"""
        if not os.path.exists(image_path):
            return f"图像文件不存在: {image_path}"
        
        if not self.is_image_file(image_path):
            return f"不支持的图像格式: {image_path}"
        
        # 使用传入的模型客户端，或者全局模型客户端，或者实例模型客户端
        client = model_client or _global_model_client or self.model_client
        
        if not client:
            return "未设置模型客户端，无法分析图像"
        
        try:
            # 检查模型客户端是否支持视觉功能
            if hasattr(client, 'generate_vision'):
                return client.generate_vision(prompt, image_path)
            else:
                return f"模型客户端 {client.__class__.__name__} 不支持视觉功能"
        except Exception as e:
            return f"分析图像时出错: {e}"

# 全局图像处理器实例
image_processor = ImageProcessor()

# 增强的图像分析函数
def analyze_image(image_path: str, prompt: str = "请描述这张图片的内容") -> str:
    """分析图像内容"""
    processor = ImageProcessor()
    
    # 使用全局模型客户端
    model_client = get_model_client()
    if model_client:
        processor.set_model_client(model_client)
    
    if not os.path.exists(image_path):
        return f"图像文件不存在: {image_path}"
    
    if not processor.is_image_file(image_path):
        return f"不支持的图像格式: {image_path}"
    
    try:
        # 获取图像基本信息
        image_info = processor.get_image_info(image_path)
        
        # 使用模型分析图像
        analysis_result = processor.analyze_image_with_model(image_path, prompt)
        
        # 整合结果
        result = f"图像分析结果:\n"
        result += f"文件路径: {image_path}\n"
        result += f"图像信息: {image_info['format']} 格式，{image_info['size']} 像素\n"
        result += f"文件大小: {image_info['file_size']}\n"
        result += f"分析内容: {analysis_result}"
        
        return result
        
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
    return analyze_image(image_path, "请详细描述这张图片的内容，包括主要对象、场景、颜色、构图等信息")

def extract_text_from_image(image_path: str) -> str:
    """从图像中提取文本"""
    return analyze_image(image_path, "请识别并提取图像中的所有文本内容，按照在图像中的位置和层次结构输出")

def identify_objects_in_image(image_path: str) -> str:
    """识别图像中的对象"""
    return analyze_image(image_path, "请识别图像中的所有对象，包括人物、物品、动物、建筑等，并说明它们的位置和特征")

def analyze_image_style(image_path: str) -> str:
    """分析图像风格"""
    return analyze_image(image_path, "请分析这张图片的艺术风格、摄影技法、色彩搭配和视觉效果")

def generate_image_tags(image_path: str) -> str:
    """生成图像标签"""
    return analyze_image(image_path, "请为这张图片生成相关的标签和关键词，用于分类和搜索")

def compare_images(image_path1: str, image_path2: str) -> str:
    """比较两张图像"""
    processor = ImageProcessor()
    model_client = get_model_client()
    
    if not model_client:
        return "未设置模型客户端，无法比较图像"
    
    try:
        # 分析第一张图像
        result1 = processor.analyze_image_with_model(image_path1, "请描述这张图片的内容", model_client)
        
        # 分析第二张图像
        result2 = processor.analyze_image_with_model(image_path2, "请描述这张图片的内容", model_client)
        
        # 生成比较结果
        compare_prompt = f"""
        请比较以下两张图像的描述，找出它们的相似之处和不同之处：
        
        图像1描述：{result1}
        图像2描述：{result2}
        
        请从以下几个方面进行比较：
        1. 主要内容和主题
        2. 色彩和风格
        3. 构图和布局
        4. 细节差异
        5. 整体相似度评分（1-10分）
        """
        
        return model_client.generate(compare_prompt)
        
    except Exception as e:
        return f"比较图像时出错: {e}" 