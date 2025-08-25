#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Puma商品信息爬虫
支持多种爬取方法：requests + BeautifulSoup, Selenium
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass, asdict
from typing import Optional, Dict, List
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ProductInfo:
    """商品信息数据类"""
    header: str = ""     # 新增：商品主标题
    sub_header: str = "" # 新增：商品副标题
    name: str = ""
    price: str = ""
    original_price: str = ""
    sale_price: str = ""  # 新增：销售价格
    discount: str = ""    # 新增：折扣信息
    description: str = ""
    color: str = ""
    color_code: str = ""  # 新增：颜色代码
    sizes: List[str] = None
    available_sizes: List[str] = None  # 新增：可用尺码
    unavailable_sizes: List[str] = None  # 新增：缺货尺码
    images: List[str] = None
    product_id: str = ""
    sku: str = ""         # 新增：SKU
    brand: str = "PUMA"   # 新增：品牌
    category: str = ""    # 新增：分类
    subcategory: str = "" # 新增：子分类
    availability: str = ""
    stock_status: str = "" # 新增：详细库存状态
    rating: str = ""
    reviews_count: str = ""
    features: List[str] = None
    materials: List[str] = None      # 新增：材料信息
    care_instructions: List[str] = None  # 新增：护理说明
    size_guide: str = ""             # 新增：尺码指南链接
    tech_specs: Dict[str, str] = None # 新增：技术规格
    badges: List[str] = None         # 新增：商品徽章（如"新品"、"热销"等）
    promotion: str = ""              # 新增：促销信息
    gender: str = ""                 # 新增：性别分类
    age_group: str = ""              # 新增：年龄组（成人/儿童等）
    style_number: str = ""           # 新增：款式编号
    
    def __post_init__(self):
        if self.sizes is None:
            self.sizes = []
        if self.available_sizes is None:
            self.available_sizes = []
        if self.unavailable_sizes is None:
            self.unavailable_sizes = []
        if self.images is None:
            self.images = []
        if self.features is None:
            self.features = []
        if self.materials is None:
            self.materials = []
        if self.care_instructions is None:
            self.care_instructions = []
        if self.tech_specs is None:
            self.tech_specs = {}
        if self.badges is None:
            self.badges = []

