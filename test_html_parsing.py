#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试longDescription HTML解析功能
"""

import requests
import json

def test_api_with_html_parsing():
    """测试API接口的HTML解析功能"""
    print("🧪 测试API接口的HTML解析功能...")
    
    # 测试URL - 包含详细longDescription的商品
    test_url = "https://us.puma.com/us/en/pd/deviate-nitro-3-womens-running-shoes/309708?swatch=04"
    
    # 调用本地API
    api_url = "http://localhost:5000/api/scrape"
    
    try:
        print(f"📡 发送请求到: {api_url}")
        print(f"🌐 测试商品URL: {test_url}")
        
        response = requests.post(
            api_url,
            json={"url": test_url},
            timeout=60
        )
        
        print(f"📊 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                product = data.get('product', {})
                current_variation = product.get('current_variation', {})
                
                print("✅ 成功获取商品信息!")
                print(f"📦 商品名称: {product.get('basic_info', {}).get('name', 'N/A')}")
                
                # 检查longDescription相关字段
                print("\n🔍 检查longDescription相关字段:")
                
                # 原始HTML内容
                if 'longDescription_raw' in current_variation:
                    html_content = current_variation['longDescription_raw']
                    print(f"✅ 原始HTML内容: {len(html_content)} 字符")
                    print(f"   前100字符: {html_content[:100]}...")
                else:
                    print("❌ 未找到longDescription_raw字段")
                
                # 纯文本内容
                if 'longDescription_text' in current_variation:
                    text_content = current_variation['longDescription_text']
                    print(f"✅ 纯文本内容: {len(text_content)} 字符")
                    print(f"   前100字符: {text_content[:100]}...")
                else:
                    print("❌ 未找到longDescription_text字段")
                
                # 解析后的结构化内容
                if 'parsed_long_description' in current_variation:
                    parsed_content = current_variation['parsed_long_description']
                    print(f"✅ 解析后的结构化内容: {len(parsed_content)} 个章节")
                    
                    for section_title, section_data in parsed_content.items():
                        print(f"\n📋 章节: {section_title}")
                        if section_data.get('text'):
                            print(f"   文本: {section_data['text'][:100]}...")
                        if section_data.get('list_items'):
                            print(f"   列表项: {len(section_data['list_items'])} 个")
                            for i, item in enumerate(section_data['list_items'][:3], 1):
                                print(f"     {i}. {item[:80]}...")
                else:
                    print("❌ 未找到parsed_long_description字段")
                
                return True
            else:
                error = data.get('error', '未知错误')
                print(f"❌ API返回错误: {error}")
                return False
        else:
            print(f"❌ HTTP请求失败: {response.status_code}")
            print(f"响应内容: {response.text[:500]}...")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        return False

def test_html_parsing_function():
    """测试HTML解析函数"""
    print("\n🧪 测试HTML解析函数...")
    
    # 模拟HTML内容
    test_html = '''<h3>PRODUCT STORY</h3>Optimized for a wide range of foot strikes and patterns, Deviate 3 is a super-fast, ultra-responsive running shoe for any runner.<h3>FEATURES &amp; BENEFITS</h3><ul><li>The upper of the shoes is made with at least 20% recycled materials</li><li>NITROFOAM™: Advanced nitrogen-infused foam</li></ul><h3>DETAILS</h3><ul><li>Regular fit</li><li>Engineered mesh upper</li></ul>'''
    
    # 导入解析函数（需要先加载app.py的函数）
    try:
        import sys
        import os
        sys.path.insert(0, '.')
        from app import parse_long_description_html
        
        result = parse_long_description_html(test_html)
        
        print("✅ HTML解析测试成功!")
        print(f"📊 解析结果: {len(result)} 个章节")
        
        for title, data in result.items():
            print(f"\n📋 {title}:")
            if data.get('text'):
                print(f"   文本: {data['text'][:100]}...")
            if data.get('list_items'):
                print(f"   列表项数量: {len(data['list_items'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ HTML解析测试失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 开始longDescription HTML解析功能测试...")
    
    # 测试HTML解析函数
    html_test = test_html_parsing_function()
    
    # 测试API接口
    api_test = test_api_with_html_parsing()
    
    print(f"\n📊 测试结果汇总:")
    print(f"   HTML解析函数: {'✅ 通过' if html_test else '❌ 失败'}")
    print(f"   API接口测试: {'✅ 通过' if api_test else '❌ 失败'}")
    
    if html_test and api_test:
        print("\n🎉 所有测试通过！longDescription HTML解析功能正常工作。")
    else:
        print("\n⚠️ 部分测试失败，请检查实现。")