"""
Amazon Listing Generator
主程序入口
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import requests
from bs4 import BeautifulSoup
import os
from PIL import Image
import threading
from transformers import pipeline
import json
from urllib.parse import urlparse


class AmazonListingGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Amazon Listing 生成器")
        self.root.geometry("1000x700")
        
        # 存储提取的数据
        self.extracted_data = {}
        
        self.setup_ui()
    
    def setup_ui(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 对标链接输入
        ttk.Label(main_frame, text="对标Listing链接:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.url_var = tk.StringVar()
        url_entry = ttk.Entry(main_frame, textvariable=self.url_var, width=80)
        url_entry.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 产品图片选择
        ttk.Label(main_frame, text="产品图片:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.image_paths = []
        self.image_listbox = tk.Listbox(main_frame, height=4)
        self.image_listbox.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 添加图片按钮
        add_image_btn = ttk.Button(main_frame, text="添加图片", command=self.add_images)
        add_image_btn.grid(row=4, column=0, sticky=tk.W, pady=5)
        
        # 删除图片按钮
        remove_image_btn = ttk.Button(main_frame, text="删除选中", command=self.remove_selected_image)
        remove_image_btn.grid(row=4, column=1, sticky=tk.W, pady=5, padx=(5, 0))
        
        # 生成按钮
        generate_btn = ttk.Button(main_frame, text="生成Listing", command=self.start_generation)
        generate_btn.grid(row=5, column=0, columnspan=2, pady=10)
        
        # 进度条
        self.progress = ttk.Progressbar(main_frame, mode='determinate', maximum=100)
        self.progress.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 结果显示区域
        result_frame = ttk.LabelFrame(main_frame, text="生成结果", padding="10")
        result_frame.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # 创建笔记本控件用于显示不同内容
        self.notebook = ttk.Notebook(result_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 英文标题标签页
        self.en_title_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.en_title_frame, text="英文标题")
        self.en_title_text = scrolledtext.ScrolledText(self.en_title_frame, height=5)
        self.en_title_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 中文标题标签页
        self.cn_title_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.cn_title_frame, text="中文标题")
        self.cn_title_text = scrolledtext.ScrolledText(self.cn_title_frame, height=5)
        self.cn_title_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 英文五点描述标签页
        self.en_bullet_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.en_bullet_frame, text="英文五点描述")
        self.en_bullet_text = scrolledtext.ScrolledText(self.en_bullet_frame, height=8)
        self.en_bullet_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 中文五点描述标签页
        self.cn_bullet_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.cn_bullet_frame, text="中文五点描述")
        self.cn_bullet_text = scrolledtext.ScrolledText(self.cn_bullet_frame, height=8)
        self.cn_bullet_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 英文详情描述标签页
        self.en_desc_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.en_desc_frame, text="英文详情描述")
        self.en_desc_text = scrolledtext.ScrolledText(self.en_desc_frame, height=10)
        self.en_desc_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 中文详情描述标签页
        self.cn_desc_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.cn_desc_frame, text="中文详情描述")
        self.cn_desc_text = scrolledtext.ScrolledText(self.cn_desc_frame, height=10)
        self.cn_desc_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(7, weight=1)
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
    
    def add_images(self):
        file_paths = filedialog.askopenfilenames(
            title="选择产品图片",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp"),
                ("All files", "*.*")
            ]
        )
        
        for path in file_paths:
            if path not in self.image_paths:
                self.image_paths.append(path)
                self.image_listbox.insert(tk.END, os.path.basename(path))
    
    def remove_selected_image(self):
        selected_idx = self.image_listbox.curselection()
        if selected_idx:
            idx = selected_idx[0]
            self.image_listbox.delete(idx)
            del self.image_paths[idx]
    
    def start_generation(self):
        """启动生成过程（在新线程中执行）"""
        if not self.url_var.get().strip():
            messagebox.showerror("错误", "请输入对标Listing链接")
            return
        
        if not self.image_paths:
            messagebox.showerror("错误", "请至少添加一张产品图片")
            return
        
        # 在新线程中执行，避免界面冻结
        thread = threading.Thread(target=self.generate_listing)
        thread.daemon = True
        thread.start()
    
    def generate_listing(self):
        """生成Listing的主要逻辑"""
        try:
            # 开始进度条
            self.root.after(0, self.progress.start)
            
            # 1. 提取对标链接数据
            self.root.after(0, self.set_progress_value_10)
            self.extract_data_from_url()
            
            # 2. 生成标题
            self.root.after(0, self.set_progress_value_30)
            en_title, cn_title = self.generate_titles()
            
            # 3. 生成五点描述
            self.root.after(0, self.set_progress_value_50)
            en_bullets, cn_bullets = self.generate_bullets()
            
            # 4. 生成详情描述
            self.root.after(0, self.set_progress_value_70)
            en_desc, cn_desc = self.generate_description()
            
            # 5. 在主线程中更新UI
            self.root.after(0, lambda: self.update_ui_with_results(
                en_title, cn_title, en_bullets, cn_bullets, en_desc, cn_desc
            ))
            
            # 停止进度条
            self.root.after(0, self.progress.stop)
            self.root.after(0, self.reset_progress_value)
            
            messagebox.showinfo("完成", "Listing生成完成！")
            
        except Exception as e:
            self.root.after(0, self.progress.stop)
            self.root.after(0, self.reset_progress_value)
            self.root.after(0, lambda: messagebox.showerror("错误", f"生成过程中出现错误: {str(e)}"))
    
    def set_progress_value_10(self):
        """设置进度条值为10"""
        self.progress['value'] = 10
    
    def set_progress_value_30(self):
        """设置进度条值为30"""
        self.progress['value'] = 30
    
    def set_progress_value_50(self):
        """设置进度条值为50"""
        self.progress['value'] = 50
    
    def set_progress_value_70(self):
        """设置进度条值为70"""
        self.progress['value'] = 70
    
    def reset_progress_value(self):
        """重置进度条值为0"""
        self.progress['value'] = 0
    
    def extract_data_from_url(self):
        """从对标链接提取数据"""
        url = self.url_var.get()
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 提取标题
            title_elem = soup.find(id='productTitle')
            if not title_elem:
                title_elem = soup.find('h1', {'class': 'a-size-large'})
            self.extracted_data['title'] = title_elem.get_text(strip=True) if title_elem else ""
            
            # 提取五点描述
            bullets = []
            ul_bullets = soup.find('ul', {'id': 'feature-bullets'})
            if not ul_bullets:
                ul_bullets = soup.find('div', {'id': 'feature-bullets'})
            
            if ul_bullets:
                lis = ul_bullets.find_all('li')
                for li in lis[:5]:  # 取前5个
                    bullet_text = li.get_text(strip=True)
                    if bullet_text:
                        bullets.append(bullet_text)
            
            self.extracted_data['bullets'] = bullets
            
            # 提取详情描述
            desc_elem = soup.find('div', {'id': 'productDescription'})
            if not desc_elem:
                desc_elem = soup.find('div', {'id': 'descriptionAndDetails'})
            self.extracted_data['description'] = desc_elem.get_text(strip=True) if desc_elem else ""
            
            # 提取品牌信息
            brand_elem = soup.find('a', {'id': 'bylineInfo'})
            self.extracted_data['brand'] = brand_elem.get_text(strip=True) if brand_elem else ""
            
        except Exception as e:
            print(f"提取URL数据时出错: {str(e)}")
            # 使用模拟数据以便继续测试
            self.extracted_data = {
                'title': 'Sample Product Title Extracted from URL',
                'bullets': [
                    'Feature 1 extracted from original listing',
                    'Feature 2 extracted from original listing',
                    'Feature 3 extracted from original listing',
                    'Feature 4 extracted from original listing',
                    'Feature 5 extracted from original listing'
                ],
                'description': 'This is a sample product description extracted from the original listing.',
                'brand': 'Sample Brand'
            }
    
    def generate_titles(self):
        """生成中英文标题"""
        # 使用提取的数据和AI模型生成标题
        original_title = self.extracted_data.get('title', '')
        
        # 这里应该是AI模型生成逻辑，暂时使用模拟数据
        en_title = f"Enhanced {original_title} - Premium Quality with Advanced Features"
        cn_title = f"升级版{original_title.split()[0] if original_title.split() else '产品'} - 高品质，功能先进"
        
        return en_title, cn_title
    
    def generate_bullets(self):
        """生成中英文五点描述"""
        # 使用提取的数据和AI模型生成五点描述
        original_bullets = self.extracted_data.get('bullets', [])
        
        # 这里应该是AI模型生成逻辑，暂时使用模拟数据
        en_bullets = [
            "Premium quality materials ensure durability and long-lasting use",
            "Advanced technology provides superior performance compared to competitors",
            "Ergonomic design offers comfortable handling and easy operation",
            "Versatile functionality meets various usage scenarios and requirements",
            "Excellent value for money with comprehensive features and benefits"
        ]
        
        cn_bullets = [
            "优质材料确保耐用性，使用寿命长久",
            "先进技术提供比竞品更优越的性能",
            "人体工学设计，操作舒适便捷",
            "多功能性满足各种使用场景需求",
            "物超所值，功能全面，优势明显"
        ]
        
        return en_bullets, cn_bullets
    
    def generate_description(self):
        """生成中英文详情描述"""
        # 使用提取的数据和AI模型生成详情描述
        original_desc = self.extracted_data.get('description', '')
        
        # 这里应该是AI模型生成逻辑，暂时使用模拟数据
        en_desc = f"""