class PumaScraper:
    """Puma商品爬虫类"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        self.timeout = 30
    
    def get_page_content(self, url: str, retries: int = 3) -> Optional[BeautifulSoup]:
        """获取页面内容"""
        for attempt in range(retries):
            try:
                logger.info(f"尝试获取页面内容 (第{attempt + 1}次): {url}")
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                logger.info("页面内容获取成功")
                return soup
                
            except requests.exceptions.Timeout:
                logger.warning(f"请求超时 (第{attempt + 1}次)")
                time.sleep(2 ** attempt)  # 指数退避
            except requests.exceptions.RequestException as e:
                logger.error(f"请求异常 (第{attempt + 1}次): {e}")
                time.sleep(2 ** attempt)
            except Exception as e:
                logger.error(f"解析HTML异常: {e}")
                
        logger.error("所有重试都失败了")
        return None
    
    def extract_json_data(self, soup: BeautifulSoup) -> Dict:
        """从页面中提取JSON数据"""
        json_data = {}
        
        # 查找包含产品数据的script标签
        script_tags = soup.find_all('script', type='application/ld+json')
        for script in script_tags:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and '@type' in data:
                    if data.get('@type') == 'Product':
                        json_data.update(data)
                        logger.info("找到Product类型的JSON-LD数据")
            except (json.JSONDecodeError, AttributeError):
                continue
        
        # 查找其他可能包含产品数据的script标签
        script_tags = soup.find_all('script')
        for script in script_tags:
            if script.string:
                # 查找window对象中的产品数据
                if 'window.productData' in script.string or 'window.product' in script.string:
                    try:
                        # 提取JSON数据的正则表达式
                        json_match = re.search(r'window\.(?:productData|product)\s*=\s*({.*?});', script.string, re.DOTALL)
                        if json_match:
                            data = json.loads(json_match.group(1))
                            json_data.update(data)
                            logger.info("找到window对象中的产品数据")
                    except (json.JSONDecodeError, AttributeError):
                        continue
        
        return json_data
    
    def parse_product_info(self, soup: BeautifulSoup, json_data: Dict) -> ProductInfo:
        """解析商品信息"""
        product = ProductInfo()
        
        try:
            # 商品Header和Sub Header - 新增
            header_selectors = [
                'h1[data-testid="product-name"]',
                'h1[data-testid="product-title"]',
                'h1.product-name',
                'h1.pdp-product-name',
                '.product-title h1',
                'h1[class*="product-name"]',
                'h1[class*="ProductName"]',
                'h1[class*="name"]',
                'h1[class*="title"]',
                '.pdp h1',
                'h1',
            ]
            product.header = self._find_text_by_selectors(soup, header_selectors)
            
            # Sub Header 通常在h2或产品描述的第一段
            sub_header_selectors = [
                'h2[data-testid="product-description"]',
                'h2[data-testid="product-subtitle"]',
                '.product-subtitle',
                '.product-description h2',
                '.pdp-description h2',
                'h2[class*="subtitle"]',
                'h2[class*="description"]',
                '.product-tagline',
                '.product-summary',
                'h2',
            ]
            product.sub_header = self._find_text_by_selectors(soup, sub_header_selectors)
            
            # 如果没有找到sub_header，尝试从描述的第一句获取
            if not product.sub_header:
                desc_selectors = [
                    '.product-description p:first-child',
                    '.pdp-description p:first-child',
                    '.product-details p:first-child',
                    '.description p:first-child',
                ]
                desc_text = self._find_text_by_selectors(soup, desc_selectors)
                if desc_text and len(desc_text) < 200:  # 只当做副标题如果不太长
                    product.sub_header = desc_text
            
            # 从 JSON 数据中获取 header 和 sub_header
            if json_data:
                if not product.header:
                    product.header = json_data.get('name', '') or json_data.get('header', '')
                if not product.sub_header:
                    product.sub_header = json_data.get('subHeader', '') or json_data.get('description', '')[:200] if json_data.get('description') else ''
            
            # 商品名称 - 更多选择器
            name_selectors = [
                'h1[data-testid="product-name"]',
                'h1.product-name',
                'h1.pdp-product-name',
                '.product-title h1',
                '[class*="product-name"] h1',
                '[class*="ProductName"] h1',
                'h1[class*="name"]',
                'h1[class*="title"]',
                '.pdp h1',
                'h1',
            ]
            product.name = self._find_text_by_selectors(soup, name_selectors)
            
            # 从JSON数据中获取名称
            if not product.name and json_data:
                product.name = json_data.get('name', '')
            
            # 价格信息 - 更多选择器
            price_selectors = [
                '[data-testid="product-price"]',
                '[data-testid="price"]',
                '.price-current',
                '.current-price',
                '.product-price .price',
                '.price-container .price',
                '.pdp-price',
                '[class*="price"][class*="current"]',
                '[class*="CurrentPrice"]',
                '[class*="Price"]',
                '.price',
                'span[class*="price"]',
                'div[class*="price"]',
            ]
            product.price = self._find_text_by_selectors(soup, price_selectors)
            
            # 从JSON数据中获取价格
            if not product.price and json_data:
                offers = json_data.get('offers', {})
                if isinstance(offers, dict):
                    product.price = offers.get('price', '') or offers.get('lowPrice', '')
                elif isinstance(offers, list) and offers:
                    product.price = offers[0].get('price', '')
            
            # 原价（划线价格）
            original_price_selectors = [
                '.price-original',
                '.price-was',
                '.strikethrough',
                '[data-testid="product-original-price"]',
                '[data-testid="original-price"]',
                '.was-price',
                '.original-price',
                '[class*="was"][class*="price"]',
                '[class*="original"][class*="price"]',
                'del',
                's',
            ]
            product.original_price = self._find_text_by_selectors(soup, original_price_selectors)
            
            # 商品描述
            desc_selectors = [
                '[data-testid="product-description"]',
                '.product-description',
                '.pdp-description',
                '.product-details-description',
                '[class*="description"]',
                '[class*="Description"]',
                '.product-detail p',
                '.description p',
                '.product-copy',
                '.product-details p',
            ]
            product.description = self._find_text_by_selectors(soup, desc_selectors)
            
            # 从JSON数据中获取描述
            if not product.description and json_data:
                product.description = json_data.get('description', '')
            
            # 颜色信息
            color_selectors = [
                '[data-testid="color-name"]',
                '[data-testid="selected-color"]',
                '.color-name',
                '.selected-color',
                '.color-label',
                '[class*="color"][class*="name"]',
                '[class*="selected"][class*="color"]',
                '.color-swatch.selected',
                '.color-option.selected',
                '[class*="Color"][class*="Name"]',
            ]
            product.color = self._find_text_by_selectors(soup, color_selectors)
            
            # 尝试从URL参数获取颜色信息
            if not product.color:
                try:
                    current_url = soup.find('link', rel='canonical')
                    if current_url:
                        href = current_url.get('href', '')
                        if 'swatch=' in href:
                            color_code = href.split('swatch=')[1].split('&')[0]
                            product.color = f"Color Code: {color_code}"
                except:
                    pass
            
            # 尺码信息
            size_elements = soup.find_all(['button', 'span', 'div', 'li', 'option'], attrs={
                'class': re.compile(r'size|Size'),
                'data-testid': re.compile(r'size|Size')
            })
            
            # 添加更多尺码选择器 - 根据实际HTML结构更新
            size_selectors = [
                '#size-picker span[data-content="size-value"]',  # 主要选择器
                '[data-test-id="size-picker"] span[data-content="size-value"]',  # 备用选择器  
                '[id="size-picker"] label span[data-content="size-value"]',  # 更具体的选择器
                'label[data-size] span[data-content="size-value"]',  # 通过data-size属性查找
                '[class*="size"] button',
                '[class*="Size"] button',
                '.size-selector button',
                '.size-option',
                '[data-testid*="size"]',
                'select[name*="size"] option',
                '.sizes li',
            ]
            
            for selector in size_selectors:
                elements = soup.select(selector)
                logger.debug(f"选择器 '{selector}' 找到 {len(elements)} 个尺码元素")
                for element in elements:
                    size_text = element.get_text(strip=True)
                    if size_text and len(size_text) <= 10 and size_text not in product.sizes:
                        # 过滤掉非尺码文本
                        if not any(word in size_text.lower() for word in ['select', 'choose', 'size', '尺码', 'guide']):
                            product.sizes.append(size_text)
                            logger.debug(f"添加尺码: {size_text}")
            
            for element in size_elements:
                size_text = element.get_text(strip=True)
                if size_text and len(size_text) <= 10 and size_text not in product.sizes:
                    if not any(word in size_text.lower() for word in ['select', 'choose', 'size', '尺码', 'guide']):
                        product.sizes.append(size_text)
                        logger.debug(f"从元素添加尺码: {size_text}")
            
            # 记录尺码获取结果
            if product.sizes:
                logger.info(f"找到 {len(product.sizes)} 个尺码: {', '.join(product.sizes)}")
            else:
                # 如果没找到，尝试直接查找size-picker容器
                logger.debug("尝试直接查找size-picker容器...")
                size_picker = soup.find(id='size-picker')
                if not size_picker:
                    size_picker = soup.find(attrs={'data-test-id': 'size-picker'})
                
                if size_picker:
                    logger.info("找到size-picker容器")
                    labels = size_picker.find_all('label')
                    logger.debug(f"容器中找到 {len(labels)} 个尺码标签")
                    
                    for label in labels:
                        size_span = label.find('span', {'data-content': 'size-value'})
                        if size_span:
                            size_text = size_span.get_text(strip=True)
                            is_disabled = label.get('data-disabled') == 'true'
                            
                            if is_disabled:
                                size_display = f"{size_text} (缺货)"
                            else:
                                size_display = size_text
                            
                            if size_display not in product.sizes:
                                product.sizes.append(size_display)
                                logger.debug(f"从容器添加尺码: {size_display}")
                    
                    if product.sizes:
                        logger.info(f"从容器找到 {len(product.sizes)} 个尺码: {', '.join(product.sizes)}")
                    else:
                        logger.warning("即使在size-picker容器中也未找到尺码信息")
                else:
                    logger.warning("未找到尺码信息 - Puma网站可能需要用户交互才会显示尺码")
            
            # 图片信息
            img_selectors = [
                '.product-images img',
                '.pdp-images img',
                '.gallery img',
                '[data-testid="product-image"] img',
                '[class*="product"][class*="image"] img',
                '[class*="Product"][class*="Image"] img',
                '.carousel img',
                '.image-gallery img',
                'img[alt*="product"]',
                'img[alt*="Product"]',
                '.main-image img',
                'img[class*="aspect-1-1"]',  # 新增：Puma网站的正方形图片
                'img[alt*="evoSPEED"]',      # 新增：包含商品名
                'img[alt*="Track"]',        # 新增：包含关键词
                'img[alt*="Field"]',        # 新增：包含关键词
                'img[src*="images.puma.com"]'  # 新增：Puma CDN图片
            ]
            for selector in img_selectors:
                images = soup.select(selector)
                logger.debug(f"选择器 '{selector}' 找到 {len(images)} 张图片")
                
                for img in images:
                    src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                    if src:
                        # 确保是完整URL
                        if src.startswith('//'):
                            full_url = 'https:' + src
                        elif src.startswith('/'):
                            full_url = 'https://us.puma.com' + src
                        elif not src.startswith('http'):
                            full_url = urljoin('https://us.puma.com', src)
                        else:
                            full_url = src
                            
                        # 过滤掉无效图片URL
                        if ('placeholder' not in full_url.lower() and 
                            'default' not in full_url.lower() and
                            'puma.com' in full_url and  # 确保是Puma的图片
                            full_url not in product.images):
                            product.images.append(full_url)
                            logger.debug(f"添加图片: {full_url[:60]}...")
            
            logger.info(f"找到 {len(product.images)} 张商品图片")
            
            # 产品ID
            product.product_id = self._extract_product_id_from_url(soup)
            
            # 库存状态
            availability_selectors = [
                '[data-testid="availability"]',
                '.stock-status',
                '.availability',
                '.inventory-status',
            ]
            product.availability = self._find_text_by_selectors(soup, availability_selectors)
            
            # 评分和评论数
            rating_selectors = [
                '.rating-value',
                '.star-rating',
                '[data-testid="rating"]',
            ]
            product.rating = self._find_text_by_selectors(soup, rating_selectors)
            
            reviews_selectors = [
                '.reviews-count',
                '.review-count',
                '[data-testid="reviews-count"]',
            ]
            product.reviews_count = self._find_text_by_selectors(soup, reviews_selectors)
            
            # 产品特性
            feature_elements = soup.find_all(['li', 'div'], attrs={
                'class': re.compile(r'feature|Feature|benefit|Benefit')
            })
            for element in feature_elements:
                feature_text = element.get_text(strip=True)
                if feature_text and len(feature_text) > 3:
                    product.features.append(feature_text)
            
            # 新增：提取材料信息
            material_selectors = [
                '.material-composition',
                '.materials',
                '.product-materials',
                '[data-testid="materials"]',
                '[class*="material"]',
                '.fabric-details',
                '.composition'
            ]
            material_elements = soup.select(','.join(material_selectors))
            for element in material_elements:
                material_text = element.get_text(strip=True)
                if material_text and len(material_text) > 3:
                    # 分割材料信息（通常用逗号或分号分隔）
                    materials = re.split(r'[,;]', material_text)
                    for material in materials:
                        material = material.strip()
                        if material and material not in product.materials:
                            product.materials.append(material)
            
            # 新增：提取护理说明
            care_selectors = [
                '.care-instructions',
                '.care-guide',
                '.washing-instructions',
                '[data-testid="care"]',
                '[class*="care"]',
                '.product-care'
            ]
            care_elements = soup.select(','.join(care_selectors))
            for element in care_elements:
                care_text = element.get_text(strip=True)
                if care_text and len(care_text) > 3:
                    product.care_instructions.append(care_text)
            
            # 新增：提取技术规格
            spec_selectors = [
                '.tech-specs',
                '.specifications',
                '.product-specs',
                '.technical-details',
                '[data-testid="specs"]'
            ]
            spec_elements = soup.select(','.join(spec_selectors))
            for element in spec_elements:
                # 查找规格项目
                spec_items = element.find_all(['dt', 'dd', 'li', 'tr'])
                current_key = None
                for item in spec_items:
                    text = item.get_text(strip=True)
                    if item.name in ['dt', 'th'] or ':' in text:
                        # 这是规格名称
                        current_key = text.replace(':', '').strip()
                    elif current_key and item.name in ['dd', 'td']:
                        # 这是规格值
                        product.tech_specs[current_key] = text
                        current_key = None
            
            # 新增：从URL和标题提取性别、年龄组信息
            page_title = soup.find('title')
            canonical_url = soup.find('link', rel='canonical')
            text_to_analyze = ""
            
            if page_title:
                text_to_analyze += page_title.get_text().lower() + " "
            if canonical_url:
                text_to_analyze += canonical_url.get('href', '').lower() + " "
            if product.name:
                text_to_analyze += product.name.lower()
            
            # 性别判断
            if 'men' in text_to_analyze and 'women' not in text_to_analyze:
                product.gender = '男性'
            elif 'women' in text_to_analyze and 'men' not in text_to_analyze:
                product.gender = '女性'
            elif 'unisex' in text_to_analyze or 'uni' in text_to_analyze:
                product.gender = '中性'
            
            # 年龄组判断
            if any(word in text_to_analyze for word in ['kid', 'youth', 'junior', 'jr']):
                product.age_group = '儿童/青少年'
            elif any(word in text_to_analyze for word in ['baby', 'infant', 'toddler']):
                product.age_group = '婴儿'
            else:
                product.age_group = '成人'
            
            # 新增：提取商品徽章
            badge_selectors = [
                '.product-badge',
                '.badge',
                '.label',
                '[data-testid="badge"]',
                '[class*="badge"]',
                '[class*="label"]',
                '.new-arrival',
                '.bestseller',
                '.limited-edition',
                '.sale-badge',
                '.promotion-badge'
            ]
            badge_elements = soup.select(','.join(badge_selectors))
            for badge in badge_elements:
                badge_text = badge.get_text(strip=True)
                if badge_text and len(badge_text) < 20 and badge_text not in product.badges:
                    product.badges.append(badge_text)
            
            # 新增：提取促销信息
            promotion_selectors = [
                '.promotion-message',
                '.promo-text',
                '.offer-text',
                '[data-testid="promotion"]',
                '[class*="promotion"]',
                '[class*="offer"]',
                '.sale-message',
                '.discount-message'
            ]
            product.promotion = self._find_text_by_selectors(soup, promotion_selectors)
            
            # 新增：提取销售价格和折扣信息
            sale_price_selectors = [
                '.sale-price',
                '.promo-price',
                '.discount-price',
                '[data-testid="sale-price"]',
                '[class*="sale"][class*="price"]',
                '.special-price'
            ]
            product.sale_price = self._find_text_by_selectors(soup, sale_price_selectors)
            
            discount_selectors = [
                '.discount-percentage',
                '.save-amount',
                '.discount-amount',
                '[data-testid="discount"]',
                '[class*="discount"][class*="percentage"]',
                '.savings'
            ]
            product.discount = self._find_text_by_selectors(soup, discount_selectors)
            
            # 新增：提取颜色代码
            if not product.color_code:
                try:
                    canonical_url = soup.find('link', rel='canonical')
                    if canonical_url:
                        href = canonical_url.get('href', '')
                        if 'swatch=' in href:
                            product.color_code = href.split('swatch=')[1].split('&')[0]
                except:
                    pass
            
            # 新增：尺码可用性检查
            if product.sizes:
                for size in product.sizes[:]:
                    if '(缺货)' in size or 'sold out' in size.lower():
                        clean_size = size.replace('(缺货)', '').replace('(Sold Out)', '').strip()
                        if clean_size not in product.unavailable_sizes:
                            product.unavailable_sizes.append(clean_size)
                        if size in product.sizes:
                            product.sizes.remove(size)
                    else:
                        if size not in product.available_sizes:
                            product.available_sizes.append(size)
            
            logger.info(f"成功解析商品信息: {product.name}")
            
        except Exception as e:
            logger.error(f"解析商品信息时出错: {e}")
        
        return product
    
    def _find_text_by_selectors(self, soup: BeautifulSoup, selectors: List[str]) -> str:
        """通过多个选择器查找文本"""
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                if text:
                    return text
        return ""
    
    def _extract_product_id_from_url(self, soup: BeautifulSoup) -> str:
        """从URL或页面中提取产品ID"""
        # 尝试从canonical URL中提取
        canonical = soup.find('link', rel='canonical')
        if canonical:
            href = canonical.get('href', '')
            # 从URL中提取数字ID
            match = re.search(r'/(\d+)(?:\?|$)', href)
            if match:
                return match.group(1)
        return ""
    
    def scrape_product(self, url: str) -> Optional[ProductInfo]:
        """爬取商品信息的主要方法"""
        logger.info(f"开始爬取商品: {url}")
        
        # 获取页面内容
        soup = self.get_page_content(url)
        if not soup:
            logger.error("无法获取页面内容")
            return None
        
        # 提取JSON数据
        json_data = self.extract_json_data(soup)
        
        # 解析商品信息
        product = self.parse_product_info(soup, json_data)
        
        return product
    
    def save_to_json(self, product: ProductInfo, filename: str = "product_info.json"):
        """保存商品信息到JSON文件"""
        try:
            output_path = get_output_path(filename)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(product), f, ensure_ascii=False, indent=2)
            logger.info(f"商品信息已保存到 {output_path}")
        except Exception as e:
            logger.error(f"保存文件时出错: {e}")


def main():
    """主函数"""
    url = "https://us.puma.com/us/en/pd/evospeed-mid-distance-nitro-elite-3-track--field-distance-spikes/312637?swatch=01"
    
    scraper = PumaScraper()
    product = scraper.scrape_product(url)
    
    if product:
        print("\n" + "="*50)
        print("商品信息爬取结果")
        print("="*50)
        print(f"商品名称: {product.name}")
        print(f"价格: {product.price}")
        print(f"原价: {product.original_price}")
        print(f"颜色: {product.color}")
        print(f"可用尺码: {', '.join(product.sizes)}")
        print(f"商品ID: {product.product_id}")
        print(f"库存状态: {product.availability}")
        print(f"评分: {product.rating}")
        print(f"评论数: {product.reviews_count}")
        print(f"图片数量: {len(product.images)}")
        print(f"产品特性: {len(product.features)}个")
        print(f"描述: {product.description[:100]}..." if len(product.description) > 100 else f"描述: {product.description}")
        
        # 保存到文件
        scraper.save_to_json(product)
        
        # 详细信息
        if product.features:
            print(f"\n产品特性:")
            for i, feature in enumerate(product.features[:5], 1):
                print(f"  {i}. {feature}")
        
        if product.images:
            print(f"\n图片链接 (前3个):")
            for i, img in enumerate(product.images[:3], 1):
                print(f"  {i}. {img}")
    else:
        print("爬取失败")


if __name__ == "__main__":
    main()