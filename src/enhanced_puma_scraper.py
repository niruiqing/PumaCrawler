#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版增强Puma商品信息爬虫
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from urllib.parse import urljoin
import logging
from config import get_output_path

logger = logging.getLogger(__name__)

def enhanced_scrape_puma(url):
    """
    增强版Puma商品爬虫
    """
    # 设置请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    }
    
    try:
        print(f"正在获取页面: {url}")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        print("页面获取成功，开始解析...")
        
        # 初始化产品信息
        product_info = {
            'name': '',
            'price': '',
            'currency': 'USD',
            'original_price': '',
            'description': '',
            'color': '',
            'brand': 'PUMA',
            'sizes': [],
            'images': [],
            'product_id': '',
            'availability': '',
            'features': [],
            'url': url
        }
        
        # 提取JSON-LD数据
        json_data = {}
        script_tags = soup.find_all('script', type='application/ld+json')
        for script in script_tags:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and data.get('@type') == 'Product':
                    json_data = data
                    print("找到JSON-LD产品数据")
                    break
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and item.get('@type') == 'Product':
                            json_data = item
                            print("找到JSON-LD产品数据")
                            break
            except:
                continue
        
        # 商品名称
        name_selectors = [
            'h1[data-testid="pdp-product-name"]',
            'h1[data-testid="product-name"]', 
            'h1.pdp-product-name',
            'h1.product-name',
            '.product-title h1',
            'h1'
        ]
        
        for selector in name_selectors:
            element = soup.select_one(selector)
            if element and element.get_text(strip=True):
                product_info['name'] = element.get_text(strip=True)
                break
        
        # 从JSON数据获取名称
        if not product_info['name'] and json_data:
            product_info['name'] = json_data.get('name', '')
        
        # 价格信息
        price_selectors = [
            '[data-testid="current-price"]',
            '[data-testid="price"]',
            '.price-current',
            '.current-price', 
            '.price .value',
            '.pdp-price .price',
            '.price'
        ]
        
        for selector in price_selectors:
            element = soup.select_one(selector)
            if element:
                price_text = element.get_text(strip=True)
                # 提取价格数字
                price_match = re.search(r'\\$?([0-9,]+\\.?[0-9]*)', price_text)
                if price_match:
                    product_info['price'] = price_match.group(1).replace(',', '')
                    break
        
        # 从JSON数据获取价格
        if not product_info['price'] and json_data:
            offers = json_data.get('offers', {})
            if isinstance(offers, dict):
                price = offers.get('price', '') or offers.get('lowPrice', '')
                if price:
                    product_info['price'] = str(price)
                    product_info['currency'] = offers.get('priceCurrency', 'USD')
        
        # 商品描述
        desc_selectors = [
            '[data-testid="pdp-product-description"]',
            '[data-testid="product-description"]',
            '.product-description',
            '.pdp-description',
            '.description'
        ]
        
        for selector in desc_selectors:
            element = soup.select_one(selector)
            if element:
                product_info['description'] = element.get_text(strip=True)
                break
        
        # 从JSON数据获取描述
        if not product_info['description'] and json_data:
            product_info['description'] = json_data.get('description', '')
        
        # 颜色信息
        color_selectors = [
            '[data-testid="color-name"]',
            '[data-testid="selected-color"]',
            '.color-name',
            '.selected-color'
        ]
        
        for selector in color_selectors:
            element = soup.select_one(selector)
            if element:
                product_info['color'] = element.get_text(strip=True)
                break
        
        # 从URL获取颜色代码
        if not product_info['color'] and 'swatch=' in url:
            color_code = url.split('swatch=')[1].split('&')[0]
            product_info['color'] = f"Color Code: {color_code}"
        
        # 产品ID
        match = re.search(r'/(\\d+)(?:\\?|$)', url)
        if match:
            product_info['product_id'] = match.group(1)
        
        # 尺码信息 - 根据实际HTML结构更新选择器
        size_selectors = [
            '#size-picker span[data-content="size-value"]',  # 主要选择器
            '[data-test-id="size-picker"] span[data-content="size-value"]',  # 备用选择器
            '[id="size-picker"] label span[data-content="size-value"]',  # 更具体的选择器
            '[data-test-id="size"] + * span[data-content="size-value"]',  # 通过input元素查找
            'label[data-size] span[data-content="size-value"]',  # 通过data-size属性查找
            '[data-test-id="size-selector"] button',  # 保留原有选择器作为备用
            '.size-selector button', 
            '.sizes button', 
            '.size-option',
            'select[name*="size"] option',
            '[class*="size"] button',
            '[class*="Size"] button'
        ]
        
        print(f"🔍 开始搜索尺码信息...")
        
        found_any_sizes = False
        for selector in size_selectors:
            elements = soup.select(selector)
            print(f"   选择器 '{selector}' 找到 {len(elements)} 个元素")
            
            for element in elements:
                size_text = element.get_text(strip=True)
                if (size_text and len(size_text) <= 10 and 
                    size_text not in product_info['sizes'] and
                    not any(word in size_text.lower() for word in ['select', 'choose', 'guide', '选择', '尺码'])):
                    
                    # 检查是否是禁用的尺码（可选择记录但标注不可用）
                    parent_label = element.find_parent('label')
                    is_disabled = False
                    if parent_label:
                        is_disabled = parent_label.get('data-disabled') == 'true'
                    
                    if is_disabled:
                        size_display = f"{size_text} (缺货)"
                    else:
                        size_display = size_text
                    
                    product_info['sizes'].append(size_display)
                    print(f"   ✅ 添加尺码: {size_display}")
                    found_any_sizes = True
        
        # 如果主要选择器没找到，尝试直接查找size-picker容器
        if not found_any_sizes:
            print(f"   🔍 尝试直接查找size-picker容器...")
            size_picker = soup.find(id='size-picker')
            if not size_picker:
                size_picker = soup.find(attrs={'data-test-id': 'size-picker'})
            
            if size_picker:
                print(f"   ✅ 找到size-picker容器")
                # 查找所有label元素
                labels = size_picker.find_all('label')
                print(f"   📋 容器中找到 {len(labels)} 个尺码标签")
                
                for label in labels:
                    size_span = label.find('span', {'data-content': 'size-value'})
                    if size_span:
                        size_text = size_span.get_text(strip=True)
                        is_disabled = label.get('data-disabled') == 'true'
                        
                        if is_disabled:
                            size_display = f"{size_text} (缺货)"
                        else:
                            size_display = size_text
                        
                        if size_display not in product_info['sizes']:
                            product_info['sizes'].append(size_display)
                            print(f"   ✅ 从容器添加尺码: {size_display}")
                            found_any_sizes = True
        
        # 如果还是没找到，说明原因
        if not found_any_sizes:
            print(f"   ⚠️  未找到尺码信息 - 可能页面结构发生变化或需要JavaScript渲染")
        
        print(f"👟 找到 {len(product_info['sizes'])} 个尺码")
        
        # 图片信息
        img_selectors = [
            '[data-testid="pdp-image-carousel"] img',
            '.product-carousel img',
            '.product-images img',
            '.image-gallery img',
            '.pdp-images img',
            'img[alt*="product"]',
            'img[class*="aspect-1-1"]',  # 新增：正方形商品图片
            'img[alt*="evoSPEED"]',      # 新增：包含商品名的alt
            'img[alt*="Track"]',        # 新增：包含Track的alt
            'img[alt*="Field"]',        # 新增：包含Field的alt
            'img[alt*="Spikes"]',       # 新增：包含Spikes的alt
            'img[src*="312637"]',       # 新增：包含商品ID的src
            'img[src*="images.puma.com"]'  # 新增：Puma官方图片CDN
        ]
        
        print(f"🔍 开始搜索商品图片...")
        
        for selector in img_selectors:
            images = soup.select(selector)
            print(f"   选择器 '{selector}' 找到 {len(images)} 张图片")
            
            for img in images:
                src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                if src:
                    # 构建完整URL
                    if src.startswith('//'):
                        full_url = 'https:' + src
                    elif src.startswith('/'):
                        full_url = 'https://us.puma.com' + src
                    elif not src.startswith('http'):
                        full_url = urljoin('https://us.puma.com', src)
                    else:
                        full_url = src
                    
                    # 过滤无效图片
                    if ('placeholder' not in full_url.lower() and 
                        'default' not in full_url.lower() and
                        full_url not in product_info['images'] and
                        # Puma图片有特殊格式，不使用传统扩展名
                        'puma.com' in full_url):
                        product_info['images'].append(full_url)
                        print(f"   ✅ 添加图片: {full_url[:80]}...")
        
        print(f"🖼️  总共找到 {len(product_info['images'])} 张商品图片")
        
        # 产品特性
        feature_selectors = [
            '.product-features li',
            '.features li',
            '.benefits li',
            '.highlights li'
        ]
        
        for selector in feature_selectors:
            elements = soup.select(selector)
            for element in elements:
                feature_text = element.get_text(strip=True)
                if feature_text and len(feature_text) > 3:
                    product_info['features'].append(feature_text)
        
        # 库存状态
        availability_selectors = [
            '[data-testid="availability"]',
            '.availability',
            '.stock-status'
        ]
        
        for selector in availability_selectors:
            element = soup.select_one(selector)
            if element:
                product_info['availability'] = element.get_text(strip=True)
                break
        
        print(f"成功解析商品: {product_info['name']}")
        return product_info
        
    except Exception as e:
        print(f"爬取失败: {e}")
        return None


