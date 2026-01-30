"""
图片处理器模块
处理主图和详情图的生成
"""

from PIL import Image, ImageDraw, ImageFont
import os
from typing import List, Tuple


class ImageProcessor:
    def __init__(self):
        self.supported_formats = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')
    
    def resize_image(self, image_path: str, size: Tuple[int, int], output_path: str = None) -> str:
        """
        调整图片大小
        :param image_path: 原图路径
        :param size: 目标尺寸 (width, height)
        :param output_path: 输出路径，如果为None则自动生成
        :return: 输出图片路径
        """
        with Image.open(image_path) as img:
            # 调整图片大小，保持比例
            img = img.resize(size, Image.Resampling.LANCZOS)
            
            if output_path is None:
                base_path = os.path.splitext(image_path)[0]
                output_path = f"{base_path}_resized.jpg"
            
            img.save(output_path, quality=95, optimize=True)
            return output_path
    
    def create_main_image(self, image_paths: List[str], output_path: str) -> str:
        """
        创建主图 - 通常Amazon主图需要纯白背景
        :param image_paths: 原图路径列表
        :param output_path: 输出路径
        :return: 输出图片路径
        """
        if not image_paths:
            raise ValueError("至少需要一个图片路径")
        
        # 使用第一张图片作为主图
        main_img_path = image_paths[0]
        
        with Image.open(main_img_path) as img:
            # 确保图片尺寸为1:1比例（Amazon推荐）
            width, height = img.size
            size = min(width, height)
            
            # 裁剪为正方形
            left = (width - size) / 2
            top = (height - size) / 2
            right = (width + size) / 2
            bottom = (height + size) / 2
            
            img = img.crop((left, top, right, bottom))
            
            # 调整到Amazon推荐尺寸 1000x1000
            img = img.resize((1000, 1000), Image.Resampling.LANCZOS)
            
            # 确保背景为白色
            if img.mode in ('RGBA', 'LA'):
                # 创建白色背景
                background = Image.new('RGB', img.size, (255, 255, 255))
                # 如果原图有透明背景，则粘贴到白色背景上
                if img.mode == 'RGBA':
                    background.paste(img, mask=img.split()[-1])  # 使用alpha通道作为掩码
                else:
                    background.paste(img)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            img.save(output_path, quality=95, optimize=True)
            return output_path
    
    def create_detail_images(self, image_paths: List[str], output_dir: str) -> List[str]:
        """
        创建详情图 - 通常是多张展示产品的不同角度或细节
        :param image_paths: 原图路径列表
        :param output_dir: 输出目录
        :return: 输出图片路径列表
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        output_paths = []
        
        for i, img_path in enumerate(image_paths):
            with Image.open(img_path) as img:
                # 调整到Amazon详情图推荐尺寸 1500x1500
                width, height = img.size
                ratio = min(width, height) / 1500
                new_size = (int(width / ratio), int(height / ratio))
                
                img = img.resize(new_size, Image.Resampling.LANCZOS)
                
                # 如果宽高比不是1:1，添加白色边框使其变为1:1
                if img.width != img.height:
                    max_dim = max(img.width, img.height)
                    background = Image.new('RGB', (max_dim, max_dim), (255, 255, 255))
                    
                    # 计算居中位置
                    offset_x = (max_dim - img.width) // 2
                    offset_y = (max_dim - img.height) // 2
                    
                    background.paste(img, (offset_x, offset_y))
                    img = background
                
                # 最终调整为1500x1500
                img = img.resize((1500, 1500), Image.Resampling.LANCZOS)
                
                output_path = os.path.join(output_dir, f"detail_{i+1}.jpg")
                img.save(output_path, quality=95, optimize=True)
                output_paths.append(output_path)
        
        return output_paths
    
    def add_watermark(self, image_path: str, watermark_text: str, output_path: str = None) -> str:
        """
        添加水印
        :param image_path: 原图路径
        :param watermark_text: 水印文字
        :param output_path: 输出路径
        :return: 输出图片路径
        """
        with Image.open(image_path) as img:
            draw = ImageDraw.Draw(img)
            
            # 尝试使用默认字体，如果没有则使用系统字体
            try:
                font = ImageFont.truetype("arial.ttf", 36)
            except IOError:
                try:
                    font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 36)  # macOS
                except IOError:
                    try:
                        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)  # Linux
                    except IOError:
                        font = ImageFont.load_default()
            
            # 计算水印位置（右下角）
            text_bbox = draw.textbbox((0, 0), watermark_text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            width, height = img.size
            margin = 50
            x = width - text_width - margin
            y = height - text_height - margin
            
            # 添加半透明白色背景
            overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            overlay_draw.rectangle([x-10, y-10, x+text_width+10, y+text_height+10], fill=(255, 255, 255, 128))
            
            # 合并图像
            img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
            
            # 添加文字
            draw = ImageDraw.Draw(img)
            draw.text((x, y), watermark_text, fill=(0, 0, 0), font=font)
            
            if output_path is None:
                base_path = os.path.splitext(image_path)[0]
                output_path = f"{base_path}_watermarked.jpg"
            
            img.save(output_path, quality=95, optimize=True)
            return output_path
    
    def batch_process(self, input_dir: str, output_dir: str, 
                     process_type: str = "detail", **kwargs) -> List[str]:
        """
        批量处理图片
        :param input_dir: 输入目录
        :param output_dir: 输出目录
        :param process_type: 处理类型 ("main", "detail", "resize", "watermark")
        :param kwargs: 额外参数
        :return: 输出图片路径列表
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        processed_paths = []
        
        for filename in os.listdir(input_dir):
            if filename.lower().endswith(self.supported_formats):
                input_path = os.path.join(input_dir, filename)
                
                if process_type == "main":
                    output_path = os.path.join(output_dir, f"main_{filename}")
                    processed_path = self.create_main_image([input_path], output_path)
                elif process_type == "detail":
                    # 创建详情图
                    detail_dir = os.path.join(output_dir, "details")
                    if not os.path.exists(detail_dir):
                        os.makedirs(detail_dir)
                    processed_paths.extend(self.create_detail_images([input_path], detail_dir))
                    continue  # 继续下一张，因为create_detail_images会处理整个列表
                elif process_type == "resize":
                    size = kwargs.get("size", (1000, 1000))
                    output_path = os.path.join(output_dir, f"resized_{filename}")
                    processed_path = self.resize_image(input_path, size, output_path)
                elif process_type == "watermark":
                    watermark_text = kwargs.get("watermark_text", "")
                    output_path = os.path.join(output_dir, f"watermarked_{filename}")
                    processed_path = self.add_watermark(input_path, watermark_text, output_path)
                else:
                    raise ValueError(f"不支持的处理类型: {process_type}")
                
                processed_paths.append(processed_path)
        
        return processed_paths