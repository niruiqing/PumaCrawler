#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新的PUMA GraphQL API客户端
基于实际的curl请求参数重新实现，获取详细的商品信息
"""

import requests
import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field

@dataclass
class ProductInfo:
    """商品信息数据类"""
    # 基本信息
    name: str = ""
    header: str = ""
    sub_header: str = ""
    brand: str = ""
    product_id: str = ""
    variant_id: str = ""
    sku: str = ""
    style_number: str = ""
    ean: str = ""
    
    # 分类信息
    category: str = ""
    subcategory: str = ""
    product_division: str = ""
    primary_category_id: str = ""
    gender: str = ""
    age_group: str = ""
    
    # 导航信息（面包屑导航）
    breadcrumb: List[Dict[str, str]] = field(default_factory=list)
    navigation_path: str = ""
    
    # 价格信息
    price: float = 0.0
    original_price: float = 0.0
    sale_price: float = 0.0
    promotion_price: Optional[float] = None
    best_price: Optional[float] = None
    discount: float = 0.0
    tax: float = 0.0
    tax_rate: float = 0.0
    
    # 颜色信息
    color: str = ""
    color_name: str = ""
    color_value: str = ""
    color_code: str = ""
    
    # 描述和特性
    description: str = ""
    features: List[str] = field(default_factory=list)
    tech_specs: Dict[str, Any] = field(default_factory=dict)
    
    # 材料和护理
    materials: List[str] = field(default_factory=list)
    material_composition: List[str] = field(default_factory=list)
    care_instructions: List[str] = field(default_factory=list)
    
    # 图片信息
    images: List[str] = field(default_factory=list)
    preview_image: str = ""
    vertical_images: List[str] = field(default_factory=list)
    
    # 尺码信息
    sizes: List[str] = field(default_factory=list)
    available_sizes: List[str] = field(default_factory=list)
    unavailable_sizes: List[str] = field(default_factory=list)
    size_chart_id: str = ""
    
    # 新增：详细尺码信息
    size_groups: List[Dict] = field(default_factory=list)
    product_measurements: Dict[str, Any] = field(default_factory=dict)
    metric_measurements: List[List[str]] = field(default_factory=list)
    imperial_measurements: List[List[str]] = field(default_factory=list)
    
    # 库存和状态
    orderable: bool = True
    availability: str = ""
    stock_status: str = ""
    display_out_of_stock: Optional[Dict] = None
    is_final_sale: Optional[bool] = None
    
    # 评价信息
    rating: Optional[float] = None
    reviews_count: Optional[int] = None
    disable_ratings: Optional[bool] = None
    disable_reviews: Optional[bool] = None
    
    # 促销和徽章
    badges: List[str] = field(default_factory=list)
    promotions: List[Dict] = field(default_factory=list)
    promotion_exclusion: bool = False
    percentage_discount_badge: int = 0
    
    # 制造信息
    manufacturer_info: Dict[str, Any] = field(default_factory=dict)
    country_of_origin: str = ""
    
    # 其他信息
    valid_until: str = ""
    is_app_exclusive: bool = False
    app_only_date_time_from: Optional[str] = None
    app_only_date_time_to: Optional[str] = None
    special_message: Optional[str] = None
    model_measurement_text: Optional[str] = None
    
    # 元数据
    scraped_at: str = ""
    method: str = "new_graphql"
    url: str = ""



class NewPumaGraphQLAPI:
    """新的PUMA GraphQL API客户端"""
    
    def __init__(self):
        """初始化API客户端"""
        self.base_url = "https://us.puma.com/api/graphql"
        self.session = requests.Session()
        
        # 基础请求头（基于提供的curl请求）
        self.headers = {
            "accept": "application/graphql-response+json, application/graphql+json, application/json",
            "accept-language": "zh-CN,zh;q=0.9",
            "content-type": "application/json",
            "locale": "en-US",
            "origin": "https://us.puma.com",
            "priority": "u=1, i",
            "puma-request-source": "web",
            "sec-ch-ua": '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
            "x-graphql-client-name": "nitro-fe",
            "x-graphql-client-version": "961757de4b96db7c1c36770d26de3e4fb6f16f24",
            "x-operation-name": "PDP"
        }
        
        # 从项目中已有的有效token（来自complete_graphql_api.py）
        self.auth_headers = {
            "authorization": "Bearer eyJ2ZXIiOiIxLjAiLCJqa3UiOiJzbGFzL3Byb2QvYmNqcF9wcmQiLCJraWQiOiI2OGI4OWE0Mi02ZjAwLTQzYWUtYjRjNC1hZmRmMGUzZWFlNzQiLCJ0eXAiOiJqd3QiLCJjbHYiOiJKMi4zLjQiLCJhbGciOiJFUzI1NiJ9.eyJhdXQiOiJHVUlEIiwic2NwIjoic2ZjYy5zaG9wcGVyLW15YWNjb3VudC5iYXNrZXRzIHNmY2Muc2hvcHBlci1teWFjY291bnQuYWRkcmVzc2VzIHNmY2Muc2hvcHBlci1wcm9kdWN0cyBzZmNjLnNob3BwZXItbXlhY2NvdW50LnJ3IHNmY2Muc2hvcHBlci1teWFjY291bnQucGF5bWVudGluc3RydW1lbnRzIHNmY2Muc2hvcHBlci1jdXN0b21lcnMubG9naW4gc2ZjYy5zaG9wcGVyLWNvbnRleHQgc2ZjYy5zaG9wcGVyLWNvbnRleHQucncgc2ZjYy5zaG9wcGVyLW15YWNjb3VudC5vcmRlcnMgc2ZjYy5zaG9wcGVyLWN1c3RvbWVycy5yZWdpc3RlciBzZmNjLnNob3BwZXItYmFza2V0cy1vcmRlcnMgc2ZjYy5zaG9wcGVyLW15YWNjb3VudC5hZGRyZXNzZXMucncgc2ZjYy5zaG9wcGVyLW15YWNjb3VudC5wcm9kdWN0bGlzdHMucncgc2ZjYy5zaG9wcGVyLXByb2R1Y3RsaXN0cyBzZmNjLnNob3BwZXItcHJvbW90aW9ucyBzZmNjLnNob3BwZXItYmFza2V0cy1vcmRlcnMucncgc2ZjYy5zaG9wcGVyLW15YWNjb3VudC5wYXltZW50aW5zdHJ1bWVudHMucncgc2ZjYy5zaG9wcGVyLWdpZnQtY2VydGlmaWNhdGVzIHNmY2Muc2hvcHBlci1wcm9kdWN0LXNlYXJjaCBzZmNjLnNob3BwZXItbXlhY2NvdW50LnByb2R1Y3RsaXN0cyBzZmNjLnNob3BwZXItY2F0ZWdvcmllcyBzZmNjLnNob3BwZXItbXlhY2NvdW50Iiwic3ViIjoiY2Mtc2xhczo6YmNqcF9wcmQ6OnNjaWQ6MWM4YzhhM2UtNjU2ZS00MWIxLThiNmYtZmIwNmM0NTFmMDE5Ojp1c2lkOjU3Yjk3ZDc0LTIzZWEtNGIxZi05YzZkLTE4NTVlODI1Y2Q5NiIsImN0eCI6InNsYXMiLCJpc3MiOiJzbGFzL3Byb2QvYmNqcF9wcmQiLCJpc3MiOjEsImRudCI6IjAiLCJhdWQiOiJjb21tZXJjZWNsb3VkL3Byb2QvYmNqcF9wcmQiLCJuYmYiOjE3NTYwODg4ODUsInN0eSI6IlVzZXIiLCJpc2IiOiJ1aWRvOnNsYXM6OnVwbjpHdWVzdDo6dWlkbjpHdWVzdCBVc2VyOjpnY2lkOmFibHJCR21yQklsWG9Sa0hsSndxWVl3SGRLOjpjaGlkOk5BIiwiZXhwIjoxNzU2MDkwNzE1LCJpYXQiOjE3NTYwODg5MTUsImp0aSI6IkMyQy0xODQ0NjA0NzcwMDc0MDYzNDc3MzQ3NjM0MTY2MzA0NTcxMTcifQ.oXAFWFX2Thwrc0mJ0tuYq9E5sDtJHNojKeKYHgv8-Z5zVGkCePB03QjyFw-lE_6EiM4ZW7tE6fFOqOaXYcqqiA",
            "customer-group": "a078f6706670a82b26dee50e6d7d1dacb6d532351e60c225876bec5eb416cf4f",
            "customer-id": "ablrBGmrBIlXoRkHlJwqYYwHdK",
            "refresh-token": "YSnG2ZM7TIQoavZQYts9b5zwREzFLVffDdSOmrkhvmM",
            "bloomreach-id": "uid=2119450463975:v=12.0:ts=1756085787277:hc=4"
        }
        
        # GraphQL查询语句（简化版）
        self.pdp_query = """
        query PDP($id: ID!) {
          product(id: $id) {
            name
            id
            header
            subHeader
            brand
            description
            primaryCategoryId
            productDivision
            disableRatings
            disableReviews
            amountOfReviews
            averageRating
            sizeChartId
            orderable
            colors {
              name
              value
            }
            image {
              href
              verticalImageHref
              alt
            }
            variations {
              id
              masterId
              variantId
              name
              price
              colorValue
              colorName
              ean
              preview
              images {
                alt
                href
                verticalImageHref
              }
              isFinalSale
              validUntil
              isAppExclusive
              badges {
                id
                label
              }
              salePrice
              productPrice {
                price
                salePrice
                promotionPrice
                tax
                taxRate
                bestPrice
              }
              styleNumber
              materialComposition
              orderable
              manufacturerInfo {
                countryOfOrigin {
                  content
                }
              }
            }
          }
        }
        """
        
        # 新增：LazyPDP查询语句（用于获取详细尺码信息）
        self.lazy_pdp_query = """
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
        
        print("✅ 新的PUMA GraphQL API客户端初始化完成")
    
    def get_fresh_token(self):
        """获取新的认证token"""
        try:
            print(f"🔄 尝试获取新的认证token...")
            
            # 创建一个新的session来避免cookie干扰
            fresh_session = requests.Session()
            
            # 设置真实的浏览器头部
            browser_headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
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
            
            # 1. 首先访问首页建立session
            print(f"📝 Step 1: 访问PUMA首页建立会话...")
            homepage_response = fresh_session.get(
                "https://us.puma.com/us/en",
                headers=browser_headers,
                timeout=30
            )
            
            print(f"📊 首页响应状态码: {homepage_response.status_code}")
            
            if homepage_response.status_code != 200:
                print(f"❌ 无法访问首页: {homepage_response.status_code}")
                return False
            
            # 2. 访问具体商品页面
            print(f"📝 Step 2: 访问商品页面...")
            product_url = "https://us.puma.com/us/en/pd/suede-xl-leopard-jr-youth/404299"
            product_response = fresh_session.get(
                product_url,
                headers=browser_headers,
                timeout=30
            )
            
            print(f"📊 商品页面响应状态码: {product_response.status_code}")
            
            if product_response.status_code != 200:
                print(f"❌ 无法访问商品页面: {product_response.status_code}")
                return False
            
            # 3. 分析页面内容寻找认证信息
            print(f"📝 Step 3: 分析页面内容寻找认证信息...")
            content = product_response.text
            
            # 查找JWT token的各种可能位置
            token_patterns = [
                # 标准JWT格式
                r'["\']authorization["\']\s*:\s*["\']Bearer\s+([A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+)["\']',
                r'["\']token["\']\s*:\s*["\']([A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+)["\']',
                r'Bearer\s+([A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+)',
                # 直接的JWT token
                r'["\']([A-Za-z0-9\-_]{20,}\.[A-Za-z0-9\-_]{20,}\.[A-Za-z0-9\-_]{20,})["\']',
                # JavaScript变量中的token
                r'token\s*[=:]\s*["\']([A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+)["\']',
                r'auth(?:orization)?\s*[=:]\s*["\']Bearer\s+([A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+)["\']',
                # window对象中的token
                r'window\.[^=]*=\s*["\']([A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+)["\']',
                # 配置对象中的token
                r'config[^}]*["\']token["\'][^"\']++["\']([A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+)["\']'
            ]
            
            # 查找其他认证头信息
            auth_patterns = {
                'customer-group': [r'["\']customer[_-]?group["\']\\s*:\\s*["\']([^"\']+)["\']', r'customerGroup["\']\\s*:\\s*["\']([^"\']+)["\']'],
                'customer-id': [r'["\']customer[_-]?id["\']\\s*:\\s*["\']([^"\']+)["\']', r'customerId["\']\\s*:\\s*["\']([^"\']+)["\']'],
                'refresh-token': [r'["\']refresh[_-]?token["\']\\s*:\\s*["\']([^"\']+)["\']', r'refreshToken["\']\\s*:\\s*["\']([^"\']+)["\']'],
                'bloomreach-id': [r'["\']bloomreach[_-]?id["\']\\s*:\\s*["\']([^"\']+)["\']', r'bloomreachId["\']\\s*:\\s*["\']([^"\']+)["\']']
            }
            
            found_tokens = []
            for pattern in token_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    # 验证JWT格式（三部分用.分隔）和长度
                    if len(match.split('.')) == 3 and len(match) > 50:
                        # 检查是否为新token（与当前的不同）
                        current_token = self.auth_headers.get("authorization", "").replace("Bearer ", "")
                        if match != current_token:
                            found_tokens.append(match)
                            print(f"✅ 找到新的JWT token: {match[:30]}...{match[-10:]}")
            
            if found_tokens:
                # 使用第一个找到的有效token
                new_token = found_tokens[0]
                print(f"✅ 在页面中找到JWT token: {new_token[:50]}...")
                self.auth_headers["authorization"] = f"Bearer {new_token}"
                
                # 尝试查找其他认证信息
                for header_name, patterns in auth_patterns.items():
                    for pattern in patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        if matches:
                            self.auth_headers[header_name] = matches[0]
                            print(f"✅ 找到 {header_name}: {matches[0][:20]}...")
                            break
                
                print(f"✅ 成功更新认证信息")
                return True
            
            # 4. 如果页面中没找到，尝试使用RefreshLogon API刷新token
            print(f"📝 Step 4: 尝试使用RefreshLogon API刷新token...")
            refresh_success = self._try_refresh_logon_api(fresh_session)
            if refresh_success:
                return True
            
            # 5. 如果RefreshLogon失败，尝试模拟GraphQL请求触发token生成
            print(f"📝 Step 5: 尝试通过GraphQL API触发token生成...")
            graphql_headers = {
                **browser_headers,
                "Content-Type": "application/json",
                "Origin": "https://us.puma.com",
                "Referer": product_url,
                "x-graphql-client-name": "nitro-fe",
                "x-graphql-client-version": "961757de4b96db7c1c36770d26de3e4fb6f16f24"
            }
            
            # 简单的查询请求
            simple_query = {
                "operationName": "GetSiteConfig",
                "query": "query GetSiteConfig { __typename }",
                "variables": {}
            }
            
            api_response = fresh_session.post(
                "https://us.puma.com/api/graphql",
                headers=graphql_headers,
                json=simple_query,
                timeout=30
            )
            
            print(f"📊 GraphQL API响应状态码: {api_response.status_code}")
            
            # 检查响应头是否包含新的认证信息
            response_headers = api_response.headers
            if 'set-cookie' in response_headers:
                print(f"📊 API响应包含Cookie信息")
            
            # 尝试从响应中提取token（某些API会在响应中返回token）
            if api_response.status_code == 200:
                try:
                    response_data = api_response.json()
                    print(f"📊 API响应包含数据")
                    # 这里可以根据API的具体响应格式来提取token
                except:
                    pass
            
            print(f"⚠️ 无法自动获取新的认证token")
            
            # 6. Fallback策略：尝试从项目中其他API客户端获取token
            print(f"📝 Step 6: Fallback - 尝试从项目中其他API客户端获取token...")
            try:
                # 尝试导入并获取其他API客户端的token
                import sys
                import os
                project_root = os.path.dirname(os.path.dirname(__file__))
                if project_root not in sys.path:
                    sys.path.insert(0, project_root)
                
                # 尝试从complete_graphql_api获取token
                try:
                    from complete_graphql_api import CompleteGraphQLAPI
                    backup_api = CompleteGraphQLAPI()
                    if hasattr(backup_api, 'headers') and 'authorization' in backup_api.headers:
                        backup_token = backup_api.headers['authorization']
                        if backup_token and backup_token != self.auth_headers.get('authorization'):
                            print(f"✅ 从CompleteGraphQLAPI获取到backup token")
                            self.auth_headers['authorization'] = backup_token
                            return True
                except ImportError:
                    pass
                
                # 尝试从working_complete_graphql_api获取token
                try:
                    from working_complete_graphql_api import WorkingCompleteGraphQLAPI
                    backup_api = WorkingCompleteGraphQLAPI()
                    if hasattr(backup_api, 'auth_headers') and 'authorization' in backup_api.auth_headers:
                        backup_token = backup_api.auth_headers['authorization']
                        if backup_token and backup_token != self.auth_headers.get('authorization'):
                            print(f"✅ 从WorkingCompleteGraphQLAPI获取到backup token")
                            # 复制所有认证头
                            for key, value in backup_api.auth_headers.items():
                                self.auth_headers[key] = value
                            return True
                except ImportError:
                    pass
                    
            except Exception as e:
                print(f"❌ Fallback策略失败: {e}")
            
            return False
            
        except Exception as e:
            print(f"❌ 获取新token时发生错误: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _try_refresh_logon_api(self, session):
        """尝试使用RefreshLogon API刷新token"""
        try:
            current_refresh_token = self.auth_headers.get("refresh-token")
            if not current_refresh_token:
                print(f"⚠️ 没有可用的refresh-token")
                return False
            
            print(f"✅ 使用现有refresh-token: {current_refresh_token[:20]}...")
            
            # RefreshLogon GraphQL查询
            refresh_query = {
                "operationName": "RefreshLogon",
                "query": """mutation RefreshLogon($input: RefreshLogonInput!) {
  refreshLogon(input: $input) {
    ...tokenPayload
  }
}
fragment tokenPayload on TokenPayload {
  __typename
  accessToken
  refreshToken
  customerId
  uniqueShopperId
  customerContext {
    __typename
    hashKey
    customerGroups
  }
  user {
    customerNo
    email
  }
}""",
                "variables": {
                    "input": {
                        "refreshToken": current_refresh_token
                    }
                }
            }
            
            # 准备请求头
            refresh_headers = {
                "accept": "application/graphql-response+json, application/graphql+json, application/json",
                "accept-language": "zh-CN,zh;q=0.9",
                "content-type": "application/json",
                "locale": "en-US",
                "origin": "https://us.puma.com",
                "priority": "u=1, i",
                "puma-request-source": "web",
                "referer": "https://us.puma.com/us/en/pd/suede-xl-super-puma-jr-youth/403380?swatch=01",
                "sec-ch-ua": '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
                "x-graphql-client-name": "nitro-fe",
                "x-graphql-client-version": "961757de4b96db7c1c36770d26de3e4fb6f16f24",
                "x-operation-name": "RefreshLogon"
            }
            
            # 添加当前的认证信息
            if self.auth_headers.get("authorization"):
                refresh_headers["authorization"] = self.auth_headers["authorization"]
            if self.auth_headers.get("customer-group"):
                refresh_headers["customer-group"] = self.auth_headers["customer-group"]
            if self.auth_headers.get("customer-id"):
                refresh_headers["customer-id"] = self.auth_headers["customer-id"]
            if self.auth_headers.get("refresh-token"):
                refresh_headers["refresh-token"] = self.auth_headers["refresh-token"]
            if self.auth_headers.get("bloomreach-id"):
                refresh_headers["bloomreach-id"] = self.auth_headers["bloomreach-id"]
            
            print(f"📝 发送RefreshLogon请求...")
            response = session.post(
                "https://us.puma.com/api/graphql",
                headers=refresh_headers,
                json=refresh_query,
                timeout=30
            )
            
            print(f"📊 RefreshLogon响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if 'data' in data and 'refreshLogon' in data['data'] and data['data']['refreshLogon']:
                        token_payload = data['data']['refreshLogon']
                        
                        # 获取新的认证信息
                        new_access_token = token_payload.get('accessToken')
                        new_refresh_token = token_payload.get('refreshToken')
                        new_customer_id = token_payload.get('customerId')
                        
                        if new_access_token:
                            print(f"✅ RefreshLogon成功！获取到新的accessToken")
                            
                            # 更新认证信息
                            self.auth_headers["authorization"] = f"Bearer {new_access_token}"
                            
                            if new_refresh_token:
                                self.auth_headers["refresh-token"] = new_refresh_token
                                print(f"✅ 更新refresh-token: {new_refresh_token[:20]}...")
                            
                            if new_customer_id:
                                self.auth_headers["customer-id"] = new_customer_id
                                print(f"✅ 更新customer-id: {new_customer_id}")
                            
                            # 更新customerContext中的hashKey作为customer-group
                            customer_context = token_payload.get('customerContext', {})
                            if customer_context and customer_context.get('hashKey'):
                                self.auth_headers["customer-group"] = customer_context['hashKey']
                                print(f"✅ 更新customer-group: {customer_context['hashKey'][:20]}...")
                            
                            print(f"✅ RefreshLogon API刷新token成功！")
                            return True
                        else:
                            print(f"❌ RefreshLogon响应中没有accessToken")
                            return False
                    elif 'errors' in data:
                        print(f"❌ RefreshLogon错误: {data['errors']}")
                        return False
                    else:
                        print(f"❌ RefreshLogon响应格式不正确")
                        return False
                        
                except json.JSONDecodeError as e:
                    print(f"❌ RefreshLogon响应JSON解析失败: {e}")
                    return False
            else:
                print(f"❌ RefreshLogon请求失败: {response.status_code}")
                if response.text:
                    print(f"   响应内容: {response.text[:200]}...")
                return False
                
        except Exception as e:
            print(f"❌ RefreshLogon API调用异常: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def extract_product_id(self, url: str) -> Optional[str]:
        """从PUMA商品URL中提取商品ID"""
        try:
            # 多种URL格式的匹配模式
            patterns = [
                r'/pd/[^/]+/(\d+)',  # 标准格式: /pd/product-name/123456
                r'product[_-]?id[=:](\d+)',  # 查询参数格式
                r'/(\d{6})(?:[/?]|$)',  # 6位数字ID
                r'/(\d{5,7})(?:[/?]|$)',  # 5-7位数字ID
            ]
            
            for pattern in patterns:
                match = re.search(pattern, url, re.IGNORECASE)
                if match:
                    product_id = match.group(1)
                    print(f"✅ 从URL提取到商品ID: {product_id}")
                    return product_id
            
            print(f"❌ 无法从URL提取商品ID: {url}")
            return None
            
        except Exception as e:
            print(f"❌ 提取商品ID时发生错误: {e}")
            return None
    
    def scrape_product(self, url: str) -> Optional[ProductInfo]:
        """主要接口：爬取商品信息"""
        try:
            print(f"🔍 开始爬取商品: {url}")
            
            # 提取商品ID
            product_id = self.extract_product_id(url)
            if not product_id:
                return None
            
            # 获取基本商品信息
            product_info = self.get_product_info(product_id)
            if not product_info:
                return None
            
            # 获取详细尺码信息
            print(f"🔍 获取详细尺码信息...")
            detailed_size_data = self.get_detailed_size_info(product_id)
            if detailed_size_data:
                # 合并详细尺码信息到基本商品信息中
                self._merge_detailed_size_info(product_info, detailed_size_data)
                print(f"✅ 成功合并详细尺码信息")
            else:
                print(f"⚠️ 无法获取详细尺码信息，使用基本信息")
            
            # 获取导航信息
            print(f"🔍 获取导航信息...")
            breadcrumb_items, navigation_path = self._extract_breadcrumb_from_html(url)
            if breadcrumb_items:
                product_info.breadcrumb = breadcrumb_items
                product_info.navigation_path = navigation_path
                print(f"✅ 成功获取导航信息: {navigation_path}")
            else:
                print(f"⚠️ 无法获取导航信息")
            
            product_info.url = url
            product_info.scraped_at = datetime.now().isoformat()
            print(f"✅ 成功爬取商品: {product_info.name}")
            return product_info
            
        except Exception as e:
            print(f"❌ 爬取商品时发生错误: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_detailed_size_info(self, product_id: str) -> Optional[Dict]:
        """通过LazyPDP API获取详细的尺码信息和商品测量数据"""
        try:
            print(f"🔍 正在获取详细尺码信息，ID: {product_id}")
            
            # 准备请求头
            request_headers = {**self.headers, **self.auth_headers}
            request_headers["referer"] = f"https://us.puma.com/us/en/pd/product/{product_id}"
            request_headers["x-operation-name"] = "LazyPDP"
            
            # 准备GraphQL请求数据
            payload = {
                "operationName": "LazyPDP",
                "query": self.lazy_pdp_query,
                "variables": {"id": product_id}
            }
            
            print(f"📡 发送LazyPDP请求...")
            response = self.session.post(
                self.base_url,
                headers=request_headers,
                json=payload,
                timeout=30
            )
            
            print(f"📈 LazyPDP响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"✅ 成功获取LazyPDP JSON响应")
                    
                    if 'errors' in data:
                        errors = data['errors']
                        print(f"❌ LazyPDP GraphQL错误: {errors}")
                        
                        # 检查是否是认证错误
                        for error in errors:
                            if error.get('extensions', {}).get('code') == 'UNAUTHENTICATED':
                                print(f"⚠️ 认证失败，尝试获取新token...")
                                if self.get_fresh_token():
                                    print(f"🔄 获取新token成功，重试请求...")
                                    # 重新准备请求头
                                    request_headers = {**self.headers, **self.auth_headers}
                                    request_headers["referer"] = f"https://us.puma.com/us/en/pd/product/{product_id}"
                                    request_headers["x-operation-name"] = "LazyPDP"
                                    
                                    # 重试请求
                                    retry_response = self.session.post(
                                        self.base_url,
                                        headers=request_headers,
                                        json=payload,
                                        timeout=30
                                    )
                                    
                                    if retry_response.status_code == 200:
                                        retry_data = retry_response.json()
                                        if 'data' in retry_data and 'product' in retry_data['data'] and retry_data['data']['product']:
                                            product_data = retry_data['data']['product']
                                            print(f"✅ 重试成功！获取到详细尺码数据")
                                            return product_data
                                        elif 'errors' in retry_data:
                                            print(f"❌ 重试后仍有错误: {retry_data['errors']}")
                                    else:
                                        print(f"❌ 重试请求失败: {retry_response.status_code}")
                                else:
                                    print(f"❌ 无法获取新token")
                                break
                        return None
                    
                    if 'data' in data and 'product' in data['data'] and data['data']['product']:
                        product_data = data['data']['product']
                        print(f"✅ 成功获取详细尺码数据")
                        return product_data
                    else:
                        print(f"❌ 响应数据中没有商品信息")
                        return None
                        
                except json.JSONDecodeError as e:
                    print(f"❌ LazyPDP JSON解析错误: {e}")
                    print(f"响应内容: {response.text[:500]}...")
                    return None
            else:
                print(f"❌ LazyPDP HTTP请求失败: {response.status_code}")
                print(f"响应内容: {response.text[:500]}...")
                return None
                
        except Exception as e:
            print(f"❌ 获取详细尺码信息时发生错误: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_product_info(self, product_id: str) -> Optional[ProductInfo]:
        try:
            print(f"🔍 正在获取商品信息，ID: {product_id}")
            
            # 准备请求头
            request_headers = {**self.headers, **self.auth_headers}
            request_headers["referer"] = f"https://us.puma.com/us/en/pd/product/{product_id}"
            
            # 准备GraphQL请求数据
            payload = {
                "operationName": "PDP",
                "query": self.pdp_query,
                "variables": {"id": product_id}
            }
            
            print(f"📡 发送GraphQL请求...")
            response = self.session.post(
                self.base_url,
                headers=request_headers,
                json=payload,
                timeout=30
            )
            
            print(f"📊 响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"✅ 成功获取JSON响应")
                    
                    if 'errors' in data:
                        errors = data['errors']
                        print(f"❌ GraphQL错误: {errors}")
                        
                        # 检查是否是认证错误
                        for error in errors:
                            if error.get('extensions', {}).get('code') == 'UNAUTHENTICATED':
                                print("⚠️ 认证失败，尝试获取新token...")
                                if self.get_fresh_token():
                                    print("🔄 获取新token成功，重试请求...")
                                    # 重新准备请求头
                                    request_headers = {**self.headers, **self.auth_headers}
                                    request_headers["referer"] = f"https://us.puma.com/us/en/pd/product/{product_id}"
                                    
                                    # 重试请求
                                    retry_response = self.session.post(
                                        self.base_url,
                                        headers=request_headers,
                                        json=payload,
                                        timeout=30
                                    )
                                    
                                    if retry_response.status_code == 200:
                                        retry_data = retry_response.json()
                                        if 'data' in retry_data and 'product' in retry_data['data'] and retry_data['data']['product']:
                                            product_data = retry_data['data']['product']
                                            print(f"✅ 重试成功！获取到商品数据: {product_data.get('name', 'Unknown')}")
                                            return self._parse_product_data(product_data)
                                        elif 'errors' in retry_data:
                                            print(f"❌ 重试后仍有错误: {retry_data['errors']}")
                                    else:
                                        print(f"❌ 重试请求失败: {retry_response.status_code}")
                                else:
                                    print("❌ 无法获取新token")
                                break
                        return None
                    
                    if 'data' in data and 'product' in data['data'] and data['data']['product']:
                        product_data = data['data']['product']
                        print(f"✅ 成功获取商品数据: {product_data.get('name', 'Unknown')}")
                        return self._parse_product_data(product_data)
                    else:
                        print(f"❌ 响应数据中没有商品信息")
                        return None
                        
                except json.JSONDecodeError as e:
                    print(f"❌ JSON解析错误: {e}")
                    print(f"响应内容: {response.text[:500]}...")
                    return None
            else:
                print(f"❌ HTTP请求失败: {response.status_code}")
                print(f"响应内容: {response.text[:500]}...")
                return None
                
        except Exception as e:
            print(f"❌ 获取商品信息时发生错误: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _parse_product_data(self, product_data: Dict) -> ProductInfo:
        """解析GraphQL响应数据为ProductInfo对象"""
        try:
            print(f"📋 开始解析商品数据...")
            
            product_info = ProductInfo()
            
            # 基本信息
            product_info.name = product_data.get('name', '')
            product_info.header = product_data.get('header', '')
            product_info.sub_header = product_data.get('subHeader', '')
            product_info.brand = product_data.get('brand', '')
            product_info.product_id = str(product_data.get('id', ''))
            product_info.description = product_data.get('description', '')
            product_info.orderable = product_data.get('orderable', True)
            product_info.primary_category_id = product_data.get('primaryCategoryId', '')
            product_info.product_division = product_data.get('productDivision', '')
            
            # 评价信息
            product_info.rating = product_data.get('averageRating')
            product_info.reviews_count = product_data.get('amountOfReviews')
            product_info.disable_ratings = product_data.get('disableRatings')
            product_info.disable_reviews = product_data.get('disableReviews')
            product_info.size_chart_id = product_data.get('sizeChartId', '')
            
            # 处理主图片
            main_image = product_data.get('image', {})
            if main_image and main_image.get('href'):
                product_info.preview_image = main_image['href']
                product_info.images.append(main_image['href'])
                if main_image.get('verticalImageHref'):
                    product_info.vertical_images.append(main_image['verticalImageHref'])
            
            # 处理颜色信息
            colors = product_data.get('colors', [])
            if colors:
                first_color = colors[0]
                product_info.color = first_color.get('name', '')
                product_info.color_name = first_color.get('name', '')
                product_info.color_value = first_color.get('value', '')
                product_info.color_code = first_color.get('value', '')
            
            # 处理变体信息
            variations = product_data.get('variations', [])
            if variations:
                first_variant = variations[0]
                
                # 更新基本信息
                product_info.variant_id = first_variant.get('variantId', '')
                product_info.sku = first_variant.get('id', '')
                product_info.style_number = first_variant.get('styleNumber', '')
                product_info.ean = first_variant.get('ean', '')
                
                # 价格信息
                product_info.price = float(first_variant.get('price', 0))
                product_info.sale_price = float(first_variant.get('salePrice', 0))
                
                # 处理产品价格对象
                product_price = first_variant.get('productPrice', {})
                if product_price:
                    product_info.original_price = float(product_price.get('price', 0))
                    product_info.sale_price = float(product_price.get('salePrice', 0))
                    product_info.promotion_price = product_price.get('promotionPrice')
                    product_info.best_price = product_price.get('bestPrice')
                    product_info.tax = float(product_price.get('tax', 0))
                    product_info.tax_rate = float(product_price.get('taxRate', 0))
                
                # 计算折扣
                if product_info.original_price > 0 and product_info.sale_price > 0:
                    product_info.discount = ((product_info.original_price - product_info.sale_price) / product_info.original_price) * 100
                
                # 颜色信息（从变体获取）
                if not product_info.color:
                    product_info.color_name = first_variant.get('colorName', '')
                    product_info.color_value = first_variant.get('colorValue', '')
                    product_info.color = first_variant.get('colorName', '')
                    product_info.color_code = first_variant.get('colorValue', '')
                
                # 状态信息
                product_info.orderable = first_variant.get('orderable', True)
                product_info.is_final_sale = first_variant.get('isFinalSale')
                product_info.valid_until = first_variant.get('validUntil', '')
                product_info.is_app_exclusive = first_variant.get('isAppExclusive', False)
                
                # 处理徽章
                badges = first_variant.get('badges', [])
                if badges:
                    product_info.badges = [badge.get('label', '') for badge in badges if badge.get('label')]
                
                # 处理材料组成
                material_composition = first_variant.get('materialComposition', [])
                if material_composition:
                    product_info.material_composition = material_composition
                    product_info.materials = material_composition
                
                # 处理制造信息
                manufacturer_info = first_variant.get('manufacturerInfo', {})
                if manufacturer_info:
                    product_info.manufacturer_info = manufacturer_info
                    country_info = manufacturer_info.get('countryOfOrigin', {})
                    if country_info and country_info.get('content'):
                        content = country_info['content']
                        if isinstance(content, list) and content:
                            product_info.country_of_origin = content[0]
                        elif isinstance(content, str):
                            product_info.country_of_origin = content
                
                # 处理图片（从变体获取）
                variant_images = first_variant.get('images', [])
                for img in variant_images:
                    if img.get('href') and img['href'] not in product_info.images:
                        product_info.images.append(img['href'])
                    if img.get('verticalImageHref') and img['verticalImageHref'] not in product_info.vertical_images:
                        product_info.vertical_images.append(img['verticalImageHref'])
                
                # 预览图片
                if first_variant.get('preview') and not product_info.preview_image:
                    product_info.preview_image = first_variant['preview']
            
            product_info.availability = "有库存"
            product_info.stock_status = "available"
            
            print(f"✅ 商品数据解析完成: {product_info.name}")
            return product_info
            
        except Exception as e:
            print(f"❌ 解析商品数据时发生错误: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _merge_detailed_size_info(self, product_info: ProductInfo, detailed_data: Dict) -> None:
        """合并详细尺码信息到ProductInfo对象中"""
        try:
            print(f"🔄 开始合并详细尺码信息...")
            
            # 处理商品测量表
            product_measurements = detailed_data.get('productMeasurements')
            if product_measurements:
                product_info.product_measurements = product_measurements
                
                # 公制测量数据
                if product_measurements.get('metric'):
                    product_info.metric_measurements = product_measurements['metric']
                    print(f"✅ 获取到公制测量数据: {len(product_measurements['metric'])} 行")
                
                # 英制测量数据
                if product_measurements.get('imperial'):
                    product_info.imperial_measurements = product_measurements['imperial']
                    print(f"✅ 获取到英制测量数据: {len(product_measurements['imperial'])} 行")
            
            # 处理变体详细信息
            variations = detailed_data.get('variations', [])
            if variations:
                first_variant = variations[0]
                
                # 处理尺码组信息
                size_groups = first_variant.get('sizeGroups', [])
                if size_groups:
                    product_info.size_groups = size_groups
                    
                    # 提取所有尺码信息
                    all_sizes = []
                    available_sizes = []
                    unavailable_sizes = []
                    
                    for size_group in size_groups:
                        sizes = size_group.get('sizes', [])
                        for size in sizes:
                            size_label = size.get('label', '')
                            if size_label:
                                all_sizes.append(size_label)
                                if size.get('orderable', False):
                                    available_sizes.append(size_label)
                                else:
                                    unavailable_sizes.append(size_label)
                    
                    # 更新尺码信息
                    if all_sizes:
                        product_info.sizes = all_sizes
                        product_info.available_sizes = available_sizes
                        product_info.unavailable_sizes = unavailable_sizes
                        print(f"✅ 更新尺码信息: 总共{len(all_sizes)}个, 可用{len(available_sizes)}个, 不可用{len(unavailable_sizes)}个")
                
                # 处理产品故事信息
                product_story = first_variant.get('productStory')
                if product_story:
                    # 更新描述信息
                    if product_story.get('longDescription') and not product_info.description:
                        product_info.description = product_story['longDescription']
                        print(f"✅ 更新商品详细描述")
                    
                    # 更新材料组成
                    material_composition = product_story.get('materialComposition', [])
                    if material_composition:
                        product_info.material_composition = material_composition
                        product_info.materials = material_composition
                        print(f"✅ 更新材料组成: {len(material_composition)} 项")
                    
                    # 更新护理说明
                    care_instructions = product_story.get('careInstructions')
                    if care_instructions:
                        if isinstance(care_instructions, list):
                            product_info.care_instructions = care_instructions
                        elif isinstance(care_instructions, str):
                            product_info.care_instructions = [care_instructions]
                        print(f"✅ 更新护理说明")
                    
                    # 更新制造商信息
                    manufacturer_info = product_story.get('manufacturerInfo')
                    if manufacturer_info:
                        if not product_info.manufacturer_info:
                            product_info.manufacturer_info = {}
                        
                        # 合并制造商信息
                        product_info.manufacturer_info.update(manufacturer_info)
                        
                        # 更新原产地信息
                        country_info = manufacturer_info.get('countryOfOrigin', {})
                        if country_info and country_info.get('content'):
                            content = country_info['content']
                            if isinstance(content, list) and content and content[0]:
                                product_info.country_of_origin = content[0]
                            elif isinstance(content, str) and content:
                                product_info.country_of_origin = content
                            print(f"✅ 更新原产地信息: {product_info.country_of_origin}")
                    
                    # 更新产品关键词
                    product_keywords = product_story.get('productKeywords', [])
                    if product_keywords:
                        # 将关键词作为特性添加
                        if not product_info.features:
                            product_info.features = []
                        product_info.features.extend(product_keywords)
                        print(f"✅ 更新产品关键词: {len(product_keywords)} 个")
                
                # 更新变体描述
                variant_description = first_variant.get('description')
                if variant_description and len(variant_description) > len(product_info.description):
                    product_info.description = variant_description
                    print(f"✅ 更新为更详细的变体描述")
            
            print(f"✅ 详细尺码信息合并完成")
            
        except Exception as e:
            print(f"❌ 合并详细尺码信息时发生错误: {e}")
            import traceback
            traceback.print_exc()
    
    def _extract_breadcrumb_from_html(self, url: str) -> tuple:
        """从页面HTML中提取面包屑导航信息"""
        try:
            print(f"🔍 开始提取导航信息: {url}")
            
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
            response = self.session.get(url, headers=headers, timeout=30)
            
            if response.status_code != 200:
                print(f"❌ 无法获取页面: {response.status_code}")
                return [], ""
            
            html_content = response.text
            print(f"✅ 成功获取页面HTML，长度: {len(html_content)}")
            
            # 检查是否存在JavaScript动态加载的迹象
            if 'skeleton-loader' in html_content or 'breadcrumbs' in html_content:
                print(f"⚠️ 检测到动态加载内容，尝试从 URL 的路径结构推断导航")
                return self._extract_navigation_from_url(url)
            
            # 优先使用BeautifulSoup解析
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # 多种面包屑导航元素查找策略
                breadcrumb_selectors = [
                    {'attrs': {'data-test-id': 'breadcrumb-nav'}},
                    {'attrs': {'aria-label': 'Breadcrumb'}},
                    {'attrs': {'class': lambda x: x and 'breadcrumb' in x.lower()}},
                    {'attrs': {'id': lambda x: x and 'breadcrumb' in x.lower()}}
                ]
                
                breadcrumb_nav = None
                for selector in breadcrumb_selectors:
                    breadcrumb_nav = soup.find('nav', selector['attrs'])
                    if breadcrumb_nav:
                        print(f"✅ 找到面包屑导航元素（使用选择器: {selector}）")
                        break
                
                if breadcrumb_nav:
                    return self._parse_breadcrumb_from_soup(breadcrumb_nav, url)
                else:
                    print(f"⚠️ BeautifulSoup未找到面包屑导航元素")
                    
            except ImportError:
                print(f"⚠️ BeautifulSoup不可用，使用正则表达式")
            except Exception as e:
                print(f"❌ BeautifulSoup解析失败: {e}")
            
            # 备用方案：使用正则表达式
            print(f"🔧 使用正则表达式提取面包屑导航...")
            breadcrumb_result = self._extract_breadcrumb_with_regex(html_content, url)
            if breadcrumb_result[0]:  # 如果找到了导航项
                return breadcrumb_result
            
            # 最后的备用方案：从 URL 推断导航
            print(f"🔧 从 URL 结构推断导航信息...")
            return self._extract_navigation_from_url(url)
            
        except Exception as e:
            print(f"❌ 提取导航信息时发生错误: {e}")
            import traceback
            traceback.print_exc()
            return [], ""
    
    def _extract_breadcrumb_with_regex(self, html_content: str, url: str = "") -> tuple:
        """使用正则表达式提取面包屑导航信息（备用方法）"""
        try:
            import re
            
            print("🔍 使用正则表达式提取导航信息...")
            
            breadcrumb_items = []
            navigation_parts = []
            
            # 查找面包屑导航区域
            breadcrumb_pattern = r'<nav[^>]*data-test-id="breadcrumb-nav"[^>]*>(.*?)</nav>'
            breadcrumb_match = re.search(breadcrumb_pattern, html_content, re.DOTALL | re.IGNORECASE)
            
            if not breadcrumb_match:
                print("❌ 正则表达式未找到面包屑导航区域")
                return [], ""
            
            breadcrumb_html = breadcrumb_match.group(1)
            print(f"✅ 找到面包屑导航区域")
            
            # 提取导航链接（更精确的正则）
            link_pattern = r'<a[^>]*data-uds-child="breadcrumb-link"[^>]*href="([^"]*)"[^>]*>(.*?)</a>'
            links = re.findall(link_pattern, breadcrumb_html, re.DOTALL | re.IGNORECASE)
            
            for href, link_content in links:
                # 清理链接内容，移除HTML标签
                clean_text = re.sub(r'<[^>]+>', '', link_content).strip()
                clean_text = re.sub(r'\s+', ' ', clean_text)  # 合并多个空格
                
                if clean_text:
                    full_url = href if href.startswith('http') else f"https://us.puma.com{href}"
                    breadcrumb_items.append({
                        'text': clean_text,
                        'url': full_url,
                        'level': len(breadcrumb_items) + 1,
                        'current': False
                    })
                    navigation_parts.append(clean_text)
            
            # 提取当前页面项（非链接项）
            # 查找包含 font-normal 的 li 元素，但不包含 breadcrumb-link
            current_pattern = r'<li[^>]*data-uds-child="breadcrumb-list-item"[^>]*class="[^"]*font-normal[^"]*"[^>]*>(?!.*?<a[^>]*data-uds-child="breadcrumb-link")(.*?)</li>'
            current_matches = re.findall(current_pattern, breadcrumb_html, re.DOTALL | re.IGNORECASE)
            
            if not current_matches:
                # 备用模式：查找不包含breadcrumb-link的li元素
                fallback_pattern = r'<li[^>]*data-uds-child="breadcrumb-list-item"[^>]*>(?!.*?<a[^>]*data-uds-child="breadcrumb-link")[^<]*([^<]+)[^<]*</li>'
                current_matches = re.findall(fallback_pattern, breadcrumb_html, re.DOTALL | re.IGNORECASE)
            
            for match in current_matches:
                clean_text = re.sub(r'<[^>]+>', '', match).strip()
                clean_text = re.sub(r'\s+', ' ', clean_text)  # 合并多个空格
                
                if clean_text and clean_text not in navigation_parts and len(clean_text) > 3:
                    breadcrumb_items.append({
                        'text': clean_text,
                        'url': url or '',
                        'level': len(breadcrumb_items) + 1,
                        'current': True
                    })
                    navigation_parts.append(clean_text)
                    break  # 只取第一个匹配项
            
            # 构建导航路径字符串
            navigation_path = ' > '.join(navigation_parts)
            
            print(f"✅ 正则表达式提取成功: {navigation_path}")
            print(f"   导航项数: {len(breadcrumb_items)}")
            
            for item in breadcrumb_items:
                current_flag = " (当前页面)" if item.get('current') else ""
                print(f"     - {item['text']}{current_flag}")
            
            return breadcrumb_items, navigation_path
            
        except Exception as e:
            print(f"❌ 正则表达式提取失败: {e}")
            import traceback
            traceback.print_exc()
            return [], ""
    
    def _parse_breadcrumb_from_soup(self, breadcrumb_nav, url: str) -> tuple:
        """从 BeautifulSoup 对象中解析面包屑导航"""
        try:
            breadcrumb_items = []
            navigation_parts = []
            
            # 提取所有导航链接
            links = breadcrumb_nav.find_all('a', {'data-uds-child': 'breadcrumb-link'})
            
            for link in links:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                if text:  # 包括所有项，不跳过Home
                    full_url = href if href.startswith('http') else f"https://us.puma.com{href}"
                    breadcrumb_items.append({
                        'text': text,
                        'url': full_url,
                        'level': len(breadcrumb_items) + 1,
                        'current': False
                    })
                    navigation_parts.append(text)
            
            # 提取最后一个非链接的面包屑项（当前页面）
            # 查找具有font-normal类的li元素
            list_items = breadcrumb_nav.find_all('li', {'data-uds-child': 'breadcrumb-list-item'})
            
            for item in list_items:
                # 如果该li没有a标签，说明是当前页面
                if not item.find('a', {'data-uds-child': 'breadcrumb-link'}):
                    current_text = item.get_text(strip=True)
                    # 清理文本，移除多余空格和特殊字符
                    current_text = re.sub(r'\s+', ' ', current_text).strip()
                    
                    if current_text and current_text not in navigation_parts and len(current_text) > 3:
                        breadcrumb_items.append({
                            'text': current_text,
                            'url': url,
                            'level': len(breadcrumb_items) + 1,
                            'current': True
                        })
                        navigation_parts.append(current_text)
                        break
            
            # 构建导航路径字符串
            navigation_path = ' > '.join(navigation_parts)
            
            print(f"✅ BeautifulSoup提取成功: {navigation_path}")
            print(f"   导航项数: {len(breadcrumb_items)}")
            
            for item in breadcrumb_items:
                current_flag = " (当前页面)" if item.get('current') else ""
                print(f"     - {item['text']}{current_flag}")
            
            return breadcrumb_items, navigation_path
            
        except Exception as e:
            print(f"❌ BeautifulSoup解析失败: {e}")
            return [], ""
    
    def _extract_navigation_from_url(self, url: str) -> tuple:
        """从 URL 结构推断导航信息（备用方案）"""
        try:
            print(f"🔧 从 URL 结构推断导航: {url}")
            
            breadcrumb_items = []
            navigation_parts = []
            
            # 从 URL 中解析信息
            # 示例 URL: https://us.puma.com/us/en/pd/suede-xl-leopard-jr-youth/404299
            
            # 添加 Home
            breadcrumb_items.append({
                'text': 'Home',
                'url': 'https://us.puma.com/us/en',
                'level': 1,
                'current': False
            })
            navigation_parts.append('Home')
            
            # 根据 URL 中的信息推断分类
            url_lower = url.lower()
            
            # 判断男女童装
            if '/men/' in url_lower or url.endswith('/men'):
                breadcrumb_items.append({
                    'text': 'Men',
                    'url': 'https://us.puma.com/us/en/men',
                    'level': 2,
                    'current': False
                })
                navigation_parts.append('Men')
                
                # 如果是鞋子相关
                if 'shoes' in url_lower or 'sneakers' in url_lower or 'footwear' in url_lower:
                    breadcrumb_items.append({
                        'text': "Men's Shoes and Sneakers",
                        'url': 'https://us.puma.com/us/en/men/shoes',
                        'level': 3,
                        'current': False
                    })
                    navigation_parts.append("Men's Shoes and Sneakers")
                    
            elif '/women/' in url_lower or url.endswith('/women'):
                breadcrumb_items.append({
                    'text': 'Women',
                    'url': 'https://us.puma.com/us/en/women',
                    'level': 2,
                    'current': False
                })
                navigation_parts.append('Women')
                
                if 'shoes' in url_lower or 'sneakers' in url_lower or 'footwear' in url_lower:
                    breadcrumb_items.append({
                        'text': "Women's Shoes and Sneakers",
                        'url': 'https://us.puma.com/us/en/women/shoes',
                        'level': 3,
                        'current': False
                    })
                    navigation_parts.append("Women's Shoes and Sneakers")
                    
            elif '/kids/' in url_lower or 'youth' in url_lower or 'jr' in url_lower:
                breadcrumb_items.append({
                    'text': 'Kids',
                    'url': 'https://us.puma.com/us/en/kids',
                    'level': 2,
                    'current': False
                })
                navigation_parts.append('Kids')
                
                if 'shoes' in url_lower or 'sneakers' in url_lower or 'footwear' in url_lower:
                    breadcrumb_items.append({
                        'text': "Kids' Shoes and Sneakers",
                        'url': 'https://us.puma.com/us/en/kids/shoes',
                        'level': 3,
                        'current': False
                    })
                    navigation_parts.append("Kids' Shoes and Sneakers")
            
            # 从产品名称中推断当前页面名称
            # 提取产品名称（URL 中 pd 后的部分）
            import re
            product_name_match = re.search(r'/pd/([^/]+)/', url)
            if product_name_match:
                product_slug = product_name_match.group(1)
                # 将连字符转换为空格，并将每个单词的首字母大写
                current_name = product_slug.replace('-', ' ').title()
                breadcrumb_items.append({
                    'text': current_name,
                    'url': url,
                    'level': len(breadcrumb_items) + 1,
                    'current': True
                })
                navigation_parts.append(current_name)
            
            navigation_path = ' > '.join(navigation_parts)
            
            print(f"✅ 从 URL 推断成功: {navigation_path}")
            print(f"   导航项数: {len(breadcrumb_items)}")
            
            for item in breadcrumb_items:
                current_flag = " (当前页面)" if item.get('current') else ""
                print(f"     - {item['text']}{current_flag}")
            
            return breadcrumb_items, navigation_path
            
        except Exception as e:
            print(f"❌ URL 推断失败: {e}")
            return [], ""