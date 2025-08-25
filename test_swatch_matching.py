#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试swatch参数匹配功能
"""

import sys
import os

# 添加src目录到Python路径
src_path = os.path.join(os.path.dirname(__file__), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from working_complete_graphql_api import WorkingCompleteGraphQLAPI

def test_swatch_matching():
    """测试swatch参数匹配功能"""
    print("🚀 开始测试swatch参数匹配功能...")
    
    # 创建API客户端
    api_client = WorkingCompleteGraphQLAPI()
    
    # 测试URL列表（不同swatch参数）
    test_urls = [
        "https://us.puma.com/us/en/pd/deviate-nitro-3-womens-running-shoes/309708?swatch=04",
        "https://us.puma.com/us/en/pd/deviate-nitro-3-womens-running-shoes/309708?swatch=01",
        "https://us.puma.com/us/en/pd/deviate-nitro-3-womens-running-shoes/309708?swatch=02",
    ]
    
    for i, test_url in enumerate(test_urls, 1):
        print(f"\n{'='*60}")
        print(f"🔍 测试 {i}: {test_url}")
        print(f"{'='*60}")
        
        # 提取产品ID和swatch参数
        product_id = api_client.extract_product_id_from_url(test_url)
        swatch_code = api_client.extract_swatch_from_url(test_url)
        
        print(f"📊 提取信息:")
        print(f"   产品ID: {product_id}")
        print(f"   Swatch参数: {swatch_code}")
        
        # 获取商品信息
        print(f"\n📡 开始获取商品信息...")
        product_info = api_client.scrape_product_from_url(test_url)
        
        if product_info:
            print(f"\n✅ 成功获取商品信息:")
            print(f"   商品名称: {product_info.name}")
            print(f"   选中的变体ID: {product_info.variant_id}")
            print(f"   颜色名称: {product_info.color_name}")
            print(f"   颜色代码: {product_info.color_value}")
            print(f"   价格: {product_info.price}")
            
            # 显示当前变体信息
            if hasattr(product_info, 'current_variation') and product_info.current_variation:
                current_var = product_info.current_variation
                print(f"\n🎯 当前变体详细信息:")
                print(f"   变体ID: {current_var.get('variantId', 'N/A')}")
                print(f"   变体名称: {current_var.get('name', 'N/A')}")
                print(f"   颜色名称: {current_var.get('colorName', 'N/A')}")
                print(f"   颜色代码: {current_var.get('colorValue', 'N/A')}")
                print(f"   价格: {current_var.get('price', 'N/A')}")
                print(f"   可订购: {current_var.get('orderable', 'N/A')}")
            
            # 显示所有变体信息（用于对比）
            if hasattr(product_info, 'all_variations') and product_info.all_variations:
                print(f"\n📋 所有变体信息 (共{len(product_info.all_variations)}个):")
                for j, var in enumerate(product_info.all_variations, 1):
                    is_current = var.get('colorValue') == swatch_code
                    marker = "👉 " if is_current else "   "
                    print(f"{marker}{j}. 变体ID: {var.get('variantId', 'N/A')}, 颜色: {var.get('colorName', 'N/A')} ({var.get('colorValue', 'N/A')})")
        else:
            print(f"❌ 获取商品信息失败")
    
    print(f"\n🎉 测试完成！")

if __name__ == "__main__":
    test_swatch_matching()