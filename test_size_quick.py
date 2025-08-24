#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试尺码获取功能
"""

import requests
import json
from datetime import datetime

def test_graphql_simple():
    """简化的GraphQL测试"""
    print("🧪 开始简化的GraphQL尺码测试...")
    
    url = "https://us.puma.com/api/graphql"
    product_id = "632782"  # 法拉利Polo衫ID
    
    # 简化的查询
    query = """
    query GetProduct($id: ID!) {
      product(id: $id) {
        id
        variations {
          id
          sizeGroups {
            label
            sizes {
              id
              label
              value
              orderable
              maxOrderableQuantity
            }
          }
        }
      }
    }
    """
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
        'Origin': 'https://us.puma.com',
        'Referer': 'https://us.puma.com/us/en/pd/scuderia-ferrari-sportswear-cs-polo-men/632782',
        'X-Operation-Name': 'GetProduct'
    }
    
    payload = {
        "operationName": "GetProduct",
        "query": query,
        "variables": {"id": product_id}
    }
    
    try:
        print(f"📡 发送GraphQL请求到: {url}")
        print(f"🆔 产品ID: {product_id}")
        
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        
        print(f"📊 响应状态: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if 'errors' in data:
                print(f"❌ GraphQL错误: {data['errors']}")
                return False
            
            if 'data' in data and data['data'] and data['data'].get('product'):
                product = data['data']['product']
                print(f"✅ 成功获取产品数据，产品ID: {product.get('id')}")
                
                # 解析尺码
                sizes_found = []
                if 'variations' in product:
                    for variation in product['variations']:
                        if 'sizeGroups' in variation:
                            for group in variation['sizeGroups']:
                                group_label = group.get('label', '')
                                print(f"   尺码组: {group_label}")
                                
                                for size in group.get('sizes', []):
                                    size_label = size.get('label', '')
                                    orderable = size.get('orderable', False)
                                    status = "✅ 有货" if orderable else "❌ 缺货"
                                    size_info = f"{group_label} {size_label} ({status})"
                                    sizes_found.append(size_info)
                                    print(f"      {size_label}: {status}")
                
                print(f"\n🎉 找到 {len(sizes_found)} 个尺码:")
                for size in sizes_found[:10]:  # 显示前10个
                    print(f"   • {size}")
                
                # 保存结果
                result = {
                    'product_id': product.get('id'),
                    'sizes_count': len(sizes_found),
                    'sizes': sizes_found,
                    'raw_data': data['data'],
                    'tested_at': datetime.now().isoformat()
                }
                
                with open('test_sizes_result.json', 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                
                print(f"\n💾 详细结果已保存到: test_sizes_result.json")
                return True
            else:
                print(f"❌ 响应中没有产品数据")
                print(f"   响应内容: {json.dumps(data, indent=2)[:500]}...")
                return False
        else:
            print(f"❌ API请求失败: {response.status_code}")
            print(f"   响应内容: {response.text[:300]}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"⏰ 请求超时")
        return False
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_page_access():
    """测试页面访问"""
    print("\n🌐 测试页面访问...")
    
    url = "https://us.puma.com/us/en/pd/scuderia-ferrari-sportswear-cs-polo-men/632782?swatch=01"
    
    try:
        response = requests.get(url, timeout=10)
        print(f"📊 页面响应状态: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            print(f"📄 页面内容长度: {len(content)} 字符")
            
            # 查找一些关键词
            keywords = ['632782', 'Ferrari', 'Polo', 'size', 'XS', 'S', 'M', 'L', 'XL']
            found_keywords = []
            
            for keyword in keywords:
                if keyword in content:
                    found_keywords.append(keyword)
            
            print(f"🔍 找到关键词: {', '.join(found_keywords)}")
            return True
        else:
            print(f"❌ 页面访问失败")
            return False
            
    except Exception as e:
        print(f"❌ 页面访问异常: {e}")
        return False

if __name__ == "__main__":
    print("="*50)
    print("🚀 快速尺码获取测试")
    print("="*50)
    
    # 测试页面访问
    page_ok = test_page_access()
    
    # 测试GraphQL
    if page_ok:
        graphql_ok = test_graphql_simple()
        
        if graphql_ok:
            print(f"\n🎉 测试成功！尺码获取功能正常工作")
        else:
            print(f"\n⚠️ GraphQL测试失败，但页面访问正常")
    else:
        print(f"\n❌ 页面访问失败，跳过GraphQL测试")
    
    print("\n" + "="*50)