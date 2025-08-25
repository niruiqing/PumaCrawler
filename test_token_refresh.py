#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试TOKEN自动刷新功能
"""

import sys
import os

# 添加src目录到Python路径
src_path = os.path.join(os.path.dirname(__file__), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from new_puma_graphql_api import NewPumaGraphQLAPI

def test_token_refresh():
    """测试TOKEN自动刷新功能"""
    print("🚀 开始测试TOKEN自动刷新功能...")
    
    # 创建API客户端
    api_client = NewPumaGraphQLAPI()
    
    print(f"📊 当前认证头信息:")
    for key, value in api_client.auth_headers.items():
        print(f"   {key}: {value[:50]}..." if len(str(value)) > 50 else f"   {key}: {value}")
    
    # 测试获取新TOKEN
    print(f"\n🔄 测试获取新TOKEN...")
    success = api_client.get_fresh_token()
    
    if success:
        print(f"✅ TOKEN刷新成功！")
        print(f"📊 新的认证头信息:")
        for key, value in api_client.auth_headers.items():
            print(f"   {key}: {value[:50]}..." if len(str(value)) > 50 else f"   {key}: {value}")
    else:
        print(f"❌ TOKEN刷新失败")
    
    # 测试获取商品信息
    print(f"\n🔍 测试获取商品信息...")
    test_url = "https://us.puma.com/us/en/pd/suede-xl-leopard-jr-youth/404299?swatch=02"
    
    product_info = api_client.scrape_product(test_url)
    
    if product_info:
        print(f"✅ 成功获取商品信息!")
        print(f"   商品名称: {product_info.name}")
        print(f"   商品ID: {product_info.product_id}")
        print(f"   价格: {product_info.price}")
        print(f"   颜色: {product_info.color}")
        print(f"   图片数量: {len(product_info.images)}")
    else:
        print(f"❌ 获取商品信息失败")
    
    return success, product_info

if __name__ == "__main__":
    success, product_info = test_token_refresh()
    
    if success and product_info:
        print(f"\n🎉 TOKEN自动刷新和商品信息获取功能正常!")
    elif success:
        print(f"\n⚠️ TOKEN刷新成功，但商品信息获取失败")
    else:
        print(f"\n❌ TOKEN刷新失败")