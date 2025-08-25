#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Puma API尝试器
尝试找到获取尺码信息的API端点
"""

import requests
import json

def try_puma_apis():
    """尝试常见的Puma API端点来获取尺码信息"""
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Referer': 'https://us.puma.com/us/en/pd/evospeed-mid-distance-nitro-elite-3-track--field-distance-spikes/312637?swatch=01'
    }
    
    product_id = "312637"
    swatch = "01"
    
    # 常见的API端点模式
    api_patterns = [
        f"https://us.puma.com/api/products/{product_id}",
        f"https://us.puma.com/api/product/{product_id}",
        f"https://us.puma.com/api/v1/products/{product_id}",
        f"https://us.puma.com/api/v2/products/{product_id}",
        f"https://us.puma.com/api/products/{product_id}/variants",
        f"https://us.puma.com/api/products/{product_id}/sizes", 
        f"https://us.puma.com/api/products/{product_id}/inventory",
        f"https://us.puma.com/api/products/{product_id}?swatch={swatch}",
        f"https://us.puma.com/api/pdp/{product_id}",
        f"https://us.puma.com/api/pdp/product/{product_id}",
        f"https://us.puma.com/us/en/api/products/{product_id}",
        f"https://us.puma.com/us/en/api/product/{product_id}",
        f"https://api.puma.com/products/{product_id}",
        f"https://api.puma.com/v1/products/{product_id}",
        f"https://api.puma.com/us/products/{product_id}",
    ]
    
    print("🔍 尝试Puma API端点...")
    
    successful_apis = []
    
    for i, api_url in enumerate(api_patterns, 1):
        try:
            print(f"   {i:2d}. 尝试: {api_url}")
            response = requests.get(api_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"       ✅ 成功! 状态码: {response.status_code}")
                    print(f"       📊 数据大小: {len(response.text)} 字符")
                    
                    # 分析返回的数据
                    if isinstance(data, dict):
                        keys = list(data.keys())
                        print(f"       🔑 主要字段: {keys[:10]}")
                        
                        # 查找尺码相关字段
                        size_fields = []
                        for key in keys:
                            if any(size_keyword in key.lower() for size_keyword in ['size', 'variant', 'sku', 'inventory', 'stock']):
                                size_fields.append(key)
                        
                        if size_fields:
                            print(f"       🎯 尺码相关字段: {size_fields}")
                        
                        # 检查是否包含商品ID
                        data_str = json.dumps(data).lower()
                        if product_id in data_str:
                            print(f"       ✅ 包含商品ID {product_id}")
                    
                    successful_apis.append({
                        'url': api_url,
                        'status_code': response.status_code,
                        'data_size': len(response.text),
                        'data': data
                    })
                    
                except json.JSONDecodeError:
                    print(f"       ⚠️  成功但非JSON: {response.status_code} (内容: {response.text[:100]}...)")
                    successful_apis.append({
                        'url': api_url,
                        'status_code': response.status_code,
                        'data_size': len(response.text),
                        'content': response.text[:500]
                    })
            else:
                print(f"       ❌ 失败: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"       ⏰ 超时")
        except requests.exceptions.RequestException as e:
            print(f"       ❌ 请求错误: {e}")
        except Exception as e:
            print(f"       ❌ 其他错误: {e}")
    
    print(f"\n📊 总结: 成功的API端点数量: {len(successful_apis)}")
    
    # 分析成功的API响应中的尺码信息
    all_sizes = []
    
    for api in successful_apis:
        if 'data' in api:
            data = api['data']
            print(f"\n🔍 分析API响应: {api['url']}")
            
            # 递归查找尺码信息
            def find_sizes_in_data(obj, path=""):
                sizes = []
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        current_path = f"{path}.{key}" if path else key
                        
                        # 检查键名是否与尺码相关
                        if any(size_keyword in key.lower() for size_keyword in ['size', 'variant', 'sku', 'inventory']):
                            print(f"   🎯 找到尺码相关字段: {current_path}")
                            if isinstance(value, list):
                                print(f"      📋 数组长度: {len(value)}")
                                for item in value:
                                    if isinstance(item, dict):
                                        # 在字典中查找尺码值
                                        for sub_key in ['size', 'value', 'name', 'label', 'code', 'id']:
                                            if sub_key in item:
                                                size_val = str(item[sub_key])
                                                if len(size_val) <= 10 and size_val not in sizes:
                                                    sizes.append(size_val)
                                                    print(f"         ✅ 尺码: {size_val}")
                                    elif isinstance(item, (str, int, float)):
                                        size_val = str(item)
                                        if len(size_val) <= 10 and size_val not in sizes:
                                            sizes.append(size_val)
                                            print(f"         ✅ 尺码: {size_val}")
                            elif isinstance(value, (str, int, float)):
                                size_val = str(value)
                                if len(size_val) <= 10 and size_val not in sizes:
                                    sizes.append(size_val)
                                    print(f"      ✅ 尺码: {size_val}")
                        
                        # 递归处理嵌套对象
                        if isinstance(value, (dict, list)):
                            sizes.extend(find_sizes_in_data(value, current_path))
                
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        sizes.extend(find_sizes_in_data(item, f"{path}[{i}]"))
                
                return sizes
            
            found_sizes = find_sizes_in_data(data)
            all_sizes.extend(found_sizes)
    
    # 去重
    unique_sizes = list(set(all_sizes))
    
    print(f"\n🎯 所有API中找到的尺码 ({len(unique_sizes)} 个):")
    for i, size in enumerate(unique_sizes, 1):
        print(f"  {i}. {size}")
    
    # 保存结果
    result = {
        'successful_apis': len(successful_apis),
        'total_sizes_found': len(unique_sizes),
        'sizes': unique_sizes,
        'api_responses': successful_apis
    }
    
    with open('api_analysis_result.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ API分析结果已保存到: api_analysis_result.json")
    
    return unique_sizes

def main():
    """主函数"""
    sizes = try_puma_apis()
    
    if sizes:
        print(f"\n🎉 成功找到 {len(sizes)} 个尺码!")
    else:
        print("\n😔 未找到任何尺码信息")

if __name__ == "__main__":
    main()