"""
多模态管理器 - 协调文本和图像处理的统一接口
"""

import os
import re
from typing import Dict, Any, List, Optional, Union
from ..tools.image_processor import ImageProcessor

class MultimodalManager:
    """多模态管理器，提供统一的文本和图像处理接口"""
    
    def __init__(self):
        self.image_processor = ImageProcessor()
        self.vision_models = []  # 支持视觉的模型列表
        self.text_models = []    # 文本模型列表
    
    def register_vision_model(self, model_alias: str, model_client):
        """注册视觉模型"""
        self.vision_models.append({
            'alias': model_alias,
            'client': model_client,
            'capabilities': self._detect_model_capabilities(model_client)
        })
    
    def register_text_model(self, model_alias: str, model_client):
        """注册文本模型"""
        self.text_models.append({
            'alias': model_alias,
            'client': model_client,
            'capabilities': self._detect_model_capabilities(model_client)
        })
    
    def _detect_model_capabilities(self, model_client) -> List[str]:
        """检测模型的能力"""
        capabilities = []
        
        # 检查是否有视觉功能
        if hasattr(model_client, 'generate_vision'):
            capabilities.append('vision')
        
        # 检查是否有工具调用功能
        if hasattr(model_client, 'generate_with_tools'):
            capabilities.append('tools')
        
        # 默认都有文本生成能力
        capabilities.append('text')
        
        return capabilities
    
    def analyze_input(self, input_text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """分析输入内容，确定处理模式"""
        context = context or {}
        
        analysis = {
            'type': 'text',
            'requires_vision': False,
            'image_paths': [],
            'text_content': input_text,
            'processing_suggestions': []
        }
        
        # 检查是否包含图像引用
        if self._contains_image_reference(input_text):
            analysis['requires_vision'] = True
            analysis['type'] = 'multimodal'
            
            # 尝试提取图像路径
            extracted_paths = self._extract_image_paths(input_text)
            analysis['image_paths'] = extracted_paths
        
        # 检查上下文中是否有图像文件
        if 'file_paths' in context:
            for path in context['file_paths']:
                if self.image_processor.is_image_file(path):
                    analysis['requires_vision'] = True
                    analysis['type'] = 'multimodal'
                    if path not in analysis['image_paths']:
                        analysis['image_paths'].append(path)
        
        # 生成处理建议
        if analysis['requires_vision']:
            analysis['processing_suggestions'].append('使用视觉模型处理图像内容')
            if analysis['image_paths']:
                analysis['processing_suggestions'].append(f'处理 {len(analysis["image_paths"])} 个图像文件')
        
        return analysis
    
    def process_multimodal_input(self, input_text: str, context: Dict[str, Any] = None) -> str:
        """处理多模态输入"""
        analysis = self.analyze_input(input_text, context)
        
        if analysis['type'] == 'text':
            # 纯文本处理
            return self._process_text_only(input_text)
        elif analysis['type'] == 'multimodal':
            # 多模态处理
            return self._process_multimodal(input_text, analysis)
        else:
            return "未知的输入类型"
    
    def _process_text_only(self, text: str) -> str:
        """处理纯文本输入"""
        # 使用最合适的文本模型
        if self.text_models:
            model = self.text_models[0]  # 使用第一个文本模型
            return model['client'].generate(text)
        else:
            return "错误: 没有可用的文本模型"
    
    def _process_multimodal(self, text: str, analysis: Dict[str, Any]) -> str:
        """处理多模态输入"""
        if not self.vision_models:
            return "错误: 没有可用的视觉模型来处理图像内容"
        
        # 选择最合适的视觉模型
        vision_model = self.vision_models[0]
        
        if analysis['image_paths']:
            # 处理每个图像
            results = []
            for image_path in analysis['image_paths']:
                try:
                    # 获取图像信息
                    image_info = self.image_processor.get_image_info(image_path)
                    
                    if 'error' in image_info:
                        results.append(f"处理 {image_path} 时出错: {image_info['error']}")
                        continue
                    
                    # 使用视觉模型分析图像
                    vision_prompt = self._create_vision_prompt(text, image_path)
                    vision_result = vision_model['client'].generate_vision(vision_prompt, image_path)
                    
                    results.append(f"图像 {image_path} ({image_info['width']}x{image_info['height']}):\n{vision_result}")
                    
                except Exception as e:
                    results.append(f"处理 {image_path} 时出错: {e}")
            
            return "\n\n".join(results)
        else:
            return "错误: 需要视觉处理但未找到图像文件"
    
    def _create_vision_prompt(self, original_text: str, image_path: str) -> str:
        """为视觉模型创建优化的提示"""
        # 基于原始文本和图像路径创建更好的提示
        vision_prompt = original_text
        
        # 添加图像上下文信息
        if self.image_processor.is_image_file(image_path):
            image_info = self.image_processor.get_image_info(image_path)
            if 'error' not in image_info:
                vision_prompt += f"\n\n图像信息: {image_info['width']}x{image_info['height']} {image_info['format']}"
        
        return vision_prompt
    
    def _contains_image_reference(self, text: str) -> bool:
        """检查文本中是否包含图像引用"""
        image_keywords = [
            "图像", "图片", "照片", "截图", "png", "jpg", "jpeg", "gif", "bmp", "tiff", "webp",
            "image", "photo", "picture", "screenshot", "看图", "分析图", "识别图",
            "视觉", "visual", "multimodal", "多模态", "看看", "识别"
        ]
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in image_keywords)
    
    def _extract_image_paths(self, text: str) -> List[str]:
        """从文本中提取图像路径"""
        paths = []
        
        # 匹配常见的文件路径模式
        path_patterns = [
            r'["\']([^"\']*\.(?:png|jpg|jpeg|gif|bmp|tiff|webp))["\']',  # 带引号的路径
            r'(\S+\.(?:png|jpg|jpeg|gif|bmp|tiff|webp))',  # 不带引号的路径
            r'文件路径[：:]\s*([^\s]+)',  # 中文文件路径标识
            r'image[:\s]+([^\s]+)',  # 英文图像路径标识
        ]
        
        for pattern in path_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    path = match[0].strip()
                else:
                    path = match.strip()
                
                if os.path.exists(path) and self.image_processor.is_image_file(path):
                    if path not in paths:
                        paths.append(path)
        
        return paths
    
    def get_available_models(self) -> Dict[str, List[str]]:
        """获取可用模型列表"""
        return {
            'vision_models': [model['alias'] for model in self.vision_models],
            'text_models': [model['alias'] for model in self.text_models]
        }
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型详细信息"""
        return {
            'vision_models': [
                {
                    'alias': model['alias'],
                    'capabilities': model['capabilities']
                } for model in self.vision_models
            ],
            'text_models': [
                {
                    'alias': model['alias'],
                    'capabilities': model['capabilities']
                } for model in self.text_models
            ]
        }

# 全局多模态管理器实例
multimodal_manager = MultimodalManager() 