#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试 swatch=04 无法匹配的问题
"""

import sys
import os
import json

# 添加src目录到Python路径
src_path = os.path.join(os.path.dirname(__file__), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from new_puma_graphql_api import NewPumaGraphQLAPI

def debug_swatch_04_issue():
    """调试swatch=04匹配问题"""
    print("🔍 开始调试 swatch=04 匹配问题...")
    
    # 创建API客户端
    api_client = NewPumaGraphQLAPI()
    
    # 问题URL
    test_url = "https://us.puma.com/us/en/pd/deviate-nitro-3-womens-running-shoes/309708?swatch=04"
    
    print(f"🌐 测试URL: {test_url}")
    
    # 1. 验证swatch参数提取
    print(f"\n📝 Step 1: 验证swatch参数提取")
    swatch_code = api_client.extract_swatch_from_url(test_url)
    print(f"   提取的swatch: '{swatch_code}'")
    print(f"   swatch类型: {type(swatch_code)}")
    print(f"   swatch长度: {len(swatch_code)}")
    
    # 2. 获取产品ID
    product_id = api_client.extract_product_id(test_url)
    print(f"\n📝 Step 2: 产品ID提取")
    print(f"   产品ID: {product_id}")
    
    if not product_id:
        print("❌ 无法提取产品ID，停止调试")
        return
    
    # 3. 直接获取商品数据进行分析
    print(f"\n📝 Step 3: 获取GraphQL原始数据")
    try:
        # 准备请求头
        request_headers = {**api_client.headers, **api_client.auth_headers}
        request_headers["referer"] = f"https://us.puma.com/us/en/pd/product/{product_id}"
        
        # 准备GraphQL请求数据
        payload = {
            "operationName": "PDP",
            "query": api_client.pdp_query,
            "variables": {"id": product_id}
        }
        
        print(f"📡 发送GraphQL请求...")
        response = api_client.session.post(
            api_client.base_url,
            headers=request_headers,
            json=payload,
            timeout=30
        )
        
        print(f"📊 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if 'data' in data and 'product' in data['data'] and data['data']['product']:
                product_data = data['data']['product']
                variations = product_data.get('variations', [])
                
                print(f"\n📝 Step 4: 分析variations数据")
                print(f"   总variations数量: {len(variations)}")
                
                if variations:
                    print(f"\n   所有variations的colorValue:")
                    for i, var in enumerate(variations):
                        color_value = var.get('colorValue', 'N/A')
                        color_name = var.get('colorName', 'N/A')
                        variant_id = var.get('variantId', 'N/A')
                        print(f"     {i+1}. colorValue='{color_value}' (类型:{type(color_value)}) | colorName='{color_name}' | variantId='{variant_id}'")
                    
                    # 4. 测试匹配逻辑
                    print(f"\n📝 Step 5: 测试匹配逻辑")
                    print(f"   查找swatch='{swatch_code}' (类型:{type(swatch_code)})")
                    
                    found_match = False
                    for i, variation in enumerate(variations):
                        color_value = variation.get('colorValue', '')
                        print(f"   比较: '{color_value}' == '{swatch_code}' ? {color_value == swatch_code}")
                        if color_value == swatch_code:
                            print(f"   ✅ 找到匹配！位置: {i+1}")
                            print(f"       变体信息: {variation.get('name', 'N/A')}")
                            print(f"       variantId: {variation.get('variantId', 'N/A')}")
                            found_match = True
                            break
                    
                    if not found_match:
                        print(f"   ❌ 未找到匹配的变体")
                        
                        # 尝试其他匹配方式
                        print(f"\n📝 Step 6: 尝试其他匹配方式")
                        
                        # 去除前后空格
                        swatch_stripped = swatch_code.strip()
                        print(f"   尝试去除空格: '{swatch_stripped}'")
                        for var in variations:
                            cv = var.get('colorValue', '').strip()
                            if cv == swatch_stripped:
                                print(f"   ✅ 去除空格后匹配成功: '{cv}'")
                                break
                        
                        # 转换为字符串比较
                        swatch_str = str(swatch_code)
                        print(f"   尝试字符串转换: '{swatch_str}'")
                        for var in variations:
                            cv = str(var.get('colorValue', ''))
                            if cv == swatch_str:
                                print(f"   ✅ 字符串转换后匹配成功: '{cv}'")
                                break
                        
                        # 不区分大小写
                        swatch_lower = swatch_code.lower()
                        print(f"   尝试不区分大小写: '{swatch_lower}'")
                        for var in variations:
                            cv = str(var.get('colorValue', '')).lower()
                            if cv == swatch_lower:
                                print(f"   ✅ 不区分大小写匹配成功: '{cv}'")
                                break
                    
                    # 5. 保存原始数据供进一步分析
                    debug_file = "debug_variations_data.json"
                    with open(debug_file, 'w', encoding='utf-8') as f:
                        json.dump({
                            'test_url': test_url,
                            'swatch_code': swatch_code,
                            'product_id': product_id,
                            'variations': variations
                        }, f, ensure_ascii=False, indent=2)
                    print(f"\n💾 原始数据已保存到: {debug_file}")
                        
                else:
                    print(f"❌ 没有找到variations数据")
            else:
                print(f"❌ GraphQL响应中没有product数据")
                if 'errors' in data:
                    print(f"   GraphQL错误: {data['errors']}")
        else:
            print(f"❌ HTTP请求失败: {response.status_code}")
            print(f"   响应内容: {response.text[:500]}...")
            
    except Exception as e:
        print(f"❌ 调试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

def test_manual_matching():
    """手动测试匹配逻辑"""
    print(f"\n🧪 手动测试匹配逻辑...")
    
    # 模拟您提供的数据
    test_variation = {
        "colorValue": "04",
        "colorName": "Pale Plum-Midnight Plum-Sun Stream",
        "variantId": "197670277549"
    }
    
    test_swatch = "04"
    
    print(f"测试数据:")
    print(f"  variation.colorValue = '{test_variation['colorValue']}' (类型: {type(test_variation['colorValue'])})")
    print(f"  swatch = '{test_swatch}' (类型: {type(test_swatch)})")
    print(f"  匹配结果: {test_variation['colorValue'] == test_swatch}")

if __name__ == "__main__":
    # 先做手动测试
    test_manual_matching()
    
    # 再做完整调试
    debug_swatch_04_issue()