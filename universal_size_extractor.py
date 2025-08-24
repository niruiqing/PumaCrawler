#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Puma商品尺码信息获取通用方法
基于真实的GraphQL API请求分析
"""

import requests
import json
import re
from datetime import datetime
from urllib.parse import urljoin, urlparse

class PumaSizeExtractor:
    """Puma尺码信息提取器 - 通用解决方案"""
    
    def __init__(self):
        self.session = requests.Session()
        self.graphql_url = "https://us.puma.com/api/graphql"
        
        # 基础请求头
        self.base_headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
            'Accept': 'application/graphql-response+json, application/graphql+json, application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/json',
            'Origin': 'https://us.puma.com',
            'Sec-Ch-Ua': '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"macOS"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'X-Graphql-Client-Name': 'nitro-fe',
            'X-Operation-Name': 'LazyPDP',
            'Locale': 'en-US',
            'Puma-Request-Source': 'web'
        }
        
        # GraphQL查询语句
        self.size_query = """
        query LazyPDP($id: ID!) {
          product(id: $id) {
            id
            ...sizes
            variations {
              ...pdpMandatoryExtraVariantFields
              description
              productStory {
                longDescription
                materialComposition
                careInstructions
                manufacturerInfo {
                  manufacturerAddress {
                    label
                    content
                    __typename
                  }
                  countryOfOrigin {
                    label
                    content
                    __typename
                  }
                  __typename
                }
                productKeywords
                __typename
              }
              __typename
            }
            __typename
          }
        }
        fragment sizes on Product {
          productMeasurements {
            metric
            imperial
            __typename
          }
          __typename
        }
        fragment pdpMandatoryExtraVariantFields on Variant {
          id
          sizeGroups {
            label
            description
            sizes {
              id
              label
              value
              productId
              orderable
              maxOrderableQuantity
              __typename
            }
            __typename
          }
          __typename
        }
        """
    
    def extract_product_id(self, url):
        """从URL中提取产品ID"""
        match = re.search(r'/(\d+)(?:\?|$)', url)
        if match:
            return match.group(1)
        return None
    
    def get_session_token(self, product_url):
        """获取会话令牌和认证信息"""
        print(f"🔐 获取会话认证信息...")
        
        try:
            # 访问商品页面获取session
            response = self.session.get(product_url, headers={
                'User-Agent': self.base_headers['User-Agent'],
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9'
            })
            
            if response.status_code == 200:
                print(f"   ✅ 页面访问成功: {response.status_code}")
                
                # 从页面中提取可能的认证信息
                content = response.text
                
                # 查找JWT token或其他认证信息
                auth_patterns = [
                    r'"access_token":"([^"]+)"',
                    r'"bearer":"([^"]+)"',
                    r'"token":"([^"]+)"',
                    r'Bearer\s+([A-Za-z0-9\-_.]+)',
                    r'"authorization":"Bearer\s+([^"]+)"'
                ]
                
                for pattern in auth_patterns:
                    match = re.search(pattern, content)
                    if match:
                        token = match.group(1)
                        print(f"   🔑 发现认证令牌: {token[:50]}...")
                        return token
                
                # 查找customer-id等信息
                customer_patterns = [
                    r'"customer_id":"([^"]+)"',
                    r'"customerId":"([^"]+)"',
                    r'customer-id["\s]*:["\s]*([^"]+)'
                ]
                
                customer_id = None
                for pattern in customer_patterns:
                    match = re.search(pattern, content)
                    if match:
                        customer_id = match.group(1)
                        print(f"   👤 发现客户ID: {customer_id}")
                        break
                
                return {'customer_id': customer_id}
            else:
                print(f"   ❌ 页面访问失败: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"   ❌ 获取会话信息失败: {e}")
            return None
    
    def get_sizes_with_auth(self, product_id, auth_info=None):
        """使用认证信息获取尺码"""
        print(f"🔍 使用认证方式获取尺码: 产品ID {product_id}")
        
        headers = self.base_headers.copy()
        
        # 如果有认证信息，添加到请求头
        if auth_info:
            if isinstance(auth_info, str):
                headers['Authorization'] = f'Bearer {auth_info}'
            elif isinstance(auth_info, dict):
                if 'customer_id' in auth_info and auth_info['customer_id']:
                    headers['Customer-Id'] = auth_info['customer_id']
        
        # 设置referer
        headers['Referer'] = f'https://us.puma.com/us/en/pd/product/{product_id}'
        
        payload = {
            "operationName": "LazyPDP",
            "query": self.size_query,
            "variables": {"id": product_id}
        }
        
        try:
            response = self.session.post(
                self.graphql_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            print(f"   📊 API响应状态: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if 'errors' in data:
                    print(f"   ❌ GraphQL错误: {data['errors']}")
                    return None
                    
                if 'data' in data and data['data'] and data['data'].get('product'):
                    print(f"   ✅ 成功获取产品数据")
                    return self.parse_size_data(data['data'])
                else:
                    print(f"   ⚠️ 响应中无产品数据")
                    return None
            else:
                print(f"   ❌ API请求失败: {response.status_code}")
                print(f"   响应内容: {response.text[:200]}")
                return None
                
        except Exception as e:
            print(f"   ❌ 请求异常: {e}")
            return None
    
    def get_sizes_without_auth(self, product_id):
        """无认证方式获取尺码（备用方案）"""
        print(f"🔍 使用无认证方式获取尺码: 产品ID {product_id}")
        
        headers = self.base_headers.copy()
        headers['Referer'] = f'https://us.puma.com/us/en/pd/product/{product_id}'
        
        # 简化的查询
        simple_query = """
        query GetProduct($id: ID!) {
          product(id: $id) {
            id
            variations {
              id
              sizeGroups {
                label
                description
                sizes {
                  id
                  label
                  value
                  orderable
                  maxOrderableQuantity
                }
              }
            }
          }
        }
        """
        
        payload = {
            "operationName": "GetProduct",
            "query": simple_query,
            "variables": {"id": product_id}
        }
        
        try:
            response = self.session.post(
                self.graphql_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            print(f"   📊 API响应状态: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if 'errors' in data:
                    print(f"   ❌ GraphQL错误: {data['errors']}")
                    return None
                    
                if 'data' in data and data['data'] and data['data'].get('product'):
                    print(f"   ✅ 成功获取产品数据")
                    return self.parse_size_data(data['data'])
                    
            return None
            
        except Exception as e:
            print(f"   ❌ 请求异常: {e}")
            return None
    
    def parse_size_data(self, product_data):
        """解析尺码数据"""
        sizes_info = {
            'product_id': product_data['product'].get('id', ''),
            'size_groups': [],
            'all_sizes': [],
            'available_sizes': [],
            'unavailable_sizes': []
        }
        
        product = product_data['product']
        
        if 'variations' in product and product['variations']:
            for variation in product['variations']:
                if 'sizeGroups' in variation:
                    for group in variation['sizeGroups']:
                        group_info = {
                            'label': group.get('label', ''),
                            'description': group.get('description', ''),
                            'sizes': []
                        }
                        
                        for size in group.get('sizes', []):
                            size_info = {
                                'id': size.get('id', ''),
                                'label': size.get('label', ''),
                                'value': size.get('value', ''),
                                'orderable': size.get('orderable', False),
                                'maxQuantity': size.get('maxOrderableQuantity', 0),
                                'productId': size.get('productId', '')
                            }
                            
                            group_info['sizes'].append(size_info)
                            
                            # 添加到总列表
                            size_display = f"{group['label']} {size['label']}"
                            if size.get('orderable', False):
                                sizes_info['available_sizes'].append(size_display)
                            else:
                                sizes_info['unavailable_sizes'].append(size_display)
                                size_display += " (缺货)"
                            
                            sizes_info['all_sizes'].append(size_display)
                        
                        sizes_info['size_groups'].append(group_info)
        
        return sizes_info
    
    def get_sizes_universal(self, product_url):
        """通用尺码获取方法"""
        print(f"🎯 开始通用尺码获取: {product_url}")
        
        # 提取产品ID
        product_id = self.extract_product_id(product_url)
        if not product_id:
            print(f"❌ 无法从URL提取产品ID")
            return None
        
        print(f"🆔 产品ID: {product_id}")
        
        # 方法1: 获取认证信息后请求
        auth_info = self.get_session_token(product_url)
        if auth_info:
            sizes = self.get_sizes_with_auth(product_id, auth_info)
            if sizes:
                print(f"✅ 认证方式成功获取尺码")
                return sizes
        
        # 方法2: 无认证请求
        sizes = self.get_sizes_without_auth(product_id)
        if sizes:
            print(f"✅ 无认证方式成功获取尺码")
            return sizes
        
        # 方法3: 使用你提供的curl参数进行请求
        sizes = self.get_sizes_with_full_headers(product_id, product_url)
        if sizes:
            print(f"✅ 完整请求头方式成功获取尺码")
            return sizes
        
        print(f"❌ 所有方法都无法获取尺码")
        return None
    
    def get_sizes_with_full_headers(self, product_id, product_url):
        """使用完整请求头获取尺码（基于你提供的curl）"""
        print(f"🔍 使用完整请求头获取尺码...")
        
        # 模拟你提供的curl请求的关键头部
        headers = {
            'Accept': 'application/graphql-response+json, application/graphql+json, application/json',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Content-Type': 'application/json',
            'Customer-Group': '19f53594b6c24daa468fd3f0f2b87b1373b0bda5621be473324fce5d0206b44d',
            'Customer-Id': 'bck0g1lXsZkrcRlXaUlWYYwrJH',  # 示例ID
            'Locale': 'en-US',
            'Origin': 'https://us.puma.com',
            'Priority': 'u=1, i',
            'Puma-Request-Source': 'web',
            'Referer': product_url,
            'Sec-Ch-Ua': '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"macOS"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
            'X-Graphql-Client-Name': 'nitro-fe',
            'X-Graphql-Client-Version': '961757de4b96db7c1c36770d26de3e4fb6f16f24',
            'X-Operation-Name': 'LazyPDP'
        }
        
        payload = {
            "operationName": "LazyPDP",
            "query": self.size_query,
            "variables": {"id": product_id}
        }
        
        try:
            response = self.session.post(
                self.graphql_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            print(f"   📊 API响应状态: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if 'errors' in data:
                    print(f"   ❌ GraphQL错误: {data['errors']}")
                    return None
                    
                if 'data' in data and data['data'] and data['data'].get('product'):
                    print(f"   ✅ 成功获取产品数据")
                    return self.parse_size_data(data['data'])
                    
            return None
            
        except Exception as e:
            print(f"   ❌ 请求异常: {e}")
            return None

def test_size_extraction():
    """测试尺码提取功能"""
    extractor = PumaSizeExtractor()
    
    # 测试法拉利Polo衫
    ferrari_url = "https://us.puma.com/us/en/pd/scuderia-ferrari-sportswear-cs-polo-men/632782?swatch=01"
    
    print("="*70)
    print("🧪 测试Puma尺码提取器")
    print("="*70)
    
    sizes = extractor.get_sizes_universal(ferrari_url)
    
    if sizes:
        print(f"\n🎉 尺码提取成功!")
        print(f"📦 产品ID: {sizes['product_id']}")
        print(f"📏 尺码组数: {len(sizes['size_groups'])}")
        print(f"👕 总尺码数: {len(sizes['all_sizes'])}")
        print(f"✅ 可用尺码: {len(sizes['available_sizes'])}")
        print(f"❌ 缺货尺码: {len(sizes['unavailable_sizes'])}")
        
        # 显示详细尺码信息
        for i, group in enumerate(sizes['size_groups'], 1):
            print(f"\n尺码组 {i}: {group['label']}")
            if group['description']:
                print(f"   说明: {group['description']}")
            available = [s['label'] for s in group['sizes'] if s['orderable']]
            unavailable = [s['label'] for s in group['sizes'] if not s['orderable']]
            print(f"   可用: {', '.join(available)}")
            if unavailable:
                print(f"   缺货: {', '.join(unavailable)}")
        
        # 保存结果
        with open('ferrari_polo_sizes.json', 'w', encoding='utf-8') as f:
            json.dump(sizes, f, ensure_ascii=False, indent=2)
        print(f"\n💾 详细尺码信息已保存到: ferrari_polo_sizes.json")
        
    else:
        print(f"\n❌ 尺码提取失败")
        print(f"💡 建议:")
        print(f"   1. 检查网络连接")
        print(f"   2. 确认URL有效性")
        print(f"   3. 可能需要更新认证信息")

if __name__ == "__main__":
    test_size_extraction()