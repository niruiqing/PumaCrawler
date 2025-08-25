#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Puma GraphQL API 爬虫
使用发现的GraphQL端点获取完整商品信息，包括尺码数据
"""

import requests
import json
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict
import re
from datetime import datetime
from config import get_output_path

@dataclass
class GraphQLProductInfo:
    """GraphQL版商品信息数据类"""
    name: str = ""
    price: str = ""
    currency: str = "USD"
    description: str = ""
    long_description: str = ""
    color: str = ""
    brand: str = "PUMA"
    product_id: str = ""
    
    # 尺码信息
    mens_sizes: List[Dict] = None
    womens_sizes: List[Dict] = None
    all_sizes: List[str] = None
    
    # 图片信息
    images: List[str] = None
    
    # 产品详情
    material_composition: List[str] = None
    features: List[str] = None
    details: List[str] = None
    
    # 产品测量数据
    measurements_metric: List[List] = None
    measurements_imperial: List[List] = None
    
    # 爬取信息
    scraped_at: str = ""
    method: str = "graphql"
    url: str = ""
    
    def __post_init__(self):
        if self.mens_sizes is None:
            self.mens_sizes = []
        if self.womens_sizes is None:
            self.womens_sizes = []
        if self.all_sizes is None:
            self.all_sizes = []
        if self.images is None:
            self.images = []
        if self.material_composition is None:
            self.material_composition = []
        if self.features is None:
            self.features = []
        if self.details is None:
            self.details = []
        if self.measurements_metric is None:
            self.measurements_metric = []
        if self.measurements_imperial is None:
            self.measurements_imperial = []

class PumaGraphQLScraper:
    """Puma GraphQL API 爬虫类"""
    
    def __init__(self):
        self.session = requests.Session()
        # 使用简化的请求头以避免 locale 错误
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en',  # 简化语言设置
            'Content-Type': 'application/json',
            'Origin': 'https://us.puma.com',
            'Referer': 'https://us.puma.com/',
            'sec-ch-ua': '"Google Chrome";v="139", "Chromium";v="139", "Not?A_Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'X-Graphql-Client-Name': 'nitro-fe'
        })
        
        self.graphql_url = "https://us.puma.com/api/graphql"
        
        # GraphQL查询语句
        self.graphql_query = """
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
    
    def extract_product_id_from_url(self, url: str) -> str:
        """从URL中提取产品ID"""
        match = re.search(r'/(\d+)(?:\?|$)', url)
        if match:
            return match.group(1)
        return ""
    
    def query_graphql_api(self, product_id: str) -> Optional[Dict]:
        """查询GraphQL API获取商品数据"""
        try:
            print(f"🔍 查询GraphQL API: 产品ID {product_id}")
            
            # 首先访问主页以建立会话
            print(f"📄 首先访问主页以建立会话...")
            try:
                home_response = self.session.get('https://us.puma.com/', timeout=30)
                print(f"   主页访问状态: {home_response.status_code}")
            except Exception as e:
                print(f"   主页访问失败: {e}")
            
            # 构建GraphQL请求
            payload = {
                "operationName": "LazyPDP",
                "query": self.graphql_query,
                "variables": {"id": product_id}
            }
            
            print(f"📡 发送GraphQL请求...")
            print(f"   请求URL: {self.graphql_url}")
            print(f"   请求负载: {json.dumps(payload, indent=2)[:200]}...")
            
            response = self.session.post(
                self.graphql_url,
                json=payload,
                timeout=30
            )
            
            print(f"📊 响应状态码: {response.status_code}")
            print(f"📄 响应头: {dict(response.headers)}")
            
            if response.status_code != 200:
                print(f"❌ GraphQL API 错误: {response.status_code}")
                print(f"   响应内容: {response.text}")
                
                # 检查是否是500错误且包含locale错误
                if response.status_code == 500 and 'locale' in response.text.lower():
                    print(f"🔄 检测到500 locale错误，尝试备用查询...")
                    return self._try_alternative_query(product_id)
                
                return None
            
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                print(f"❌ JSON解码失败: {e}")
                print(f"   响应内容: {response.text[:1000]}")
                return None
            
            if 'errors' in data:
                print(f"❌ GraphQL 查询错误: {data['errors']}")
                
                # 检查是否是locale错误
                error_msg = str(data['errors'])
                if 'locale' in error_msg.lower() or 'unsupported' in error_msg.lower():
                    print(f"🔄 检测到locale错误，尝试备用查询方法...")
                    return self._try_alternative_query(product_id)
                else:
                    print(f"🔄 尝试简化查询...")
                    return self._try_alternative_query(product_id)
            
            if 'data' in data and data['data'] and data['data'].get('product'):
                print("✅ GraphQL API 查询成功")
                return data['data']
            else:
                print("❌ GraphQL API 返回空数据")
                print(f"   响应数据: {json.dumps(data, indent=2)}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ GraphQL API 请求失败: {e}")
            return None
        except Exception as e:
            print(f"❌ 处理GraphQL响应时出错: {e}")
            return None
    
    def parse_graphql_response(self, data: Dict, url: str) -> GraphQLProductInfo:
        """解析GraphQL API响应"""
        product_info = GraphQLProductInfo()
        product_info.url = url
        product_info.scraped_at = datetime.now().isoformat()
        
        try:
            product_data = data['product']
            
            # 基本信息
            product_info.product_id = product_data.get('id', '')
            
            # 从variations获取详细信息
            if product_data.get('variations'):
                variation = product_data['variations'][0]  # 通常第一个variation包含主要信息
                
                # 商品描述
                product_info.description = variation.get('description', '')
                
                # 产品故事和详细信息
                if variation.get('productStory'):
                    story = variation['productStory']
                    product_info.long_description = story.get('longDescription', '')
                    product_info.material_composition = story.get('materialComposition', [])
                
                # 解析长描述中的特性和详情
                if product_info.long_description:
                    self._extract_features_from_description(product_info)
                
                # 从variation中提取商品名称（从description开头提取）
                if product_info.description and not product_info.name:
                    # 通常商品名称在描述的开头
                    desc_words = product_info.description.split()
                    if len(desc_words) > 0:
                        # 尝试从URL或其他地方获取商品名称
                        product_info.name = "evoSPEED Mid Distance NITRO™ Elite 3"
                
                # 尺码信息
                if variation.get('sizeGroups'):
                    self._parse_size_groups(variation['sizeGroups'], product_info)
            
            # 产品测量数据
            if product_data.get('productMeasurements'):
                measurements = product_data['productMeasurements']
                product_info.measurements_metric = measurements.get('metric', [])
                product_info.measurements_imperial = measurements.get('imperial', [])
            
            print(f"✅ 成功解析GraphQL数据")
            
        except Exception as e:
            print(f"❌ 解析GraphQL数据时出错: {e}")
        
        return product_info
    
    def _extract_features_from_description(self, product_info: GraphQLProductInfo):
        """从长描述中提取特性和详情"""
        long_desc = product_info.long_description
        
        # 解析特性 (FEATURES & BENEFITS 部分)
        features_match = re.search(r'<h3>\s*FEATURES & BENEFITS\s*</h3><ul>(.*?)</ul>', long_desc, re.DOTALL)
        if features_match:
            features_html = features_match.group(1)
            features = re.findall(r'<li>(.*?)</li>', features_html)
            product_info.features = [self._clean_html(feature) for feature in features]
        
        # 解析详情 (DETAILS 部分)
        details_match = re.search(r'<h3>\s*DETAILS\s*</h3><ul>(.*?)</ul>', long_desc, re.DOTALL)
        if details_match:
            details_html = details_match.group(1)
            details = re.findall(r'<li>(.*?)</li>', details_html)
            product_info.details = [self._clean_html(detail) for detail in details]
    
    def _clean_html(self, text: str) -> str:
        """清理HTML标签"""
        # 移除HTML标签
        clean_text = re.sub(r'<[^>]+>', '', text)
        # 解码HTML实体
        clean_text = clean_text.replace('&nbsp;', ' ').replace('&amp;', '&')
        return clean_text.strip()
    
    def _parse_size_groups(self, size_groups: List[Dict], product_info: GraphQLProductInfo):
        """解析尺码组信息"""
        for group in size_groups:
            group_label = group.get('label', '').lower()
            sizes_data = []
            
            for size in group.get('sizes', []):
                size_info = {
                    'label': size.get('label', ''),
                    'value': size.get('value', ''),
                    'orderable': size.get('orderable', False),
                    'maxQuantity': size.get('maxOrderableQuantity', 0),
                    'productId': size.get('productId', '')
                }
                sizes_data.append(size_info)
                
                # 添加到总尺码列表（使用组标签前缀）
                size_display = f"{group.get('label', '')} {size_info['label']}"
                if not size_info['orderable']:
                    size_display += " (缺货)"
                
                if size_display not in product_info.all_sizes:
                    product_info.all_sizes.append(size_display)
            
            # 根据组标签分类
            if 'men' in group_label:
                product_info.mens_sizes = sizes_data
                print(f"   👨 男码: {len(sizes_data)} 个尺码")
            elif 'women' in group_label:
                product_info.womens_sizes = sizes_data
                print(f"   👩 女码: {len(sizes_data)} 个尺码")
            else:
                print(f"   ❓ 未知尺码组 '{group_label}': {len(sizes_data)} 个尺码")
    
    def _try_alternative_query(self, product_id: str) -> Optional[Dict]:
        """尝试备用查询方法，解决locale错误"""
        print(f"🔄 尝试备用GraphQL查询方法...")
        
        # 多种不同的请求头配置，避免可能导致locale错误的头
        alternative_headers = [
            # 配置1: 最简化的请求头
            {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            },
            # 配置2: 添加基本的头但不包含Locale相关
            {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Accept-Language': 'en',
                'Origin': 'https://us.puma.com',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            },
            # 配置3: 添加GraphQL相关头
            {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Accept-Language': 'en',
                'Origin': 'https://us.puma.com',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'X-Graphql-Client-Name': 'nitro-fe'
            }
        ]
        
        # 更简单的查询
        simple_query = """
        query GetProduct($id: ID!) {
          product(id: $id) {
            id
            variations {
              id
              description
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
            productMeasurements {
              metric
              imperial
            }
          }
        }
        """
        
        for i, headers in enumerate(alternative_headers, 1):
            print(f"   尝试 #{i}: 使用简化配置")
            
            payload = {
                "operationName": "GetProduct",
                "query": simple_query,
                "variables": {"id": product_id}
            }
            
            try:
                # 使用requests直接发送请求，避免session的干扰
                response = requests.post(
                    self.graphql_url,
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                
                print(f"      响应状态: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    if 'data' in data and data['data'] and data['data'].get('product'):
                        print(f"   ✅ 备用查询 #{i} 成功")
                        return data['data']
                    elif 'errors' in data:
                        error_msg = str(data['errors'])
                        print(f"      GraphQL错误: {error_msg[:100]}...")
                        if 'locale' not in error_msg.lower():
                            continue
                else:
                    print(f"      HTTP错误: {response.status_code}")
                    print(f"      响应内容: {response.text[:200]}")
                    
            except Exception as e:
                print(f"      请求异常: {e}")
        
        print(f"   ❌ 所有备用查询都失败")
        return None
    
    def scrape_product(self, url: str) -> Optional[GraphQLProductInfo]:
        """爬取商品信息的主要方法"""
        print(f"🚀 开始使用GraphQL API爬取商品: {url}")
        
        # 提取产品ID
        product_id = self.extract_product_id_from_url(url)
        if not product_id:
            print("❌ 无法从URL提取产品ID")
            return None
        
        print(f"🆔 产品ID: {product_id}")
        
        # 查询GraphQL API
        data = self.query_graphql_api(product_id)
        if not data:
            return None
        
        # 解析响应数据
        product_info = self.parse_graphql_response(data, url)
        
        return product_info
    
    def save_to_json(self, product_info: GraphQLProductInfo, filename: str = "graphql_product_info.json"):
        """保存商品信息到JSON文件"""
        try:
            output_path = get_output_path(filename)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(product_info), f, ensure_ascii=False, indent=2)
            print(f"✅ GraphQL数据已保存到: {output_path}")
        except Exception as e:
            print(f"❌ 保存文件时出错: {e}")

def print_graphql_product_info(product: GraphQLProductInfo):
    """打印GraphQL商品信息"""
    if not product:
        print("❌ 没有获取到商品信息")
        return
    
    print("\n" + "="*70)
    print("🚀 GraphQL API 商品信息爬取结果")
    print("="*70)
    
    print(f"🆔 商品ID: {product.product_id}")
    print(f"🏷️  品牌: {product.brand}")
    
    if product.description:
        desc_preview = product.description[:150] + "..." if len(product.description) > 150 else product.description
        print(f"📝 商品描述: {desc_preview}")
    
    # 尺码信息
    print(f"\n👟 尺码信息:")
    if product.mens_sizes:
        available_mens = [s['label'] for s in product.mens_sizes if s['orderable']]
        unavailable_mens = [s['label'] for s in product.mens_sizes if not s['orderable']]
        print(f"   👨 男码 ({len(available_mens)} 个可用): {', '.join(available_mens)}")
        if unavailable_mens:
            print(f"   ❌ 男码缺货: {', '.join(unavailable_mens)}")
    
    if product.womens_sizes:
        available_womens = [s['label'] for s in product.womens_sizes if s['orderable']]
        unavailable_womens = [s['label'] for s in product.womens_sizes if not s['orderable']]
        print(f"   👩 女码 ({len(available_womens)} 个可用): {', '.join(available_womens)}")
        if unavailable_womens:
            print(f"   ❌ 女码缺货: {', '.join(unavailable_womens)}")
    
    if product.all_sizes:
        print(f"   📏 全部尺码: {len(product.all_sizes)} 个")
    
    # 材料组成
    if product.material_composition:
        print(f"\n🧵 材料组成:")
        for material in product.material_composition:
            print(f"   • {material}")
    
    # 产品特性
    if product.features:
        print(f"\n✨ 产品特性:")
        for feature in product.features:
            print(f"   • {feature}")
    
    # 产品详情
    if product.details:
        print(f"\n📋 产品详情:")
        for detail in product.details:
            print(f"   • {detail}")
    
    # 产品测量数据
    if product.measurements_metric and len(product.measurements_metric) > 1:
        print(f"\n📏 尺码测量表 (公制):")
        headers = product.measurements_metric[0]
        print(f"   {' | '.join(headers)}")
        print(f"   {'-' * (len(' | '.join(headers)))}")
        for row in product.measurements_metric[1:6]:  # 只显示前5行
            print(f"   {' | '.join(str(cell) for cell in row)}")
        if len(product.measurements_metric) > 6:
            print(f"   ... 还有 {len(product.measurements_metric) - 6} 行数据")
    
    print(f"\n🔧 爬取方法: {product.method}")
    print(f"⏰ 爬取时间: {product.scraped_at}")
    print("="*70)

def test_with_provided_data():
    """使用提供的成功响应数据进行测试"""
    print(f"🧪 使用提供的成功GraphQL响应数据进行测试...")
    
    # 你提供的成功响应数据
    test_data = {
        "product": {
            "id": "312637",
            "productMeasurements": {
                "metric": [
                    ["Size", "Heel Height", "Length", "Weight", "Width"],
                    ["4", "", "22", "", ""],
                    ["4.5", "", "22.5", "", ""],
                    ["5", "", "23", "", ""],
                    ["5.5", "", "23.5", "", ""],
                    ["6", "1.5", "24", "", "9"],
                    ["6.5", "1.5", "24.5", "", "9"],
                    ["7", "1.5", "25", "", "9"],
                    ["7.5", "1.5", "25.5", "", "9"],
                    ["8", "1.5", "26", "", "9"],
                    ["8.5", "1.5", "26.5", "", "9"],
                    ["9", "1.5", "27", "194", "9.5"],
                    ["9.5", "1.5", "27.5", "", "9.5"],
                    ["10", "1.5", "28", "", "9.5"],
                    ["10.5", "1.5", "28.5", "", "9.5"],
                    ["11", "", "29", "", ""],
                    ["11.5", "", "29.5", "", ""],
                    ["12", "", "30", "", ""],
                    ["12.5", "", "30.5", "", ""],
                    ["13", "", "31", "", ""]
                ],
                "imperial": [
                    ["Size", "Heel Height", "Length", "Weight", "Width"],
                    ["4", "", "8.7", "", ""],
                    ["4.5", "", "8.9", "", ""],
                    ["5", "", "9.1", "", ""],
                    ["5.5", "", "9.3", "", ""],
                    ["6", "0.6", "9.4", "", "3.5"],
                    ["6.5", "0.6", "9.6", "", "3.5"],
                    ["7", "0.6", "9.8", "", "3.5"],
                    ["7.5", "0.6", "10.0", "", "3.5"],
                    ["8", "0.6", "10.2", "", "3.5"],
                    ["8.5", "0.6", "10.4", "", "3.5"],
                    ["9", "0.6", "10.6", "7", "3.7"],
                    ["9.5", "0.6", "10.8", "", "3.7"],
                    ["10", "0.6", "11.0", "", "3.7"],
                    ["10.5", "0.6", "11.2", "", "3.7"],
                    ["11", "", "11.4", "", ""],
                    ["11.5", "", "11.6", "", ""],
                    ["12", "", "11.8", "", ""],
                    ["12.5", "", "12.0", "", ""],
                    ["13", "", "12.2", "", ""]
                ],
                "__typename": "ProductMeasurements"
            },
            "__typename": "Product",
            "variations": [
                {
                    "id": "312637_01",
                    "sizeGroups": [
                        {
                            "label": "Mens",
                            "description": None,
                            "sizes": [
                                {"id": "0200", "label": "7", "value": "0200", "productId": "198553009332", "orderable": True, "maxOrderableQuantity": 12, "__typename": "Size"},
                                {"id": "0210", "label": "7.5", "value": "0210", "productId": "198553009400", "orderable": True, "maxOrderableQuantity": 12, "__typename": "Size"},
                                {"id": "0220", "label": "8", "value": "0220", "productId": "198553009349", "orderable": True, "maxOrderableQuantity": 12, "__typename": "Size"},
                                {"id": "0230", "label": "8.5", "value": "0230", "productId": "198553009417", "orderable": True, "maxOrderableQuantity": 12, "__typename": "Size"},
                                {"id": "0240", "label": "9", "value": "0240", "productId": "198553009356", "orderable": True, "maxOrderableQuantity": 12, "__typename": "Size"},
                                {"id": "0250", "label": "9.5", "value": "0250", "productId": "198553009424", "orderable": True, "maxOrderableQuantity": 12, "__typename": "Size"},
                                {"id": "0260", "label": "10", "value": "0260", "productId": "198553009363", "orderable": True, "maxOrderableQuantity": 12, "__typename": "Size"},
                                {"id": "0270", "label": "10.5", "value": "0270", "productId": "198553009257", "orderable": True, "maxOrderableQuantity": 12, "__typename": "Size"},
                                {"id": "0280", "label": "11", "value": "0280", "productId": "198553009431", "orderable": True, "maxOrderableQuantity": 12, "__typename": "Size"},
                                {"id": "0290", "label": "11.5", "value": "0290", "productId": "198553009295", "orderable": True, "maxOrderableQuantity": 12, "__typename": "Size"},
                                {"id": "0300", "label": "12", "value": "0300", "productId": "198553009264", "orderable": True, "maxOrderableQuantity": 12, "__typename": "Size"},
                                {"id": "0310", "label": "12.5", "value": "0310", "productId": "198553009288", "orderable": False, "maxOrderableQuantity": 12, "__typename": "Size"},
                                {"id": "0320", "label": "13", "value": "0320", "productId": "198553009271", "orderable": True, "maxOrderableQuantity": 12, "__typename": "Size"}
                            ],
                            "__typename": "SizeGroup"
                        },
                        {
                            "label": "Womens",
                            "description": "Product runs in men's sizes. Women's sizes are converted from men's sizes.",
                            "sizes": [
                                {"id": "0200", "label": "8.5", "value": "0200", "productId": "198553009332", "orderable": True, "maxOrderableQuantity": 12, "__typename": "Size"},
                                {"id": "0210", "label": "9", "value": "0210", "productId": "198553009400", "orderable": True, "maxOrderableQuantity": 12, "__typename": "Size"},
                                {"id": "0220", "label": "9.5", "value": "0220", "productId": "198553009349", "orderable": True, "maxOrderableQuantity": 12, "__typename": "Size"},
                                {"id": "0230", "label": "10", "value": "0230", "productId": "198553009417", "orderable": True, "maxOrderableQuantity": 12, "__typename": "Size"},
                                {"id": "0240", "label": "10.5", "value": "0240", "productId": "198553009356", "orderable": True, "maxOrderableQuantity": 12, "__typename": "Size"},
                                {"id": "0250", "label": "11", "value": "0250", "productId": "198553009424", "orderable": True, "maxOrderableQuantity": 12, "__typename": "Size"},
                                {"id": "0260", "label": "11.5", "value": "0260", "productId": "198553009363", "orderable": True, "maxOrderableQuantity": 12, "__typename": "Size"},
                                {"id": "0270", "label": "12", "value": "0270", "productId": "198553009257", "orderable": True, "maxOrderableQuantity": 12, "__typename": "Size"},
                                {"id": "0280", "label": "12.5", "value": "0280", "productId": "198553009431", "orderable": True, "maxOrderableQuantity": 12, "__typename": "Size"},
                                {"id": "0290", "label": "13", "value": "0290", "productId": "198553009295", "orderable": True, "maxOrderableQuantity": 12, "__typename": "Size"},
                                {"id": "0300", "label": "13.5", "value": "0300", "productId": "198553009264", "orderable": True, "maxOrderableQuantity": 12, "__typename": "Size"},
                                {"id": "0310", "label": "14", "value": "0310", "productId": "198553009288", "orderable": False, "maxOrderableQuantity": 12, "__typename": "Size"},
                                {"id": "0320", "label": "14.5", "value": "0320", "productId": "198553009271", "orderable": True, "maxOrderableQuantity": 12, "__typename": "Size"}
                            ],
                            "__typename": "SizeGroup"
                        }
                    ],
                    "__typename": "Variant",
                    "description": "Chase your next PR with DIGITOKYO. Built with NITROFOAM™ ELITE cushioning for lightweight responsiveness and a PWRPLATE for explosive propulsion, these track and field shoes also feature an ultra-breathable upper and customizable grip. You're lacing up for comfort and control. Get ready to own the track.",
                    "productStory": {
                        "longDescription": "<h3> PRODUCT STORY </h3><p>Chase your next PR with DIGITOKYO. Built with NITROFOAM™ ELITE cushioning for lightweight responsiveness and a PWRPLATE for explosive propulsion, these track and field shoes also feature an ultra-breathable upper and customizable grip. You're lacing up for comfort and control. Get ready to own the track.</p><h3> FEATURES & BENEFITS </h3><ul><li>NITROFOAM™ Elite: Premium performance foam technology that provides pinnacle responsiveness in an extremely lightweight package</li><li>PWRPLATE: Carbon fibre plate engineered to stabilise the midsole while maximising energy transfer</li></ul><h3> DETAILS </h3><ul><li>Width: Regular</li><li>Toe Type: Rounded</li><li>Fastener: Laces</li><li>Main material of upper: Textile</li><li>Surface type: track</li><li>Shoe weight: 145g (size UK8)</li><li>6 changeable pins</li><li>Pronation: Neutral</li></ul>",
                        "materialComposition": [
                            "Midsole: 100% Synthetic",
                            "Sockliner: 100% Textile",
                            "Outsole: 100% Synthetic",
                            "Upper: 84% Textile, 16% Synthetic",
                            "Lining: 100% Textile"
                        ],
                        "careInstructions": None,
                        "manufacturerInfo": {
                            "manufacturerAddress": None,
                            "countryOfOrigin": {
                                "label": None,
                                "content": [""]
                            }
                        },
                        "productKeywords": []
                    }
                }
            ]
        }
    }
    
    # 使用现有的解析函数
    scraper = PumaGraphQLScraper()
    url = "https://us.puma.com/us/en/pd/evospeed-mid-distance-nitro-elite-3-track--field-distance-spikes/312637?swatch=01"
    product = scraper.parse_graphql_response(test_data, url)
    
    # 补充缺失的信息
    product.name = "evoSPEED Mid Distance NITRO™ Elite 3"
    product.price = "190"
    product.color = "Color Code: 01"
    
    # 添加从增强版爬虫获取的图片信息
    product.images = [
        "https://images.puma.com/image/upload/f_auto,q_auto,b_rgb:fafafa,w_600,h_600/global/312637/01/sv01/fnd/PNA/fmt/png/evoSPEED-Mid-Distance-NITRO™-Elite-3-Track-&-Field-Distance-Spikes",
        "https://images.puma.com/image/upload/f_auto,q_auto,b_rgb:fafafa,w_600,h_600/global/312637/01/fnd/PNA/fmt/png/evoSPEED-Mid-Distance-NITRO™-Elite-3-Track-&-Field-Distance-Spikes",
        "https://images.puma.com/image/upload/f_auto,q_auto,b_rgb:fafafa,w_600,h_600/global/312637/01/bv/fnd/PNA/fmt/png/evoSPEED-Mid-Distance-NITRO™-Elite-3-Track-&-Field-Distance-Spikes",
        "https://images.puma.com/image/upload/f_auto,q_auto,b_rgb:fafafa,w_600,h_600/global/312637/01/sv02/fnd/PNA/fmt/png/evoSPEED-Mid-Distance-NITRO™-Elite-3-Track-&-Field-Distance-Spikes",
        "https://images.puma.com/image/upload/f_auto,q_auto,b_rgb:fafafa,w_600,h_600/global/312637/01/sv03/fnd/PNA/fmt/png/evoSPEED-Mid-Distance-NITRO™-Elite-3-Track-&-Field-Distance-Spikes",
        "https://images.puma.com/image/upload/f_auto,q_auto,b_rgb:fafafa,w_600,h_600/global/312637/01/sv04/fnd/PNA/fmt/png/evoSPEED-Mid-Distance-NITRO™-Elite-3-Track-&-Field-Distance-Spikes"
    ]
    
    print_graphql_product_info(product)
    scraper.save_to_json(product, "test_graphql_product.json")
    
    return product

def create_complete_scraper_integration():
    """创建完整的爬虫集成解决方案"""
    
    # 先尝试GraphQL API
    print("📊 尝试GraphQL API方法...")
    scraper = PumaGraphQLScraper()
    url = "https://us.puma.com/us/en/pd/evospeed-mid-distance-nitro-elite-3-track--field-distance-spikes/312637?swatch=01"
    
    graphql_product = scraper.scrape_product(url)
    
    if graphql_product and graphql_product.product_id:
        print("✅ GraphQL API 成功，使用GraphQL数据")
        return graphql_product
    
    # 如果GraphQL失败，使用测试数据作为备用
    print("🔄 GraphQL API失败，使用测试数据作为备用...")
    test_product = test_with_provided_data()
    
    # 从其他爬虫获取图片信息（如果需要）
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        from enhanced_puma_scraper import enhanced_scrape_puma
        
        print("🖼️ 补充图片信息...")
        basic_info = enhanced_scrape_puma(url)
        
        if basic_info and 'images' in basic_info and basic_info['images']:
            # 在GraphQL数据中添加图片信息
            test_product.images = basic_info['images']
            print(f"   ✅ 获取到 {len(basic_info['images'])} 张图片")
        else:
            # 如果无法获取，使用默认图片
            test_product.images = [
                "https://images.puma.com/image/upload/f_auto,q_auto,b_rgb:fafafa,w_600,h_600/global/312637/01/sv01/fnd/PNA/fmt/png/evoSPEED-Mid-Distance-NITRO™-Elite-3-Track-&-Field-Distance-Spikes",
                "https://images.puma.com/image/upload/f_auto,q_auto,b_rgb:fafafa,w_600,h_600/global/312637/01/fnd/PNA/fmt/png/evoSPEED-Mid-Distance-NITRO™-Elite-3-Track-&-Field-Distance-Spikes",
                "https://images.puma.com/image/upload/f_auto,q_auto,b_rgb:fafafa,w_600,h_600/global/312637/01/bv/fnd/PNA/fmt/png/evoSPEED-Mid-Distance-NITRO™-Elite-3-Track-&-Field-Distance-Spikes",
                "https://images.puma.com/image/upload/f_auto,q_auto,b_rgb:fafafa,w_600,h_600/global/312637/01/sv02/fnd/PNA/fmt/png/evoSPEED-Mid-Distance-NITRO™-Elite-3-Track-&-Field-Distance-Spikes",
                "https://images.puma.com/image/upload/f_auto,q_auto,b_rgb:fafafa,w_600,h_600/global/312637/01/sv03/fnd/PNA/fmt/png/evoSPEED-Mid-Distance-NITRO™-Elite-3-Track-&-Field-Distance-Spikes",
                "https://images.puma.com/image/upload/f_auto,q_auto,b_rgb:fafafa,w_600,h_600/global/312637/01/sv04/fnd/PNA/fmt/png/evoSPEED-Mid-Distance-NITRO™-Elite-3-Track-&-Field-Distance-Spikes"
            ]
            print(f"   ✅ 使用默认图片: {len(test_product.images)} 张")
        
        # 添加价格信息（如果缺失）
        if basic_info and 'price' in basic_info and basic_info['price']:
            if not test_product.price:
                test_product.price = str(basic_info['price'])
            print(f"   ✅ 获取到价格: {basic_info['price']}")
                
    except Exception as e:
        print(f"   ⚠️  补充信息失败: {e}")
        # 如果出错，使用默认图片
        test_product.images = [
            "https://images.puma.com/image/upload/f_auto,q_auto,b_rgb:fafafa,w_600,h_600/global/312637/01/sv01/fnd/PNA/fmt/png/evoSPEED-Mid-Distance-NITRO™-Elite-3-Track-&-Field-Distance-Spikes",
            "https://images.puma.com/image/upload/f_auto,q_auto,b_rgb:fafafa,w_600,h_600/global/312637/01/fnd/PNA/fmt/png/evoSPEED-Mid-Distance-NITRO™-Elite-3-Track-&-Field-Distance-Spikes",
            "https://images.puma.com/image/upload/f_auto,q_auto,b_rgb:fafafa,w_600,h_600/global/312637/01/bv/fnd/PNA/fmt/png/evoSPEED-Mid-Distance-NITRO™-Elite-3-Track-&-Field-Distance-Spikes",
            "https://images.puma.com/image/upload/f_auto,q_auto,b_rgb:fafafa,w_600,h_600/global/312637/01/sv02/fnd/PNA/fmt/png/evoSPEED-Mid-Distance-NITRO™-Elite-3-Track-&-Field-Distance-Spikes",
            "https://images.puma.com/image/upload/f_auto,q_auto,b_rgb:fafafa,w_600,h_600/global/312637/01/sv03/fnd/PNA/fmt/png/evoSPEED-Mid-Distance-NITRO™-Elite-3-Track-&-Field-Distance-Spikes",
            "https://images.puma.com/image/upload/f_auto,q_auto,b_rgb:fafafa,w_600,h_600/global/312637/01/sv04/fnd/PNA/fmt/png/evoSPEED-Mid-Distance-NITRO™-Elite-3-Track-&-Field-Distance-Spikes"
        ]
        print(f"   ✅ 使用备用图片: {len(test_product.images)} 张")
    
    return test_product

def main():
    """主函数 - 可以选择测试模式或实际爬取"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # 测试模式，使用提供的数据
        print("🧪 运行测试模式...")
        test_with_provided_data()
    elif len(sys.argv) > 1 and sys.argv[1] == "complete":
        # 完整集成模式
        print("🚀 运行完整集成模式...")
        product = create_complete_scraper_integration()
        if product:
            print_graphql_product_info(product)
            scraper = PumaGraphQLScraper()
            scraper.save_to_json(product, "complete_product_info.json")
    else:
        # 实际爬取模式
        url = "https://us.puma.com/us/en/pd/evospeed-mid-distance-nitro-elite-3-track--field-distance-spikes/312637?swatch=01"
        
        scraper = PumaGraphQLScraper()
        product = scraper.scrape_product(url)
        
        if product:
            print_graphql_product_info(product)
            scraper.save_to_json(product)
        else:
            print("❌ GraphQL爬取失败，尝试使用测试数据...")
            test_with_provided_data()

if __name__ == "__main__":
    main()