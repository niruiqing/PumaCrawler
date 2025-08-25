#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PUMA TOKEN 更新指南

当前TOKEN已过期，需要获取新的认证信息。
按照以下步骤获取新的token：

## 方法1：通过浏览器开发者工具获取

1. 打开Chrome浏览器，访问 https://us.puma.com
2. 按F12打开开发者工具
3. 切换到Network（网络）标签页
4. 刷新页面或点击任意商品
5. 在Network面板中查找GraphQL请求（通常是对 /api/graphql 的POST请求）
6. 点击该请求，查看Request Headers部分
7. 复制以下头部信息：
   - authorization: Bearer xxxxx
   - customer-group: xxxxx
   - customer-id: xxxxx
   - refresh-token: xxxxx
   - bloomreach-id: xxxxx

## 方法2：直接使用更新脚本

运行以下命令获取新token：
```
python get_new_token.py
```

## 更新步骤

将获取到的新token更新到 new_puma_graphql_api.py 文件中的 auth_headers 部分：

```python
self.auth_headers = {
    "authorization": "Bearer 新的token",
    "customer-group": "新的customer-group",
    "customer-id": "新的customer-id", 
    "refresh-token": "新的refresh-token",
    "bloomreach-id": "新的bloomreach-id"
}
```

## 当前TOKEN信息
过期时间: 2025-08-25 12:26:57 (已过期)
需要更新认证信息才能继续使用GraphQL API
"""

import requests
import json
import re
from datetime import datetime

def get_new_puma_token():
    """自动获取新的PUMA token"""
    print("🔍 正在尝试获取新的PUMA token...")
    
    session = requests.Session()
    
    # 设置浏览器头部
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    
    try:
        # 1. 访问首页
        print("📝 Step 1: 访问PUMA首页...")
        homepage = session.get("https://us.puma.com/us/en", headers=headers, timeout=30)
        print(f"   首页状态码: {homepage.status_code}")
        
        if homepage.status_code != 200:
            print("❌ 无法访问PUMA首页")
            return None
        
        # 2. 尝试访问任意商品页面触发token生成
        print("📝 Step 2: 访问商品页面...")
        product_url = "https://us.puma.com/us/en/pd/suede-xl-super-puma-jr-youth/403380"
        product_page = session.get(product_url, headers=headers, timeout=30)
        print(f"   商品页面状态码: {product_page.status_code}")
        
        # 3. 查找页面中的JavaScript配置
        print("📝 Step 3: 分析页面内容...")
        content = product_page.text
        
        # 查找可能的token配置
        patterns = [
            r'"authorization":\s*"([^"]+)"',
            r'"Bearer\s+([A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+)"',
            r'bearer["\']?\s*:\s*["\']([A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+)["\']',
        ]
        
        found_tokens = []
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            found_tokens.extend(matches)
        
        if found_tokens:
            print(f"✅ 找到 {len(found_tokens)} 个可能的token")
            for i, token in enumerate(found_tokens):
                if token.startswith('Bearer '):
                    token = token[7:]
                print(f"   Token {i+1}: {token[:50]}...")
            return found_tokens[0] if found_tokens[0].startswith('Bearer ') else f"Bearer {found_tokens[0]}"
        else:
            print("⚠️ 未在页面中找到token")
            
        # 4. 尝试通过API端点获取
        print("📝 Step 4: 尝试通过API获取token...")
        api_response = session.post(
            "https://us.puma.com/api/graphql",
            headers={
                **headers,
                "Content-Type": "application/json",
                "x-graphql-client-name": "nitro-fe",
            },
            json={
                "operationName": "GetBasicInfo", 
                "query": "query GetBasicInfo { __typename }"
            },
            timeout=30
        )
        
        print(f"   API响应状态码: {api_response.status_code}")
        if api_response.status_code == 200:
            print("   API调用成功，但可能需要具体的token获取逻辑")
        
        return None
        
    except Exception as e:
        print(f"❌ 获取token时发生错误: {e}")
        return None

if __name__ == "__main__":
    print("🚀 PUMA Token获取工具")
    print("=" * 50)
    
    token = get_new_puma_token()
    
    if token:
        print(f"\n✅ 成功获取token:")
        print(f"   {token}")
        print(f"\n请将此token更新到 new_puma_graphql_api.py 文件中")
    else:
        print(f"\n❌ 未能自动获取token")
        print(f"请按照上述手动步骤获取token")