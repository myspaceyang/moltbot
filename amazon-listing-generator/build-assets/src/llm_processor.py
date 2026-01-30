"""
大语言模型处理器
用于生成高质量的标题、五点描述和详情描述
"""

import openai
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import os
from typing import List, Dict
import re


class LLMProcessor:
    def __init__(self, model_type="openai", api_key=None):
        """
        初始化LLM处理器
        :param model_type: 模型类型 ("openai", "transformers")
        :param api_key: API密钥（对于OpenAI）
        """
        self.model_type = model_type
        
        if model_type == "openai":
            if api_key:
                openai.api_key = api_key
            elif os.getenv("OPENAI_API_KEY"):
                openai.api_key = os.getenv("OPENAI_API_KEY")
            else:
                # 如果没有API密钥，暂时使用模拟模式
                print("警告: 没有提供OpenAI API密钥，将使用模拟模式")
                self.model_type = "mock"
        
        elif model_type == "transformers":
            # 使用本地模型
            model_name = "facebook/bart-large-cnn"  # 可以替换为其他模型
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
                self.generator = pipeline(
                    "text2text-generation",
                    model=self.model,
                    tokenizer=self.tokenizer,
                    device=0 if torch.cuda.is_available() else -1
                )
            except Exception as e:
                print(f"加载本地模型失败: {e}，将使用模拟模式")
                self.model_type = "mock"
    
    def generate_title(self, product_info: Dict, target_language: str = "english") -> str:
        """
        生成产品标题
        :param product_info: 产品信息字典
        :param target_language: 目标语言 ("english", "chinese")
        :return: 生成的标题
        """
        if self.model_type == "openai":
            prompt = self._create_title_prompt(product_info, target_language)
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an expert at creating compelling Amazon product titles."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=100,
                    temperature=0.7
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                print(f"OpenAI API调用失败: {e}")
                return self._mock_generate_title(product_info, target_language)
        
        elif self.model_type == "transformers":
            prompt = self._create_title_prompt(product_info, target_language)
            try:
                result = self.generator(prompt, max_length=100, num_return_sequences=1)
                return result[0]['generated_text']
            except Exception as e:
                print(f"本地模型调用失败: {e}")
                return self._mock_generate_title(product_info, target_language)
        
        else:  # mock模式
            return self._mock_generate_title(product_info, target_language)
    
    def generate_bullet_points(self, product_info: Dict, target_language: str = "english", count: int = 5) -> List[str]:
        """
        生成五点描述
        :param product_info: 产品信息字典
        :param target_language: 目标语言 ("english", "chinese")
        :param count: 生成数量
        :return: 生成的要点列表
        """
        if self.model_type == "openai":
            prompt = self._create_bullet_prompt(product_info, target_language, count)
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an expert at creating compelling Amazon product bullet points."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=300,
                    temperature=0.7
                )
                bullets_text = response.choices[0].message.content.strip()
                return self._parse_bullet_points(bullets_text)
            except Exception as e:
                print(f"OpenAI API调用失败: {e}")
                return self._mock_generate_bullet_points(product_info, target_language, count)
        
        elif self.model_type == "transformers":
            prompt = self._create_bullet_prompt(product_info, target_language, count)
            try:
                result = self.generator(prompt, max_length=300, num_return_sequences=1)
                bullets_text = result[0]['generated_text']
                return self._parse_bullet_points(bullets_text)
            except Exception as e:
                print(f"本地模型调用失败: {e}")
                return self._mock_generate_bullet_points(product_info, target_language, count)
        
        else:  # mock模式
            return self._mock_generate_bullet_points(product_info, target_language, count)
    
    def generate_description(self, product_info: Dict, target_language: str = "english") -> str:
        """
        生成详情描述
        :param product_info: 产品信息字典
        :param target_language: 目标语言 ("english", "chinese")
        :return: 生成的详情描述
        """
        if self.model_type == "openai":
            prompt = self._create_description_prompt(product_info, target_language)
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an expert at creating compelling Amazon product descriptions."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500,
                    temperature=0.7
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                print(f"OpenAI API调用失败: {e}")
                return self._mock_generate_description(product_info, target_language)
        
        elif self.model_type == "transformers":
            prompt = self._create_description_prompt(product_info, target_language)
            try:
                result = self.generator(prompt, max_length=500, num_return_sequences=1)
                return result[0]['generated_text']
            except Exception as e:
                print(f"本地模型调用失败: {e}")
                return self._mock_generate_description(product_info, target_language)
        
        else:  # mock模式
            return self._mock_generate_description(product_info, target_language)
    
    def _create_title_prompt(self, product_info: Dict, target_language: str) -> str:
        """创建标题生成提示"""
        lang_text = "English" if target_language.lower() == "english" else "Chinese"
        
        prompt = f"""
Create a compelling {lang_text} Amazon product title based on the following information:

Product Information:
- Original Title: {product_info.get('title', 'N/A')}
- Brand: {product_info.get('brand', 'N/A')}
- Key Features: {', '.join(product_info.get('feature_bullets', [])[:3]) if product_info.get('feature_bullets') else 'N/A'}
- Description: {product_info.get('description', 'N/A')[:200]}...

Requirements:
- Include key features and specifications
- Use compelling adjectives
- Keep it under 200 characters
- Optimize for search (include relevant keywords)
- Make it attractive to customers

Generated {lang_text} Title:"""
        
        return prompt
    
    def _create_bullet_prompt(self, product_info: Dict, target_language: str, count: int) -> str:
        """创建五点描述生成提示"""
        lang_text = "English" if target_language.lower() == "english" else "Chinese"
        
        prompt = f"""
Create {count} compelling {lang_text} Amazon product bullet points based on the following information:

Product Information:
- Original Title: {product_info.get('title', 'N/A')}
- Brand: {product_info.get('brand', 'N/A')}
- Original Bullets: {', '.join(product_info.get('feature_bullets', [])) if product_info.get('feature_bullets') else 'N/A'}
- Description: {product_info.get('description', 'N/A')[:300]}...

Requirements:
- Focus on benefits rather than just features
- Use power words and adjectives
- Keep each point under 500 characters
- Start each point with a capital letter
- Make them scannable and easy to read
- Highlight unique selling points

Generated {lang_text} Bullet Points (each on a new line):"""
        
        return prompt
    
    def _create_description_prompt(self, product_info: Dict, target_language: str) -> str:
        """创建详情描述生成提示"""
        lang_text = "English" if target_language.lower() == "english" else "Chinese"
        
        prompt = f"""
Create a compelling {lang_text} Amazon product description based on the following information:

Product Information:
- Original Title: {product_info.get('title', 'N/A')}
- Brand: {product_info.get('brand', 'N/A')}
- Original Bullets: {', '.join(product_info.get('feature_bullets', [])) if product_info.get('feature_bullets') else 'N/A'}
- Description: {product_info.get('description', 'N/A')[:500]}...

Requirements:
- Expand on the key features and benefits
- Include usage scenarios and target audience
- Use persuasive language
- Structure with paragraphs
- Keep it between 1000-2000 characters
- Make it SEO-friendly

Generated {lang_text} Description:"""
        
        return prompt
    
    def _parse_bullet_points(self, text: str) -> List[str]:
        """解析生成的要点文本"""
        # 分割文本，按行分割
        lines = text.split('\n')
        bullets = []
        
        for line in lines:
            # 清理行首尾空白
            line = line.strip()
            
            # 移除编号或符号前缀
            cleaned = re.sub(r'^[\d+\-\*\•]\.\s*', '', line)  # 移除 "1. ", "2. ", "- ", "* ", "• "等
            cleaned = re.sub(r'^[\d+\-\*\•]\s+', '', cleaned)  # 移除 "1 ", "2 ", "- ", 等
            
            if cleaned and len(cleaned) > 5:  # 忽略太短的行
                bullets.append(cleaned)
        
        # 如果没有通过换行符分割出要点，尝试按句号分割
        if len(bullets) < 2:
            sentences = re.split(r'[.!?]+', text)
            bullets = [s.strip() for s in sentences if len(s.strip()) > 10]
        
        return bullets[:5]  # 限制为最多5个要点
    
    def _mock_generate_title(self, product_info: Dict, target_language: str) -> str:
        """模拟生成标题"""
        if target_language.lower() == "chinese":
            return f"【升级版】{product_info.get('title', '产品').split()[0] if product_info.get('title') else '商品'} - 高品质，功能强大，{product_info.get('brand', '品牌')}官方正品"
        else:
            return f"Premium {product_info.get('title', 'Product')} - Enhanced Version with Advanced Features, High Quality {product_info.get('brand', 'Brand')} Official Product"
    
    def _mock_generate_bullet_points(self, product_info: Dict, target_language: str, count: int) -> List[str]:
        """模拟生成要点"""
        if target_language.lower() == "chinese":
            base_bullets = [
                "高品质材料制造，确保产品耐用性和可靠性",
                "创新设计，提供卓越的用户体验和便利性",
                "多功能特性，满足多样化的使用需求",
                "易于操作和维护，节省时间和精力",
                "专业认证，安全可靠，品质保证"
            ]
        else:
            base_bullets = [
                "High-quality materials ensure product durability and reliability",
                "Innovative design provides superior user experience and convenience",
                "Multi-functional features meet diverse usage requirements",
                "Easy to operate and maintain, saving time and effort",
                "Professional certification, safe and reliable, quality guaranteed"
            ]
        
        return base_bullets[:count]
    
    def _mock_generate_description(self, product_info: Dict, target_language: str) -> str:
        """模拟生成详情描述"""
        if target_language.lower() == "chinese":
            return f"""
产品概述:
{product_info.get('description', '这款高品质产品结合了先进技术与人性化设计，为用户提供卓越的使用体验。')}

核心特点:
• 采用优质材料制造，确保长期使用的可靠性
• 创新技术加持，性能表现优于同类产品
• 人体工学设计，操作舒适便捷
• 多功能性设计，适应多种使用场景
• 通过严格质量检测，安全可靠

适用人群:
{product_info.get('brand', '本产品')}适用于对品质有高要求的用户，无论是日常使用还是专业场合都能表现出色。
"""
        else:
            return f"""
Product Overview:
{product_info.get('description', 'This high-quality product combines advanced technology with user-centric design to deliver an exceptional user experience.')}

Key Features:
• Made with premium materials to ensure long-term reliability
• Enhanced with innovative technology for superior performance compared to similar products
• Ergonomic design for comfortable and convenient operation
• Multi-functional design suitable for various usage scenarios
• Passed strict quality inspections, safe and reliable

Target Users:
{product_info.get('brand', 'This product')} is suitable for users who demand high quality and can perform excellently in both daily use and professional settings.
"""