def print_product_info(product):
    """打印商品信息"""
    if not product:
        print("❌ 没有获取到商品信息")
        return
    
    print("\\n" + "="*60)
    print("🛍️  增强版PUMA商品信息")
    print("="*60)
    print(f"📦 商品名称: {product['name']}")
    print(f"🏷️  品牌: {product['brand']}")
    
    if product['price']:
        print(f"💰 价格: {product['currency']} ${product['price']}")
    else:
        print("💰 价格: N/A")
    
    if product['color']:
        print(f"🎨 颜色: {product['color']}")
    
    print(f"🆔 商品ID: {product['product_id']}")
    
    if product['availability']:
        print(f"📦 库存状态: {product['availability']}")
    
    if product['sizes']:
        print(f"👟 可用尺码 ({len(product['sizes'])}个): {', '.join(product['sizes'][:10])}")
        if len(product['sizes']) > 10:
            print(f"    ... 还有{len(product['sizes']) - 10}个尺码")
    
    print(f"🖼️  图片数量: {len(product['images'])}张")
    
    if product['features']:
        print(f"✨ 产品特性 ({len(product['features'])}个):")
        for i, feature in enumerate(product['features'][:3], 1):
            print(f"   {i}. {feature}")
        if len(product['features']) > 3:
            print(f"   ... 还有{len(product['features']) - 3}个特性")
    
    if product['description']:
        desc_preview = product['description'][:200] + "..." if len(product['description']) > 200 else product['description']
        print(f"📝 商品描述: {desc_preview}")
    
    print("="*60)


def save_to_json(product, filename="enhanced_puma_product.json"):
    """保存到JSON文件"""
    try:
        output_path = get_output_path(filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(product, f, ensure_ascii=False, indent=2)
        print(f"✅ 商品信息已保存到: {output_path}")
    except Exception as e:
        print(f"❌ 保存失败: {e}")


def main():
    """主函数"""
    url = "https://us.puma.com/us/en/pd/evospeed-mid-distance-nitro-elite-3-track--field-distance-spikes/312637?swatch=01"
    
    # 爬取商品信息
    product = enhanced_scrape_puma(url)
    
    # 显示结果
    print_product_info(product)
    
    # 保存到文件
    if product:
        save_to_json(product)
        
        # 显示图片链接
        if product['images']:
            print(f"\\n🖼️  图片链接 (前5个):")
            for i, img in enumerate(product['images'][:5], 1):
                print(f"  {i}. {img}")


if __name__ == "__main__":
    main()