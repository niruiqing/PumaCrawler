#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试导航信息提取功能
"""

import sys
import os
import requests
import re

# 添加src目录到Python路径
src_path = os.path.join(os.path.dirname(__file__), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

def debug_html_content():
    """调试页面HTML内容"""
    print("🔍 开始调试页面HTML内容...")
    
    test_url = "https://us.puma.com/us/en/pd/suede-xl-leopard-jr-youth/404299?swatch=02"
    
    # 设置浏览器头部
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive"
    }
    
    # 获取页面HTML
    response = requests.get(test_url, headers=headers, timeout=30)
    
    if response.status_code != 200:
        print(f"❌ 无法获取页面: {response.status_code}")
        return
    
    html_content = response.text
    print(f"✅ 成功获取页面HTML，长度: {len(html_content)}")
    
    # 搜索面包屑导航相关的内容
    print("\n🔍 搜索面包屑导航相关内容...")
    
    # 1. 搜索breadcrumb相关的标签
    breadcrumb_patterns = [
        r'breadcrumb[^>]*>.*?</[^>]*breadcrumb',
        r'data-test-id[^>]*breadcrumb[^>]*>.*?</nav>',
        r'<nav[^>]*breadcrumb[^>]*>.*?</nav>',
        r'breadcrumb-nav[^>]*>.*?</nav>',
        r'breadcrumb.*?</nav>'
    ]
    
    for i, pattern in enumerate(breadcrumb_patterns, 1):
        matches = re.findall(pattern, html_content, re.DOTALL | re.IGNORECASE)
        if matches:
            print(f"✅ 模式 {i} 找到 {len(matches)} 个匹配项")
            for j, match in enumerate(matches[:2], 1):  # 只显示前2个匹配项
                print(f"   匹配项 {j}: {match[:200]}...")
        else:
            print(f"❌ 模式 {i} 无匹配")
    
    # 2. 搜索data-test-id属性
    print("\n🔍 搜索data-test-id属性...")
    test_id_pattern = r'data-test-id="[^"]*"'
    test_ids = re.findall(test_id_pattern, html_content, re.IGNORECASE)
    
    breadcrumb_test_ids = [tid for tid in test_ids if 'breadcrumb' in tid.lower()]
    if breadcrumb_test_ids:
        print(f"✅ 找到 {len(breadcrumb_test_ids)} 个breadcrumb相关的test-id:")
        for tid in breadcrumb_test_ids[:5]:
            print(f"   - {tid}")
    else:
        print("❌ 未找到breadcrumb相关的test-id")
    
    # 显示所有test-id（前20个）
    print(f"\n📋 页面中的所有data-test-id（前20个）:")
    for tid in test_ids[:20]:
        print(f"   - {tid}")
    
    # 3. 搜索导航相关的内容
    print("\n🔍 搜索导航相关内容...")
    nav_patterns = [
        r'<nav[^>]*>.*?</nav>',
        r'navigation[^>]*>.*?</[^>]*navigation',
        r'Home.*?Men.*?Shoes'
    ]
    
    for i, pattern in enumerate(nav_patterns, 1):
        matches = re.findall(pattern, html_content, re.DOTALL | re.IGNORECASE)
        if matches:
            print(f"✅ 导航模式 {i} 找到 {len(matches)} 个匹配项")
            for j, match in enumerate(matches[:2], 1):
                print(f"   导航匹配项 {j}: {match[:300]}...")
        else:
            print(f"❌ 导航模式 {i} 无匹配")
    
    # 4. 搜索面包屑关键词
    print("\n🔍 搜索面包屑关键词...")
    keywords = ['Home', 'Men', 'Women', 'Kids', 'Shoes', 'Sneakers', 'Suede']
    
    for keyword in keywords:
        pattern = rf'\b{keyword}\b'
        matches = re.findall(pattern, html_content, re.IGNORECASE)
        if matches:
            print(f"✅ 找到关键词 '{keyword}': {len(matches)} 次")
        else:
            print(f"❌ 未找到关键词 '{keyword}'")
    
    # 5. 保存HTML片段到文件以供进一步分析
    print("\n💾 保存HTML片段...")
    
    # 查找包含 Home 和 Men 的区域
    home_men_pattern = r'.{0,500}Home.{0,200}Men.{0,500}'
    home_men_matches = re.findall(home_men_pattern, html_content, re.DOTALL | re.IGNORECASE)
    
    if home_men_matches:
        print(f"✅ 找到包含Home和Men的区域 {len(home_men_matches)} 个")
        
        with open('debug_breadcrumb_fragments.html', 'w', encoding='utf-8') as f:
            f.write("<!-- 包含Home和Men的HTML片段 -->\n")
            for i, match in enumerate(home_men_matches[:5], 1):
                f.write(f"\n<!-- 片段 {i} -->\n")
                f.write(match)
                f.write("\n\n")
        
        print("💾 HTML片段已保存到 debug_breadcrumb_fragments.html")
        
        # 显示第一个片段
        print(f"\n📋 第一个包含Home和Men的片段:")
        print(home_men_matches[0][:500])
    else:
        print("❌ 未找到包含Home和Men的区域")

if __name__ == "__main__":
    debug_html_content()