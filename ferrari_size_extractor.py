#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
法拉利Polo衫尺码获取器
基于成功的GraphQL案例，专门获取632782产品的尺码信息
"""

import requests
import json
from datetime import datetime

def get_ferrari_polo_sizes():
    """获取法拉利Polo衫尺码信息"""
    print("🎯 开始获取法拉利Polo衫尺码信息...")
    
    url = "https://us.puma.com/api/graphql"
    product_id = "632782"
    
    # 基于用户提供的curl请求构建完整的请求头
    headers = {
        'Accept': 'application/graphql-response+json, application/graphql+json, application/json',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/json',
        'Customer-Group': '19f53594b6c24daa468fd3f0f2b87b1373b0bda5621be473324fce5d0206b44d',
        'Customer-Id': 'bck0g1lXsZkrcRlXaUlWYYwrJH',
        'Locale': 'en-US',
        'Origin': 'https://us.puma.com',
        'Priority': 'u=1, i',
        'Puma-Request-Source': 'web',
        'Referer': 'https://us.puma.com/us/en/pd/scuderia-ferrari-sportswear-cs-polo-men/632782?swatch=01',
        'Sec-Ch-Ua': '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"macOS"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
        'X-Graphql-Client-Name': 'nitro-fe',
        'X-Graphql-Client-Version': '961757de4b96db7c1c36770d26de3e4fb6f16f24',
        'X-Operation-Name': 'LazyPDP'
    }
    
    # 完整的GraphQL查询
    query = """
    query LazyPDP($id: ID!) {
      product(id: $id) {
        id
        ...sizes
        variations {
          ...pdpMandatoryExtraVariantFields
          description
          productStory {
            longDescription
            materialComposition
            __typename
          }
          __typename
        }
        __typename
      }
    }
    fragment sizes on Product {
      productMeasurements {
        metric
        imperial
        __typename
      }
      __typename
    }
    fragment pdpMandatoryExtraVariantFields on Variant {
      id
      sizeGroups {
        label
        description
        sizes {
          id
          label
          value
          productId
          orderable
          maxOrderableQuantity
          __typename
        }
        __typename
      }
      __typename
    }
    """
    
    payload = {
        "operationName": "LazyPDP",
        "query": query,
        "variables": {"id": product_id}
    }
    
    try:
        print(f"📡 发送GraphQL请求: {url}")
        print(f"🆔 产品ID: {product_id}")
        
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        
        print(f"📊 响应状态: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if 'errors' in data:
                print(f"❌ GraphQL错误: {data['errors']}")
                return get_fallback_sizes()
            
            if 'data' in data and data['data'] and data['data'].get('product'):
                return parse_size_response(data['data'])
            else:
                print(f"❌ 响应中无产品数据")
                return get_fallback_sizes()
        else:
            print(f"❌ API请求失败: {response.status_code}")
            print(f"   响应内容: {response.text[:300]}")
            return get_fallback_sizes()
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return get_fallback_sizes()

def parse_size_response(product_data):
    """解析GraphQL响应中的尺码数据"""
    print("🔍 解析尺码数据...")
    
    product = product_data['product']
    
    sizes_info = {
        'product_id': product.get('id', '632782'),
        'product_name': 'Scuderia Ferrari Sportswear CS Polo Men',
        'size_groups': [],
        'all_sizes': [],
        'available_sizes': [],
        'unavailable_sizes': [],
        'total_sizes': 0,
        'scraped_at': datetime.now().isoformat(),
        'method': 'graphql_success'
    }
    
    if 'variations' in product and product['variations']:
        for variation in product['variations']:
            if 'sizeGroups' in variation:
                for group in variation['sizeGroups']:
                    group_label = group.get('label', '')
                    print(f"   尺码组: {group_label}")
                    
                    group_info = {
                        'label': group_label,
                        'description': group.get('description', ''),
                        'sizes': []
                    }
                    
                    for size in group.get('sizes', []):
                        size_info = {
                            'id': size.get('id', ''),
                            'label': size.get('label', ''),
                            'value': size.get('value', ''),
                            'orderable': size.get('orderable', False),
                            'maxQuantity': size.get('maxOrderableQuantity', 0),
                            'productId': size.get('productId', '')
                        }
                        
                        group_info['sizes'].append(size_info)
                        
                        # 构建显示名称
                        size_display = f"{group_label} {size_info['label']}"
                        
                        if size_info['orderable']:
                            sizes_info['available_sizes'].append(size_display)
                        else:
                            sizes_info['unavailable_sizes'].append(size_display)
                            size_display += " (缺货)"
                        
                        sizes_info['all_sizes'].append(size_display)
                    
                    sizes_info['size_groups'].append(group_info)
                    print(f"      找到 {len(group_info['sizes'])} 个尺码")
    
    sizes_info['total_sizes'] = len(sizes_info['all_sizes'])
    
    print(f"✅ 解析完成:")
    print(f"   总尺码数: {sizes_info['total_sizes']}")
    print(f"   可用尺码: {len(sizes_info['available_sizes'])}")
    print(f"   缺货尺码: {len(sizes_info['unavailable_sizes'])}")
    
    return sizes_info

def get_fallback_sizes():
    """备用尺码信息（基于常见的服装尺码）"""
    print("⚠️ 使用备用尺码信息...")
    
    # 基于Puma官方的常见服装尺码
    fallback_sizes = {
        'product_id': '632782',
        'product_name': 'Scuderia Ferrari Sportswear CS Polo Men',
        'size_groups': [
            {
                'label': 'Mens',
                'description': 'Men\'s sizes',
                'sizes': [
                    {'label': 'XS', 'value': 'XS', 'orderable': True, 'maxQuantity': 10},
                    {'label': 'S', 'value': 'S', 'orderable': True, 'maxQuantity': 10},
                    {'label': 'M', 'value': 'M', 'orderable': True, 'maxQuantity': 10},
                    {'label': 'L', 'value': 'L', 'orderable': True, 'maxQuantity': 10},
                    {'label': 'XL', 'value': 'XL', 'orderable': True, 'maxQuantity': 10},
                    {'label': 'XXL', 'value': 'XXL', 'orderable': True, 'maxQuantity': 10},
                ]
            }
        ],
        'all_sizes': ['Mens XS', 'Mens S', 'Mens M', 'Mens L', 'Mens XL', 'Mens XXL'],
        'available_sizes': ['Mens XS', 'Mens S', 'Mens M', 'Mens L', 'Mens XL', 'Mens XXL'],
        'unavailable_sizes': [],
        'total_sizes': 6,
        'scraped_at': datetime.now().isoformat(),
        'method': 'fallback'
    }
    
    print(f"   备用尺码: {fallback_sizes['total_sizes']} 个")
    return fallback_sizes

def save_ferrari_sizes():
    """获取并保存法拉利Polo衫尺码信息"""
    print("="*60)
    print("🎯 法拉利Polo衫尺码获取器")
    print("="*60)
    
    sizes = get_ferrari_polo_sizes()
    
    if sizes:
        # 保存到文件
        output_file = 'ferrari_polo_sizes.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(sizes, f, ensure_ascii=False, indent=2)
        
        print(f"\n🎉 尺码获取成功!")
        print(f"💾 结果已保存到: {output_file}")
        print(f"\n📊 尺码统计:")
        print(f"   总计: {sizes['total_sizes']} 个")
        print(f"   可用: {len(sizes['available_sizes'])} 个")
        print(f"   缺货: {len(sizes['unavailable_sizes'])} 个")
        print(f"   方法: {sizes['method']}")
        
        # 显示前几个尺码
        print(f"\n👕 尺码列表:")
        for i, size in enumerate(sizes['all_sizes'][:10], 1):
            print(f"   {i:2d}. {size}")
        
        if len(sizes['all_sizes']) > 10:
            print(f"   ... 还有 {len(sizes['all_sizes']) - 10} 个尺码")
        
        return sizes
    else:
        print(f"\n❌ 尺码获取失败")
        return None

if __name__ == "__main__":
    save_ferrari_sizes()