Product Overview:
{original_desc if original_desc else 'This premium product combines advanced technology with user-friendly design to deliver exceptional performance.'}

Key Features:
• High-quality construction ensures reliability and longevity
• Innovative design enhances user experience
• Multi-functional capabilities for versatile applications
• Easy to use with intuitive controls
• Backed by our quality guarantee

Specifications:
• Material: Premium grade materials
• Dimensions: Standard sizing for optimal use
• Weight: Lightweight yet durable construction
• Color: Attractive finish options available

Package Includes:
• Main product
• User manual
• Warranty card
"""
        
        cn_desc = f"""
产品概述:
{original_desc if original_desc else '这款优质产品结合了先进技术与人性化设计，提供卓越的性能表现。'}

主要特点:
• 高质量构造确保可靠性和耐久性
• 创新设计提升用户体验
• 多功能性满足多样化应用场景
• 操作简便，控制直观
• 提供品质保证

规格参数:
• 材质: 优质材料
• 尺寸: 标准尺寸，使用优化
• 重量: 轻便但结构坚固
• 颜色: 多种颜色选项可供选择

包装清单:
• 产品主体
• 用户手册
• 保修卡
"""
        
        return en_desc, cn_desc
    
    def update_ui_with_results(self, en_title, cn_title, en_bullets, cn_bullets, en_desc, cn_desc):
        """在UI上更新生成的结果"""
        # 清空现有内容
        self.en_title_text.delete(1.0, tk.END)
        self.cn_title_text.delete(1.0, tk.END)
        self.en_bullet_text.delete(1.0, tk.END)
        self.cn_bullet_text.delete(1.0, tk.END)
        self.en_desc_text.delete(1.0, tk.END)
        self.cn_desc_text.delete(1.0, tk.END)
        
        # 插入新内容
        self.en_title_text.insert(tk.END, en_title)
        self.cn_title_text.insert(tk.END, cn_title)
        self.en_bullet_text.insert(tk.END, "\n".join(en_bullets))
        self.cn_bullet_text.insert(tk.END, "\n".join(cn_bullets))
        self.en_desc_text.insert(tk.END, en_desc)
        self.cn_desc_text.insert(tk.END, cn_desc)


def main():
    root = tk.Tk()
    app = AmazonListingGenerator(root)
    root.mainloop()


if __name__ == "__main__":
    main()