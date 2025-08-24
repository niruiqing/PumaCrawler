#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深度JavaScript分析器
专门分析页面中的JavaScript代码来找到尺码和其他动态数据
"""

import requests
from bs4 import BeautifulSoup
import json
import re

def deep_js_analysis(url):
    """深度分析JavaScript中的数据"""
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    }
    
    try:
        print(f"🔍 深度分析JavaScript: {url}")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        print("✅ 页面获取成功，开始深度分析JavaScript...")
        
        script_tags = soup.find_all('script')
        print(f"📊 页面总共找到 {len(script_tags)} 个script标签")
        
        all_data = {
            'product_data': [],
            'size_data': [],
            'variant_data': [],
            'inventory_data': [],
            'raw_objects': []
        }
        
        for i, script in enumerate(script_tags, 1):
            if script.string:
                content = script.string
                print(f"\n🔍 分析第 {i} 个script标签 (长度: {len(content)} 字符)")
                
                # 1. 查找常见的产品数据模式
                product_patterns = [
                    r'window\.__INITIAL_STATE__\s*=\s*({.+?});',
                    r'window\.__NEXT_DATA__\s*=\s*({.+?});',
                    r'window\.productData\s*=\s*({.+?});',
                    r'window\.product\s*=\s*({.+?});',
                    r'var\s+productData\s*=\s*({.+?});',
                    r'const\s+productData\s*=\s*({.+?});',
                    r'let\s+productData\s*=\s*({.+?});',
                ]
                
                for pattern in product_patterns:
                    matches = re.findall(pattern, content, re.DOTALL)
                    for match in matches:
                        try:
                            data = json.loads(match)
                            all_data['product_data'].append({
                                'script_index': i,
                                'pattern': pattern,
                                'data': data
                            })
                            print(f"   ✅ 找到产品数据: {pattern}")
                        except json.JSONDecodeError:
                            print(f"   ❌ JSON解析失败: {pattern}")
                
                # 2. 专门查找尺码相关数据
                size_patterns = [
                    r'"sizes?"\s*:\s*(\[.+?\])',
                    r'"availableSizes?"\s*:\s*(\[.+?\])',
                    r'"sizeOptions?"\s*:\s*(\[.+?\])',
                    r'"variants?"\s*:\s*(\[.+?\])',
                    r'"skus?"\s*:\s*(\[.+?\])',
                    r'"inventory"\s*:\s*({.+?})',
                    r'"stock"\s*:\s*({.+?})',
                ]
                
                for pattern in size_patterns:
                    matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
                    for match in matches:
                        try:
                            if match.startswith('['):
                                data = json.loads(match)
                            else:
                                data = json.loads(match)
                            all_data['size_data'].append({
                                'script_index': i,
                                'pattern': pattern,
                                'data': data
                            })
                            print(f"   ✅ 找到尺码数据: {pattern}")
                        except json.JSONDecodeError:
                            continue
                
                # 3. 查找包含数字的数组（可能是尺码）
                number_array_pattern = r'\[[\s]*(?:\d+\.?\d*[\s]*,?[\s]*)+\]'
                number_arrays = re.findall(number_array_pattern, content)
                for arr in number_arrays:
                    try:
                        data = json.loads(arr)
                        if len(data) > 3 and len(data) < 20:  # 尺码数组通常有3-20个元素
                            all_data['size_data'].append({
                                'script_index': i,
                                'pattern': 'number_array',
                                'data': data
                            })
                            print(f"   ✅ 找到数字数组: {arr[:50]}...")
                    except:
                        continue
                
                # 4. 查找包含"312637"（商品ID）的对象
                if '312637' in content:
                    print(f"   🎯 在第{i}个script中找到商品ID 312637")
                    
                    # 提取包含商品ID的JSON对象
                    id_patterns = [
                        r'({[^{}]*"312637"[^{}]*})',
                        r'({[^{}]*312637[^{}]*})',
                    ]
                    
                    for pattern in id_patterns:
                        matches = re.findall(pattern, content)
                        for match in matches:
                            try:
                                data = json.loads(match)
                                all_data['raw_objects'].append({
                                    'script_index': i,
                                    'type': 'product_id_object',
                                    'data': data
                                })
                                print(f"      ✅ 找到包含商品ID的对象")
                            except:
                                continue
                
                # 5. 查找所有看起来像JSON的大对象
                large_object_pattern = r'({[^{}]{100,}?})'
                large_objects = re.findall(large_object_pattern, content)
                for obj in large_objects[:5]:  # 只取前5个大对象
                    try:
                        data = json.loads(obj)
                        if isinstance(data, dict) and len(data) > 5:
                            # 检查是否包含可能的尺码信息
                            obj_str = json.dumps(data).lower()
                            if any(keyword in obj_str for keyword in ['size', 'variant', 'sku', 'inventory']):
                                all_data['raw_objects'].append({
                                    'script_index': i,
                                    'type': 'large_object_with_size_keywords',
                                    'data': data
                                })
                                print(f"   ✅ 找到包含尺码关键词的大对象")
                    except:
                        continue
        
        # 分析收集到的数据
        print(f"\n📊 数据收集总结:")
        print(f"   产品数据对象: {len(all_data['product_data'])}")
        print(f"   尺码数据对象: {len(all_data['size_data'])}")
        print(f"   原始对象: {len(all_data['raw_objects'])}")
        
        # 提取所有可能的尺码
        extracted_sizes = []
        
        # 从尺码数据中提取
        for item in all_data['size_data']:
            data = item['data']
            if isinstance(data, list):
                for size_item in data:
                    if isinstance(size_item, (int, float, str)):
                        size_str = str(size_item)
                        if size_str not in extracted_sizes and len(size_str) <= 10:
                            extracted_sizes.append(size_str)
                    elif isinstance(size_item, dict):
                        # 查找尺码相关字段
                        for key in ['size', 'value', 'name', 'label', 'code']:
                            if key in size_item:
                                size_str = str(size_item[key])
                                if size_str not in extracted_sizes and len(size_str) <= 10:
                                    extracted_sizes.append(size_str)
        
        # 从原始对象中提取
        for item in all_data['raw_objects']:
            data = item['data']
            if isinstance(data, dict):
                # 递归查找所有可能的尺码字段
                def extract_sizes_from_dict(d, path=""):
                    sizes = []
                    if isinstance(d, dict):
                        for key, value in d.items():
                            if any(size_keyword in key.lower() for size_keyword in ['size', 'variant', 'sku']):
                                if isinstance(value, list):
                                    for v in value:
                                        if isinstance(v, (str, int, float)) and len(str(v)) <= 10:
                                            sizes.append(str(v))
                                elif isinstance(value, (str, int, float)) and len(str(value)) <= 10:
                                    sizes.append(str(value))
                            elif isinstance(value, (dict, list)):
                                sizes.extend(extract_sizes_from_dict(value, f"{path}.{key}"))
                    elif isinstance(d, list):
                        for item in d:
                            sizes.extend(extract_sizes_from_dict(item, path))
                    return sizes
                
                found_sizes = extract_sizes_from_dict(data)
                for size in found_sizes:
                    if size not in extracted_sizes:
                        extracted_sizes.append(size)
        
        print(f"\n🎯 提取到的所有尺码 ({len(extracted_sizes)} 个):")
        for i, size in enumerate(extracted_sizes[:20], 1):
            print(f"  {i}. {size}")
        
        # 保存详细结果
        result = {
            'url': url,
            'total_sizes_found': len(extracted_sizes),
            'extracted_sizes': extracted_sizes,
            'analysis_summary': {
                'product_data_objects': len(all_data['product_data']),
                'size_data_objects': len(all_data['size_data']),
                'raw_objects': len(all_data['raw_objects'])
            },
            'detailed_data': all_data
        }
        
        return result
        
    except Exception as e:
        print(f"❌ 深度分析失败: {e}")
        return {}

def main():
    """主函数"""
    url = "https://us.puma.com/us/en/pd/evospeed-mid-distance-nitro-elite-3-track--field-distance-spikes/312637?swatch=01"
    
    result = deep_js_analysis(url)
    
    if result:
        # 保存完整结果
        with open('deep_js_analysis_result.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 深度JavaScript分析结果已保存到: deep_js_analysis_result.json")

if __name__ == "__main__":
    main()