# 示例使用
if __name__ == "__main__":
    # 初始化处理器
    processor = LLMProcessor(model_type="mock")  # 使用模拟模式
    
    # 示例产品信息
    sample_info = {
        'title': 'Wireless Bluetooth Headphones',
        'brand': 'TechSound',
        'feature_bullets': [
            'Bluetooth 5.0 for stable connection',
            'Noise cancellation technology',
            '30-hour battery life',
            'Comfortable over-ear design',
            'Built-in microphone for calls'
        ],
        'description': 'Premium wireless headphones with advanced noise cancellation and exceptional sound quality.'
    }
    
    # 生成英文内容
    en_title = processor.generate_title(sample_info, "english")
    en_bullets = processor.generate_bullet_points(sample_info, "english")
    en_desc = processor.generate_description(sample_info, "english")
    
    # 生成中文内容
    cn_title = processor.generate_title(sample_info, "chinese")
    cn_bullets = processor.generate_bullet_points(sample_info, "chinese")
    cn_desc = processor.generate_description(sample_info, "chinese")
    
    print("英文标题:", en_title)
    print("\n英文要点:", "\n".join(en_bullets))
    print("\n英文描述:", en_desc)
    print("\n" + "="*50 + "\n")
    print("中文标题:", cn_title)
    print("\n中文要点:", "\n".join(cn_bullets))
    print("\n中文描述:", cn_desc)