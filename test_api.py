#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API调试测试脚本
"""

import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_api():
    print("🔍 开始测试API...")
    
    try:
        # 测试导入
        print("📦 测试导入working_complete_graphql_api...")
        from working_complete_graphql_api import WorkingCompleteGraphQLAPI
        print("✅ 成功导入WorkingCompleteGraphQLAPI")
        
        # 创建客户端
        print("🔧 创建API客户端...")
        client = WorkingCompleteGraphQLAPI()
        print("✅ 成功创建API客户端")
        
        # 测试URL
        test_url = "https://us.puma.com/us/en/pd/suede-xl-leopard-jr-youth/404299?swatch=02"
        print(f"🌐 测试URL: {test_url}")
        
        # 提取产品ID
        product_id = client.extract_product_id_from_url(test_url)
        print(f"🆔 提取的产品ID: {product_id}")
        
        if not product_id:
            print("❌ 无法提取产品ID")
            return False
        
        # 测试API调用
        print("📡 开始API调用...")
        result = client.get_complete_product_info(product_id, test_url)
        
        if result:
            print(f"✅ 成功获取商品信息: {result.name}")
            print(f"💰 价格: {result.price}")
            print(f"🎨 颜色: {result.color_name}")
            print(f"🖼️ 图片数量: {len(result.images)}")
            return True
        else:
            print("❌ 未能获取商品信息")
            return False
            
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_basic_request():
    print("\n🔍 测试基本网络请求...")
    try:
        import requests
        response = requests.get("https://us.puma.com", timeout=10)
        print(f"✅ PUMA官网响应状态: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ 网络请求失败: {e}")
        return False

def test_graphql_endpoint():
    print("\n🔍 测试GraphQL端点...")
    try:
        import requests
        
        headers = {
            'accept': 'application/json',
            'content-type': 'application/json',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # 简单的健康检查查询
        test_query = {
            "query": "{ __typename }"
        }
        
        response = requests.post(
            "https://us.puma.com/api/graphql",
            headers=headers,
            json=test_query,
            timeout=10
        )
        
        print(f"GraphQL端点响应状态: {response.status_code}")
        if response.status_code == 200:
            print("✅ GraphQL端点可访问")
            return True
        else:
            print(f"⚠️ GraphQL端点响应异常: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ GraphQL端点测试失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 开始API诊断测试...\n")
    
    # 基本网络测试
    network_ok = test_basic_request()
    
    # GraphQL端点测试
    graphql_ok = test_graphql_endpoint()
    
    # API功能测试
    api_ok = test_api()
    
    print("\n📊 测试结果汇总:")
    print(f"   网络连接: {'✅' if network_ok else '❌'}")
    print(f"   GraphQL端点: {'✅' if graphql_ok else '❌'}")
    print(f"   API功能: {'✅' if api_ok else '❌'}")
    
    if all([network_ok, graphql_ok, api_ok]):
        print("\n🎉 所有测试通过！API应该可以正常工作。")
    else:
        print("\n⚠️ 发现问题，需要进一步调查。")