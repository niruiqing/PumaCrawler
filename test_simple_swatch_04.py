#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试swatch=04的问题
"""

import sys
import os

# 添加src目录到Python路径
src_path = os.path.join(os.path.dirname(__file__), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

def test_simple_swatch_04():
    """简单测试swatch=04"""
    print("🔍 简单测试swatch=04匹配...")
    
    try:
        from new_puma_graphql_api import NewPumaGraphQLAPI
        
        # 创建API客户端
        api_client = NewPumaGraphQLAPI()
        
        # 测试URL
        test_url = "https://us.puma.com/us/en/pd/deviate-nitro-3-womens-running-shoes/309708?swatch=04"
        
        print(f"🌐 测试URL: {test_url}")
        
        # 1. 测试swatch参数提取
        swatch_code = api_client.extract_swatch_from_url(test_url)
        print(f"📋 提取的swatch: '{swatch_code}' (类型: {type(swatch_code)})")
        
        # 2. 测试产品ID提取
        product_id = api_client.extract_product_id(test_url)
        print(f"📋 提取的产品ID: '{product_id}'")
        
        if not product_id:
            print("❌ 无法提取产品ID")
            return
        
        # 3. 测试完整的爬取过程
        print(f"\n📡 开始完整的商品信息获取...")
        product_info = api_client.scrape_product(test_url)
        
        if product_info:
            print(f"\n✅ 成功获取商品信息!")
            print(f"   商品名称: {product_info.name}")
            print(f"   变体ID: {product_info.variant_id}")
            print(f"   颜色名称: {product_info.color_name}")
            print(f"   颜色代码: {product_info.color_value}")
            print(f"   价格: {product_info.price}")
            
            # 验证是否匹配了正确的swatch
            if product_info.color_value == swatch_code:
                print(f"🎯 ✅ swatch匹配成功! colorValue={product_info.color_value} == swatch={swatch_code}")
            else:
                print(f"⚠️ swatch匹配异常: colorValue={product_info.color_value} != swatch={swatch_code}")
        else:
            print(f"❌ 获取商品信息失败")
            
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_swatch_04()