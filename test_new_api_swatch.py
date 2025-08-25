#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 new_puma_graphql_api.py 中的 swatch 参数匹配功能
"""

import sys
import os

# 添加src目录到Python路径
src_path = os.path.join(os.path.dirname(__file__), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from new_puma_graphql_api import NewPumaGraphQLAPI

def test_new_api_swatch_matching():
    """测试新API的swatch参数匹配功能"""
    print("🚀 开始测试 NewPumaGraphQLAPI 的 swatch 参数匹配功能...")
    
    # 创建API客户端
    api_client = NewPumaGraphQLAPI()
    
    # 测试URL列表（不同swatch参数）
    test_urls = [
        "https://us.puma.com/us/en/pd/deviate-nitro-3-womens-running-shoes/309708?swatch=04",
        "https://us.puma.com/us/en/pd/deviate-nitro-3-womens-running-shoes/309708?swatch=01", 
        "https://us.puma.com/us/en/pd/suede-xl-leopard-jr-youth/404299?swatch=02",
    ]
    
    for i, test_url in enumerate(test_urls, 1):
        print(f"\n{'='*60}")
        print(f"🔍 测试 {i}: {test_url}")
        print(f"{'='*60}")
        
        # 提取产品ID和swatch参数
        product_id = api_client.extract_product_id(test_url)
        swatch_code = api_client.extract_swatch_from_url(test_url)
        
        print(f"📊 提取信息:")
        print(f"   产品ID: {product_id}")
        print(f"   Swatch参数: {swatch_code}")
        
        if not product_id:
            print(f"❌ 无法提取产品ID，跳过此测试")
            continue
        
        # 获取商品信息
        print(f"\n📡 开始获取商品信息...")
        product_info = api_client.scrape_product(test_url)
        
        if product_info:
            print(f"\n✅ 成功获取商品信息:")
            print(f"   商品名称: {product_info.name}")
            print(f"   选中的变体ID: {product_info.variant_id}")
            print(f"   颜色名称: {product_info.color_name}")
            print(f"   颜色代码: {product_info.color_value}")
            print(f"   价格: {product_info.price}")
            print(f"   图片数量: {len(product_info.images)}")
            
            # 验证swatch匹配是否正确
            if swatch_code and product_info.color_value:
                if product_info.color_value == swatch_code:
                    print(f"🎯 ✅ swatch匹配正确！URL中的swatch={swatch_code} 与变体的colorValue={product_info.color_value} 一致")
                else:
                    print(f"⚠️ swatch匹配可能有问题：URL中的swatch={swatch_code}，但变体的colorValue={product_info.color_value}")
            else:
                print(f"ℹ️ 无法验证swatch匹配（swatch_code={swatch_code}, color_value={product_info.color_value}）")
                
        else:
            print(f"❌ 获取商品信息失败")
    
    print(f"\n🎉 NewPumaGraphQLAPI swatch匹配测试完成！")

def test_swatch_extraction():
    """单独测试swatch参数提取功能"""
    print(f"\n🔧 测试swatch参数提取功能...")
    
    api_client = NewPumaGraphQLAPI()
    
    test_cases = [
        "https://us.puma.com/us/en/pd/deviate-nitro-3-womens-running-shoes/309708?swatch=04",
        "https://us.puma.com/us/en/pd/suede-xl-leopard-jr-youth/404299?swatch=02",
        "https://us.puma.com/us/en/pd/some-product/123456?swatch=10&other=param",
        "https://us.puma.com/us/en/pd/no-swatch-product/789012",  # 没有swatch参数
    ]
    
    for url in test_cases:
        swatch = api_client.extract_swatch_from_url(url)
        print(f"   URL: {url}")
        print(f"   提取的swatch: '{swatch}'")
        print()

if __name__ == "__main__":
    # 先测试参数提取功能
    test_swatch_extraction()
    
    # 再测试完整的swatch匹配功能
    test_new_api_swatch_matching()