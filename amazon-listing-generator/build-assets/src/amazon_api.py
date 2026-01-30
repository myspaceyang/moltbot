"""
Amazon API 接口模块
用于获取对标listing数据和验证生成内容
"""

import requests
from bs4 import BeautifulSoup
import time
import random
from urllib.parse import urlparse, parse_qs
import re


class AmazonAPI:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        self.session.headers.update(self.headers)
    
    def get_product_details(self, url: str) -> dict:
        """
        从Amazon链接获取产品详细信息
        :param url: Amazon产品页面URL
        :return: 包含产品信息的字典
        """
        try:
            # 验证URL格式
            parsed_url = urlparse(url)
            if 'amazon' not in parsed_url.netloc:
                raise ValueError("URL必须是Amazon域名")
            
            # 获取页面内容
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            product_data = {}
            
            # 提取产品标题
            title_elem = soup.find(id='productTitle')
            if not title_elem:
                title_elem = soup.find('span', {'id': 'productTitle'})
            if not title_elem:
                title_elem = soup.find('h1', {'class': re.compile(r'.*title.*', re.I)})
            
            product_data['title'] = title_elem.get_text(strip=True) if title_elem else ""
            
            # 提取产品特性（五点描述）
            feature_bullets = []
            ul_bullets = soup.find('ul', {'id': 'feature-bullets'})
            if not ul_bullets:
                ul_bullets = soup.find('div', {'id': 'feature-bullets'})
            
            if ul_bullets:
                lis = ul_bullets.find_all('li')
                for li in lis[:5]:  # 取前5个特性
                    bullet_text = li.get_text(strip=True)
                    if bullet_text:
                        # 清理文本
                        bullet_text = re.sub(r'^[\*\-\•\s]+', '', bullet_text)  # 移除开头的符号
                        feature_bullets.append(bullet_text)
            
            product_data['feature_bullets'] = feature_bullets
            
            # 提取产品描述
            desc_elem = soup.find('div', {'id': 'productDescription'})
            if not desc_elem:
                desc_elem = soup.find('div', {'id': 'aplus'})
            if not desc_elem:
                desc_elem = soup.find('div', {'data-feature-name': 'productDescription'})
            
            product_data['description'] = desc_elem.get_text(strip=True) if desc_elem else ""
            
            # 提取品牌
            brand_elem = soup.find('a', {'id': 'bylineInfo'})
            if not brand_elem:
                brand_elem = soup.find('span', {'class': re.compile(r'.*brand.*', re.I)})
            product_data['brand'] = brand_elem.get_text(strip=True) if brand_elem else ""
            
            # 提取评分
            rating_elem = soup.find('span', {'id': 'acrPopover'})
            if rating_elem:
                rating_match = re.search(r'(\d+\.?\d*)', rating_elem.get('title') or '')
                product_data['rating'] = float(rating_match.group(1)) if rating_match else 0.0
            else:
                product_data['rating'] = 0.0
            
            # 提取评价数
            review_count_elem = soup.find('span', {'id': 'acrCustomerReviewText'})
            if review_count_elem:
                count_match = re.search(r'(\d+(?:,\d+)*)', review_count_elem.get_text())
                product_data['review_count'] = int(count_match.group(1).replace(',', '')) if count_match else 0
            else:
                product_data['review_count'] = 0
            
            # 提取价格
            price_elem = soup.find('span', {'class': re.compile(r'.*price.*', re.I)})
            if not price_elem:
                price_elem = soup.find('span', {'id': re.compile(r'.*price.*', re.I)})
            product_data['price'] = price_elem.get_text(strip=True) if price_elem else ""
            
            # 提取图片URL
            img_urls = []
            img_div = soup.find(id='altImages') or soup.find('div', {'data-action': 'thumb-grid'})
            if img_div:
                img_tags = img_div.find_all('img')
                for img_tag in img_tags:
                    src = img_tag.get('src') or img_tag.get('data-old-hires') or img_tag.get('data-thumb-url')
                    if src and src.startswith('http'):
                        img_urls.append(src)
            
            # 如果没找到缩略图，尝试找主图
            if not img_urls:
                main_img = soup.find(id='landingImage') or soup.find('img', {'id': 'prodImage'})
                if main_img:
                    src = main_img.get('src') or main_img.get('data-a-dynamic-image')
                    if src:
                        if isinstance(src, str):
                            img_urls.append(src)
                        else:
                            # 如果src是字典形式的动态图片
                            img_urls.extend(list(src.keys()) if isinstance(src, dict) else [])
            
            product_data['image_urls'] = img_urls[:10]  # 限制最多10张图片
            
            # 提取分类信息
            breadcrumb = soup.find('div', {'id': 'wayfinding-breadcrumbs_feature_div'})
            if breadcrumb:
                categories = [a.get_text(strip=True) for a in breadcrumb.find_all('a')]
                product_data['categories'] = categories
            else:
                product_data['categories'] = []
            
            # 添加延迟，避免被反爬虫检测
            time.sleep(random.uniform(1, 3))
            
            return product_data
            
        except requests.RequestException as e:
            print(f"请求错误: {e}")
            return self.get_fallback_data(url)
        except Exception as e:
            print(f"解析错误: {e}")
            return self.get_fallback_data(url)
    
    def get_fallback_data(self, url: str) -> dict:
        """
        获取备用数据（当主要方法失败时）
        """
        print("使用备用方法获取数据...")
        # 这里可以实现其他数据获取方法
        # 或者返回一个基本的结构
        return {
            'title': '无法获取标题',
            'feature_bullets': ['无法获取产品特性'],
            'description': '无法获取产品描述',
            'brand': '未知品牌',
            'rating': 0.0,
            'review_count': 0,
            'price': '价格面议',
            'image_urls': [],
            'categories': []
        }
    
    def validate_asin(self, asin: str) -> bool:
        """
        验证ASIN是否有效
        :param asin: Amazon标准识别号
        :return: 是否有效
        """
        # ASIN通常由字母和数字组成，长度为10位
        pattern = r'^[A-Z0-9]{10}$'
        return bool(re.match(pattern, asin))
    
    def get_product_by_asin(self, asin: str, domain: str = 'www.amazon.com') -> dict:
        """
        通过ASIN获取产品信息
        :param asin: Amazon标准识别号
        :param domain: Amazon域名
        :return: 产品信息
        """
        if not self.validate_asin(asin):
            raise ValueError(f"无效的ASIN: {asin}")
        
        url = f"https://{domain}/dp/{asin}"
        return self.get_product_details(url)
    
    def search_products(self, query: str, max_results: int = 10) -> list:
        """
        搜索产品
        :param query: 搜索关键词
        :param max_results: 最大返回结果数
        :return: 产品列表
        """
        search_url = f"https://www.amazon.com/s?k={query.replace(' ', '+')}"
        
        try:
            response = self.session.get(search_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            products = []
            # 查找产品列表项
            items = soup.find_all('div', {'data-component-type': 's-search-result'})
            
            for item in items[:max_results]:
                product = {}
                
                # 提取产品标题和链接
                title_elem = item.find('h2', class_='a-size-mini')
                if not title_elem:
                    title_elem = item.find('h2', class_='a-size-base')
                
                if title_elem:
                    link_elem = title_elem.find('a')
                    if link_elem:
                        product['title'] = link_elem.get_text(strip=True)
                        product['url'] = 'https://www.amazon.com' + link_elem.get('href', '')
                        product['asin'] = parse_qs(urlparse(product['url']).query).get('pd_rd_i', [''])[0]
                
                # 提取价格
                price_whole = item.find('span', class_='a-price-whole')
                price_fraction = item.find('span', class_='a-price-fraction')
                if price_whole:
                    price = price_whole.get_text().strip()
                    if price_fraction:
                        price += '.' + price_fraction.get_text().strip()
                    product['price'] = price
                
                # 提取评分
                rating_elem = item.find('span', {'class': re.compile(r'a-icon-alt')})
                if rating_elem:
                    rating_match = re.search(r'(\d+\.?\d*)', rating_elem.get_text())
                    if rating_match:
                        product['rating'] = float(rating_match.group(1))
                
                # 提取评价数
                review_elem = item.find('span', {'class': re.compile(r'a-size-base')})
                if review_elem:
                    review_match = re.search(r'(\d+(?:,\d+)*)', review_elem.get_text())
                    if review_match:
                        product['review_count'] = int(review_match.group(1).replace(',', ''))
                
                if product:  # 如果找到了一些信息
                    products.append(product)
                
                if len(products) >= max_results:
                    break
            
            time.sleep(random.uniform(2, 4))  # 避免请求过于频繁
            
            return products
            
        except Exception as e:
            print(f"搜索错误: {e}")
            return []


# 示例使用
if __name__ == "__main__":
    api = AmazonAPI()
    
    # 示例：获取产品信息
    # url = "https://www.amazon.com/dp/B08N5WRWNW"  # 替换为实际的Amazon产品URL
    # product_info = api.get_product_details(url)
    # print(product_info)