#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强的PUMA TOKEN获取工具
使用多种策略自动获取最新的认证token
"""

import requests
import json
import re
from datetime import datetime
import time

class EnhancedTokenFetcher:
    """增强的TOKEN获取器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1"
        }
    
    def strategy_1_homepage_analysis(self):
        """策略1: 分析首页内容"""
        print("🔍 策略1: 分析PUMA首页内容...")
        
        try:
            response = self.session.get("https://us.puma.com/us/en", headers=self.headers, timeout=30)
            print(f"   首页状态码: {response.status_code}")
            
            if response.status_code == 200:
                return self._extract_tokens_from_content(response.text, "首页")
            
        except Exception as e:
            print(f"   策略1失败: {e}")
        
        return None
    
    def strategy_2_product_page_analysis(self):
        """策略2: 分析商品页面内容"""
        print("🔍 策略2: 分析商品页面内容...")
        
        test_urls = [
            "https://us.puma.com/us/en/pd/suede-xl-leopard-jr-youth/404299",
            "https://us.puma.com/us/en/pd/suede-xl-leopard-jr-youth/404299?swatch=02",
            "https://us.puma.com/us/en/pd/rs-x-efekt-prism-sneakers/393270",
        ]
        
        for url in test_urls:
            try:
                print(f"   尝试访问: {url}")
                response = self.session.get(url, headers=self.headers, timeout=30)
                print(f"   状态码: {response.status_code}")
                
                if response.status_code == 200:
                    result = self._extract_tokens_from_content(response.text, f"商品页面 {url}")
                    if result:
                        return result
                        
            except Exception as e:
                print(f"   访问 {url} 失败: {e}")
        
        return None
    
    def strategy_3_api_exploration(self):
        """策略3: 探索API端点"""
        print("🔍 策略3: 探索API端点...")
        
        api_endpoints = [
            ("https://us.puma.com/api/auth/guest", "POST", {}),
            ("https://us.puma.com/api/session", "GET", {}),
            ("https://us.puma.com/api/config", "GET", {}),
        ]
        
        for endpoint, method, data in api_endpoints:
            try:
                print(f"   尝试 {method} {endpoint}")
                
                if method == "POST":
                    response = self.session.post(endpoint, headers={
                        **self.headers,
                        "Content-Type": "application/json"
                    }, json=data, timeout=30)
                else:
                    response = self.session.get(endpoint, headers=self.headers, timeout=30)
                
                print(f"   状态码: {response.status_code}")
                
                if response.status_code == 200:
                    # 检查响应头
                    for header_name, header_value in response.headers.items():
                        if 'token' in header_name.lower() or 'auth' in header_name.lower():
                            print(f"   找到认证头: {header_name}: {header_value}")
                    
                    # 检查响应体
                    try:
                        json_data = response.json()
                        result = self._extract_tokens_from_json(json_data, f"API {endpoint}")
                        if result:
                            return result
                    except:
                        result = self._extract_tokens_from_content(response.text, f"API {endpoint}")
                        if result:
                            return result
                            
            except Exception as e:
                print(f"   API探索失败 {endpoint}: {e}")
        
        return None
    
    def strategy_4_network_simulation(self):
        """策略4: 模拟网络请求"""
        print("🔍 策略4: 模拟GraphQL网络请求...")
        
        try:
            # 先访问一个页面建立session
            self.session.get("https://us.puma.com/us/en", headers=self.headers, timeout=30)
            
            # 尝试发送简单的GraphQL查询
            graphql_url = "https://us.puma.com/api/graphql"
            
            queries = [
                {
                    "operationName": None,
                    "query": "{ __typename }",
                    "variables": {}
                },
                {
                    "operationName": "GetConfig",
                    "query": "query GetConfig { __typename }",
                    "variables": {}
                }
            ]
            
            for query in queries:
                try:
                    print(f"   尝试GraphQL查询: {query['operationName'] or 'Anonymous'}")
                    
                    response = self.session.post(graphql_url, headers={
                        **self.headers,
                        "Content-Type": "application/json",
                        "Origin": "https://us.puma.com",
                        "Referer": "https://us.puma.com/us/en/"
                    }, json=query, timeout=30)
                    
                    print(f"   GraphQL状态码: {response.status_code}")
                    
                    # 检查响应中是否包含新的token信息
                    if response.status_code in [200, 401, 403]:
                        try:
                            json_data = response.json()
                            if 'errors' in json_data:
                                print(f"   GraphQL错误: {json_data['errors']}")
                            
                            # 即使有错误，也可能包含token信息
                            result = self._extract_tokens_from_json(json_data, "GraphQL响应")
                            if result:
                                return result
                        except:
                            pass
                            
                except Exception as e:
                    print(f"   GraphQL请求失败: {e}")
        
        except Exception as e:
            print(f"   策略4失败: {e}")
        
        return None
    
    def _extract_tokens_from_content(self, content, source):
        """从内容中提取token"""
        print(f"   分析 {source} 内容 ({len(content)} 字符)...")
        
        # 更全面的token模式
        token_patterns = [
            # 标准JWT格式
            r'["\']authorization["\']\\s*:\\s*["\']Bearer\\s+([A-Za-z0-9\\-_]+\\.[A-Za-z0-9\\-_]+\\.[A-Za-z0-9\\-_]+)["\']',
            r'["\']token["\']\\s*:\\s*["\']([A-Za-z0-9\\-_]+\\.[A-Za-z0-9\\-_]+\\.[A-Za-z0-9\\-_]+)["\']',
            r'Bearer\\s+([A-Za-z0-9\\-_]+\\.[A-Za-z0-9\\-_]+\\.[A-Za-z0-9\\-_]+)',
            # 直接的JWT token
            r'["\']([A-Za-z0-9\\-_]{20,}\\.[A-Za-z0-9\\-_]{20,}\\.[A-Za-z0-9\\-_]{20,})["\']',
            # JavaScript变量中的token
            r'token\\s*[=:]\\s*["\']([A-Za-z0-9\\-_]+\\.[A-Za-z0-9\\-_]+\\.[A-Za-z0-9\\-_]+)["\']',
            r'auth(?:orization)?\\s*[=:]\\s*["\']Bearer\\s+([A-Za-z0-9\\-_]+\\.[A-Za-z0-9\\-_]+\\.[A-Za-z0-9\\-_]+)["\']',
        ]
        
        auth_patterns = {
            'customer-group': [
                r'["\']customer[_-]?group["\']\\s*:\\s*["\']([^"\']{10,})["\']',
                r'customerGroup["\']\\s*:\\s*["\']([^"\']{10,})["\']',
                r'customer[_-]?group["\']?\\s*[=:]\\s*["\']([^"\']{10,})["\']'
            ],
            'customer-id': [
                r'["\']customer[_-]?id["\']\\s*:\\s*["\']([^"\']{10,})["\']',
                r'customerId["\']\\s*:\\s*["\']([^"\']{10,})["\']',
                r'customer[_-]?id["\']?\\s*[=:]\\s*["\']([^"\']{10,})["\']'
            ],
            'refresh-token': [
                r'["\']refresh[_-]?token["\']\\s*:\\s*["\']([^"\']{10,})["\']',
                r'refreshToken["\']\\s*:\\s*["\']([^"\']{10,})["\']',
            ],
            'bloomreach-id': [
                r'["\']bloomreach[_-]?id["\']\\s*:\\s*["\']([^"\']{10,})["\']',
                r'bloomreachId["\']\\s*:\\s*["\']([^"\']{10,})["\']',
            ]
        }
        
        found_tokens = []
        found_auth = {}
        
        # 查找JWT tokens
        for pattern in token_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if len(match.split('.')) == 3 and len(match) > 50:  # JWT格式验证
                    found_tokens.append(match)
                    print(f"   ✅ 找到JWT token: {match[:50]}...")
        
        # 查找其他认证信息
        for auth_type, patterns in auth_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    found_auth[auth_type] = matches[0]
                    print(f"   ✅ 找到 {auth_type}: {matches[0][:30]}...")
                    break
        
        if found_tokens:
            result = {
                'authorization': f"Bearer {found_tokens[0]}",
                **found_auth
            }
            print(f"   🎉 成功从 {source} 提取到认证信息!")
            return result
        
        print(f"   ❌ 未从 {source} 找到有效token")
        return None
    
    def _extract_tokens_from_json(self, json_data, source):
        """从JSON数据中提取token"""
        print(f"   分析 {source} JSON数据...")
        
        def search_recursive(obj, path=""):
            """递归搜索JSON对象"""
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    
                    # 检查key是否包含token相关词汇
                    if any(keyword in key.lower() for keyword in ['token', 'auth', 'bearer', 'jwt']):
                        if isinstance(value, str) and len(value.split('.')) == 3:
                            print(f"   ✅ 在 {current_path} 找到JWT: {value[:50]}...")
                            return {'authorization': f"Bearer {value}"}
                    
                    # 递归搜索
                    result = search_recursive(value, current_path)
                    if result:
                        return result
                        
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    result = search_recursive(item, f"{path}[{i}]")
                    if result:
                        return result
            
            return None
        
        result = search_recursive(json_data)
        if result:
            print(f"   🎉 成功从 {source} JSON提取到token!")
            return result
        
        print(f"   ❌ 未从 {source} JSON找到token")
        return None
    
    def get_fresh_token(self, verbose=True):
        """获取新的token，尝试多种策略"""
        print("🚀 开始增强TOKEN获取流程...")
        print("=" * 60)
        
        strategies = [
            self.strategy_1_homepage_analysis,
            self.strategy_2_product_page_analysis, 
            self.strategy_3_api_exploration,
            self.strategy_4_network_simulation
        ]
        
        for i, strategy in enumerate(strategies, 1):
            print(f"\n📋 执行策略 {i}/4...")
            try:
                result = strategy()
                if result:
                    print(f"🎉 策略 {i} 成功!")
                    print("📊 获取到的认证信息:")
                    for key, value in result.items():
                        print(f"   {key}: {value[:50]}..." if len(str(value)) > 50 else f"   {key}: {value}")
                    return result
                else:
                    print(f"❌ 策略 {i} 失败")
            except Exception as e:
                print(f"❌ 策略 {i} 异常: {e}")
            
            # 策略间短暂延迟
            time.sleep(1)
        
        print("\n❌ 所有策略都失败了")
        return None

def main():
    """主函数"""
    print("🚀 启动增强TOKEN获取工具")
    print("=" * 60)
    
    fetcher = EnhancedTokenFetcher()
    result = fetcher.get_fresh_token(verbose=True)
    
    if result:
        print(f"\n✅ TOKEN获取成功!")
        print("📋 建议更新以下认证信息到 new_puma_graphql_api.py:")
        print("-" * 50)
        for key, value in result.items():
            print(f'"{key}": "{value}",')
        print("-" * 50)
    else:
        print(f"\n❌ TOKEN获取失败，请尝试手动获取")

if __name__ == "__main__":
    main()