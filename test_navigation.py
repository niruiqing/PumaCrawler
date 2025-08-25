#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试导航信息提取功能
"""

import sys
import os

# 添加src目录到Python路径
src_path = os.path.join(os.path.dirname(__file__), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

def test_navigation_extraction():
    """测试导航信息提取功能"""
    print("🚀 开始测试导航信息提取功能...")
    
    try:
        from new_puma_graphql_api import NewPumaGraphQLAPI
        
        # 创建API客户端
        api_client = NewPumaGraphQLAPI()
        
        # 测试URL
        test_url = "https://us.puma.com/us/en/pd/suede-xl-leopard-jr-youth/404299?swatch=02"
        
        print(f"📝 测试URL: {test_url}")
        
        # 测试导航信息提取
        breadcrumb_items, navigation_path = api_client._extract_breadcrumb_from_html(test_url)
        
        print(f"\n📊 提取结果:")
        print(f"   导航路径: {navigation_path}")
        print(f"   导航项数量: {len(breadcrumb_items)}")
        
        if breadcrumb_items:
            print(f"\n📋 详细导航项:")
            for i, item in enumerate(breadcrumb_items, 1):
                current = " (当前页面)" if item.get('current') else ""
                print(f"   {i}. {item['text']}{current}")
                print(f"      URL: {item.get('url', '无')}")
                print(f"      级别: {item['level']}")
        
        # 测试完整的商品信息获取
        print(f"\n🔍 测试完整商品信息获取...")
        product_info = api_client.scrape_product(test_url)
        
        if product_info:
            print(f"✅ 成功获取商品信息!")
            print(f"   商品名称: {product_info.name}")
            print(f"   导航路径: {product_info.navigation_path}")
            if product_info.breadcrumb:
                print(f"   导航项数: {len(product_info.breadcrumb)}")
                for item in product_info.breadcrumb:
                    print(f"     - {item['text']}")
        else:
            print(f"❌ 获取商品信息失败")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_navigation_extraction()
    if success:
        print(f"\n🎉 导航信息提取功能测试成功!")
    else:
        print(f"\n❌ 导航信息提取功能测试失败")