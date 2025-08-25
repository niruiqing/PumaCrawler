#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Puma商品页面图片分析器
分析页面中的所有图片元素，找出商品图片的位置
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from urllib.parse import urljoin

def analyze_images(url):
    """分析页面中的所有图片"""
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    }
    
    try:
        print(f"🔍 分析页面图片: {url}")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        print("✅ 页面获取成功，开始分析图片...")
        
        # 找到所有img标签
        all_images = soup.find_all('img')
        print(f"📊 页面总共找到 {len(all_images)} 个图片标签")
        
        # 分析图片
        product_images = []
        other_images = []
        
        for i, img in enumerate(all_images, 1):
            img_info = {
                'index': i,
                'src': img.get('src', ''),
                'data_src': img.get('data-src', ''),
                'data_lazy_src': img.get('data-lazy-src', ''),
                'alt': img.get('alt', ''),
                'class': img.get('class', []),
                'id': img.get('id', ''),
                'parent_class': img.parent.get('class', []) if img.parent else [],
                'parent_id': img.parent.get('id', '') if img.parent else '',
                'style': img.get('style', '')
            }
            
            # 判断是否为商品图片
            is_product_img = False
            
            # 检查src属性
            for src_attr in ['src', 'data_src', 'data_lazy_src']:
                src_value = img_info.get(src_attr, '')
                if src_value:
                    # 过滤条件
                    if any(keyword in src_value.lower() for keyword in [
                        'product', 'zoom', 'detail', 'carousel', 'gallery'
                    ]):
                        is_product_img = True
                        break
                    
                    # 检查图片尺寸（通常商品图片比较大）
                    if any(size in src_value for size in ['800', '600', '1000', '1200']):
                        is_product_img = True
                        break
            
            # 检查alt属性
            alt_text = img_info.get('alt', '').lower()
            if any(keyword in alt_text for keyword in [
                'product', 'shoe', 'sneaker', 'puma', 'evospeed', 'nitro'
            ]):
                is_product_img = True
            
            # 检查class属性
            class_list = img_info.get('class', [])
            if any(cls for cls in class_list if any(keyword in cls.lower() for keyword in [
                'product', 'carousel', 'gallery', 'zoom', 'detail'
            ])):
                is_product_img = True
            
            # 检查父元素class
            parent_class = img_info.get('parent_class', [])
            if any(cls for cls in parent_class if any(keyword in cls.lower() for keyword in [
                'product', 'carousel', 'gallery', 'zoom', 'detail', 'images'
            ])):
                is_product_img = True
            
            if is_product_img:
                product_images.append(img_info)
            else:
                other_images.append(img_info)
        
        print(f"✅ 分析完成:")
        print(f"   🖼️  疑似商品图片: {len(product_images)} 个")
        print(f"   🖼️  其他图片: {len(other_images)} 个")
        
        # 显示商品图片详情
        if product_images:
            print(f"\n📋 疑似商品图片详情:")
            for img in product_images[:10]:  # 只显示前10个
                print(f"\n图片 #{img['index']}:")
                print(f"  src: {img['src']}")
                if img['data_src']:
                    print(f"  data-src: {img['data_src']}")
                if img['data_lazy_src']:
                    print(f"  data-lazy-src: {img['data_lazy_src']}")
                print(f"  alt: {img['alt']}")
                print(f"  class: {img['class']}")
                print(f"  parent_class: {img['parent_class']}")
        
        # 分析页面的script标签，寻找图片数据
        print(f"\n🔍 分析JavaScript中的图片数据...")
        script_tags = soup.find_all('script')
        
        image_urls_in_js = []
        for script in script_tags:
            if script.string:
                # 查找图片URL模式
                img_patterns = [
                    r'"(https?://[^"]*\.(jpg|jpeg|png|webp)[^"]*)"',
                    r"'(https?://[^']*\.(jpg|jpeg|png|webp)[^']*)'",
                    r'"(/[^"]*\.(jpg|jpeg|png|webp)[^"]*)"',
                    r"'(/[^']*\.(jpg|jpeg|png|webp)[^']*)'",
                ]
                
                for pattern in img_patterns:
                    matches = re.findall(pattern, script.string, re.IGNORECASE)
                    for match in matches:
                        url_part = match[0] if isinstance(match, tuple) else match
                        if url_part not in image_urls_in_js:
                            image_urls_in_js.append(url_part)
        
        print(f"📊 在JavaScript中找到 {len(image_urls_in_js)} 个图片URL")
        
        # 过滤出可能的商品图片
        js_product_images = []
        for img_url in image_urls_in_js:
            if any(keyword in img_url.lower() for keyword in [
                'product', 'zoom', 'detail', '312637', 'evospeed'
            ]):
                # 构建完整URL
                if img_url.startswith('//'):
                    full_url = 'https:' + img_url
                elif img_url.startswith('/'):
                    full_url = 'https://us.puma.com' + img_url
                elif not img_url.startswith('http'):
                    full_url = urljoin('https://us.puma.com', img_url)
                else:
                    full_url = img_url
                
                if full_url not in js_product_images:
                    js_product_images.append(full_url)
        
        if js_product_images:
            print(f"\n🖼️  JavaScript中的商品图片 ({len(js_product_images)} 个):")
            for i, img_url in enumerate(js_product_images[:10], 1):
                print(f"  {i}. {img_url}")
        
        # 合并所有找到的图片
        all_found_images = []
        
        # 从HTML img标签获取
        for img in product_images:
            for attr in ['src', 'data_src', 'data_lazy_src']:
                url_val = img.get(attr, '')
                if url_val:
                    # 构建完整URL
                    if url_val.startswith('//'):
                        full_url = 'https:' + url_val
                    elif url_val.startswith('/'):
                        full_url = 'https://us.puma.com' + url_val
                    elif not url_val.startswith('http'):
                        full_url = urljoin('https://us.puma.com', url_val)
                    else:
                        full_url = url_val
                    
                    if full_url not in all_found_images:
                        all_found_images.append(full_url)
        
        # 从JavaScript获取
        all_found_images.extend(js_product_images)
        
        # 去重
        all_found_images = list(set(all_found_images))
        
        print(f"\n🎯 最终找到的商品图片 ({len(all_found_images)} 个):")
        for i, img_url in enumerate(all_found_images[:15], 1):
            print(f"  {i}. {img_url}")
        
        return all_found_images
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        return []

def main():
    """主函数"""
    url = "https://us.puma.com/us/en/pd/evospeed-mid-distance-nitro-elite-3-track--field-distance-spikes/312637?swatch=01"
    
    images = analyze_images(url)
    
    if images:
        # 保存分析结果
        result = {
            'url': url,
            'images_found': len(images),
            'images': images,
            'analysis_time': '2025-08-22'
        }
        
        with open('image_analysis_result.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 分析结果已保存到: image_analysis_result.json")
    else:
        print("\n❌ 未找到任何商品图片")

if __name__ == "__main__":
    main()