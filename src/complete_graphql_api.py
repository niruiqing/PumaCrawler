#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的PUMA GraphQL API接口
基于用户提供的完整curl请求，实现完整的商品信息获取，包括尺码信息
"""

import requests
import json
import re
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional, Dict, List
from config import get_output_path

@dataclass
class CompleteProductInfo:
    """完整的商品信息数据结构"""
    # 基本信息
    product_id: str = ""
    name: str = ""
    header: str = ""
    sub_header: str = ""
    description: str = ""
    brand: str = ""
    
    # 价格信息
    price: str = ""
    sale_price: str = ""
    promotion_price: str = ""
    best_price: str = ""
    
    # 颜色和变体信息
    color_name: str = ""
    color_value: str = ""
    orderable: bool = False
    style_number: str = ""
    
    # 图片信息
    images: List[str] = None
    
    # 尺码信息
    sizes: Dict = None
    
    # 材料和制造信息
    material_composition: List[str] = None
    manufacturer_info: Dict = None
    
    # 促销和徽章信息
    promotions: List[Dict] = None
    badges: List[Dict] = None
    
    # 库存和订购信息
    display_out_of_stock: Dict = None
    is_final_sale: bool = False
    
    # 评价信息
    average_rating: str = ""
    amount_of_reviews: str = ""
    
    # 其他信息
    size_chart_id: str = ""
    product_division: str = ""
    ean: str = ""
    
    # 元数据
    scraped_at: str = ""
    method: str = ""
    url: str = ""
    
    def __post_init__(self):
        if self.images is None:
            self.images = []
        if self.material_composition is None:
            self.material_composition = []
        if self.promotions is None:
            self.promotions = []
        if self.badges is None:
            self.badges = []

class CompleteGraphQLAPI:
    """完整的PUMA GraphQL API客户端"""
    
    def __init__(self):
        self.session = requests.Session()
        self.graphql_url = "https://us.puma.com/api/graphql"
        
        # 基于最新认证信息构建请求头
        self.headers = {
            'accept': 'application/graphql-response+json, application/graphql+json, application/json',
            'accept-language': 'zh-CN,zh;q=0.9',
            'authorization': 'Bearer eyJ2ZXIiOiIxLjAiLCJqa3UiOiJzbGFzL3Byb2QvYmNqcF9wcmQiLCJraWQiOiI2OGI4OWE0Mi02ZjAwLTQzYWUtYjRjNC1hZmRmMGUzZWFlNzQiLCJ0eXAiOiJqd3QiLCJjbHYiOiJKMi4zLjQiLCJhbGciOiJFUzI1NiJ9.eyJhdXQiOiJHVUlEIiwic2NwIjoic2ZjYy5zaG9wcGVyLW15YWNjb3VudC5iYXNrZXRzIHNmY2Muc2hvcHBlci1teWFjY291bnQuYWRkcmVzc2VzIHNmY2Muc2hvcHBlci1wcm9kdWN0cyBzZmNjLnNob3BwZXItbXlhY2NvdW50LnJ3IHNmY2Muc2hvcHBlci1teWFjY291bnQucGF5bWVudGluc3RydW1lbnRzIHNmY2Muc2hvcHBlci1jdXN0b21lcnMubG9naW4gc2ZjYy5zaG9wcGVyLWNvbnRleHQgc2ZjYy5zaG9wcGVyLWNvbnRleHQucncgc2ZjYy5zaG9wcGVyLW15YWNjb3VudC5vcmRlcnMgc2ZjYy5zaG9wcGVyLWN1c3RvbWVycy5yZWdpc3RlciBzZmNjLnNob3BwZXItYmFza2V0cy1vcmRlcnMgc2ZjYy5zaG9wcGVyLW15YWNjb3VudC5hZGRyZXNzZXMucncgc2ZjYy5zaG9wcGVyLW15YWNjb3VudC5wcm9kdWN0bGlzdHMucncgc2ZjYy5zaG9wcGVyLXByb2R1Y3RsaXN0cyBzZmNjLnNob3BwZXItcHJvbW90aW9ucyBzZmNjLnNob3BwZXItYmFza2V0cy1vcmRlcnMucncgc2ZjYy5zaG9wcGVyLW15YWNjb3VudC5wYXltZW50aW5zdHJ1bWVudHMucncgc2ZjYy5zaG9wcGVyLWdpZnQtY2VydGlmaWNhdGVzIHNmY2Muc2hvcHBlci1wcm9kdWN0LXNlYXJjaCBzZmNjLnNob3BwZXItbXlhY2NvdW50LnByb2R1Y3RsaXN0cyBzZmNjLnNob3BwZXItY2F0ZWdvcmllcyBzZmNjLnNob3BwZXItbXlhY2NvdW50Iiwic3ViIjoiY2Mtc2xhczo6YmNqcF9wcmQ6OnNjaWQ6MWM4YzhhM2UtNjU2ZS00MWIxLThiNmYtZmIwNmM0NTFmMDE5Ojp1c2lkOjU3Yjk3ZDc0LTIzZWEtNGIxZi05YzZkLTE4NTVlODI1Y2Q5NiIsImN0eCI6InNsYXMiLCJpc3MiOiJzbGFzL3Byb2QvYmNqcF9wcmQiLCJpc3QiOjEsImRudCI6IjAiLCJhdWQiOiJjb21tZXJjZWNsb3VkL3Byb2QvYmNqcF9wcmQiLCJuYmYiOjE3NTYwODg4ODUsInN0eSI6IlVzZXIiLCJpc2IiOiJ1aWRvOnNsYXM6OnVwbjpHdWVzdDo6dWlkbjpHdWVzdCBVc2VyOjpnY2lkOmFibHJCR21yQklsWG9Sa0hsSndxWVl3SGRLOjpjaGlkOk5BIiwiZXhwIjoxNzU2MDkwNzE1LCJpYXQiOjE3NTYwODg5MTUsImp0aSI6IkMyQy0xODQ0NjA0NzcwMDc0MDYzNDc3MzQ3NjM0MTY2MzA0NTcxMTcifQ.oXAFWFX2Thwrc0mJ0tuYq9E5sDtJHNojKeKYHgv8-Z5zVGkCePB03QjyFw-lE_6EiM4ZW7tE6fFOqOaXYcqqiA',
            'bloomreach-id': 'uid=2119450463975:v=12.0:ts=1756085787277:hc=4',
            'content-type': 'application/json',
            'customer-group': 'a078f6706670a82b26dee50e6d7d1dacb6d532351e60c225876bec5eb416cf4f',
            'customer-id': 'ablrBGmrBIlXoRkHlJwqYYwHdK',
            'locale': 'en-US',
            'origin': 'https://us.puma.com',
            'priority': 'u=1, i',
            'puma-request-source': 'web',
            'refresh-token': 'YSnG2ZM7TIQoavZQYts9b5zwREzFLVffDdSOmrkhvmM',
            'sec-ch-ua': '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
            'x-graphql-client-name': 'nitro-fe',
            'x-graphql-client-version': '961757de4b96db7c1c36770d26de3e4fb6f16f24',
            'x-operation-name': 'PDP'
        }
        
        # 基本商品信息查询
        self.graphql_query = """query PDP($id: ID!) {
  product(id: $id) {
    ...mandatoryMasterFields
    productNameTranslated
    description
    primaryCategoryId
    productDivision
    brand
    disableRatings
    disableReviews
    amountOfReviews
    averageRating
    sizeChartId
    promotions(page: ProductDetailsPage) {
      id
      calloutMessage
      __typename
    }
    orderable
    variations {
      ...pdpMandatoryVariantFields
      isFinalSale
      ean
      badges {
        id
        label
        __typename
      }
      salePrice
      productPrice {
        price
        salePrice
        promotionPrice
        bestPrice
        __typename
      }
      styleNumber
      materialComposition
      displayOutOfStock {
        soldout
        soldoutWithRecommender
        comingsoon
        backsoon
        presale
        displayValue
        validTo
        __typename
      }
      orderable
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
      __typename
    }
    __typename
  }
}
fragment mandatoryMasterFields on Product {
  name
  id
  header
  subHeader
  orderableColorCount
  displayOutOfStock {
    soldout
    soldoutWithRecommender
    comingsoon
    backsoon
    presale
    displayValue
    __typename
  }
  colors {
    name
    value
    image {
      href
      verticalImageHref
      alt
      __typename
    }
    __typename
  }
  image {
    href
    verticalImageHref
    alt
    __typename
  }
  showExploreCollectionCTA
  __typename
}
fragment pdpMandatoryVariantFields on Variant {
  id
  masterId
  variantId
  name
  header
  subHeader
  price
  colorValue
  colorName
  ean
  preview
  images {
    alt
    href
    verticalImageHref
    __typename
  }
  __typename
}"""
        
        # 尺码专用GraphQL查询（基于完整curl请求）
        self.size_query = """query LazyPDP($id: ID!) {
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
}"""

    def extract_product_id_from_url(self, url: str) -> str:
        """从URL中提取产品ID"""
        match = re.search(r'/(\d+)(?:\?|$)', url)
        if match:
            return match.group(1)
        return ""
        
    def get_size_info(self, product_id: str, url: str = "") -> Optional[Dict]:
        """获取尺码信息的专用方法"""
        print(f"👉 获取尺码信息...")
        print(f"🆔 产品ID: {product_id}")
        
        # 为尺码查询创建专用头部
        size_headers = self.headers.copy()
        size_headers['x-operation-name'] = 'LazyPDP'
        
        if url:
            size_headers['referer'] = url
            
        payload = {
            "operationName": "LazyPDP",
            "query": self.size_query,
            "variables": {"id": product_id}
        }
        
        try:
            print(f"📡 发送尺码GraphQL请求...")
            response = self.session.post(
                self.graphql_url,
                headers=size_headers,
                json=payload,
                timeout=30
            )
            
            print(f"📊 尺码响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if 'errors' in data:
                    print(f"❌ 尺码GraphQL错误: {data['errors']}")
                    return None
                
                if 'data' in data and data['data'] and data['data'].get('product'):
                    print(f"✅ 成功获取尺码数据")
                    return self.parse_size_data(data['data']['product'])
                else:
                    print(f"❌ 尺码响应中无产品数据")
                    return None
            else:
                print(f"❌ 尺码API请求失败: {response.status_code}")
                print(f"   响应内容: {response.text[:500]}")
                return None
                
        except Exception as e:
            print(f"❌ 尺码请求异常: {e}")
            return None
            
    def parse_size_data(self, size_data: Dict) -> Dict:
        """解析尺码数据和商品详细信息"""
        size_info = {
            'size_groups': [],
            'all_sizes': [],
            'available_sizes': [],
            'unavailable_sizes': [],
            'product_measurements': None,
            'product_story': None,
            'material_composition_from_story': [],
            'care_instructions': [],
            'product_keywords': []
        }
        
        # 解析尺码组
        variations = size_data.get('variations', [])
        for variation in variations:
            # 处理尺码组
            size_groups = variation.get('sizeGroups', [])
            for group in size_groups:
                group_info = {
                    'label': group.get('label', ''),
                    'description': group.get('description', ''),
                    'sizes': []
                }
                
                sizes = group.get('sizes', [])
                for size in sizes:
                    size_item = {
                        'id': size.get('id', ''),
                        'label': size.get('label', ''),
                        'value': size.get('value', ''),
                        'productId': size.get('productId', ''),
                        'orderable': size.get('orderable', False),
                        'maxOrderableQuantity': size.get('maxOrderableQuantity', 0)
                    }
                    
                    group_info['sizes'].append(size_item)
                    
                    # 添加到全部尺码列表
                    if size_item['label'] not in size_info['all_sizes']:
                        size_info['all_sizes'].append(size_item['label'])
                    
                    # 按可用性分类
                    if size_item['orderable']:
                        if size_item['label'] not in size_info['available_sizes']:
                            size_info['available_sizes'].append(size_item['label'])
                    else:
                        if size_item['label'] not in size_info['unavailable_sizes']:
                            size_info['unavailable_sizes'].append(size_item['label'])
                
                size_info['size_groups'].append(group_info)
            
            # 处理productStory信息（新增）
            product_story = variation.get('productStory', {})
            if product_story:
                size_info['product_story'] = {
                    'longDescription': product_story.get('longDescription', ''),
                    'productKeywords': product_story.get('productKeywords', []),
                    'careInstructions': product_story.get('careInstructions', [])
                }
                
                # 材料组成（从 productStory 获取）
                material_comp = product_story.get('materialComposition', [])
                if material_comp:
                    size_info['material_composition_from_story'] = material_comp
                
                # 关键词
                keywords = product_story.get('productKeywords', [])
                if keywords:
                    size_info['product_keywords'] = keywords
                
                # 护理说明
                care_instructions = product_story.get('careInstructions', [])
                if care_instructions:
                    size_info['care_instructions'] = care_instructions
                
                # 制造商信息（从 productStory 获取）
                manufacturer_info = product_story.get('manufacturerInfo', {})
                if manufacturer_info:
                    size_info['manufacturer_info_from_story'] = manufacturer_info
        
        # 解析产品测量数据
        measurements = size_data.get('productMeasurements')
        if measurements:
            size_info['product_measurements'] = measurements
            
        return size_info

    def get_product_info(self, product_id: str, url: str = "") -> Optional[CompleteProductInfo]:
        """获取完整的商品信息（包括尺码）"""
        print(f"🚀 使用完整GraphQL API获取商品信息...")
        print(f"🆔 产品ID: {product_id}")
        
        # 更新referer
        if url:
            self.headers['referer'] = url
        
        # 首先获取基本产品信息
        payload = {
            "operationName": "PDP",
            "query": self.graphql_query,
            "variables": {"id": product_id}
        }
        
        try:
            print(f"📡 发送完整GraphQL请求...")
            response = self.session.post(
                self.graphql_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            print(f"📊 响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if 'errors' in data:
                    print(f"❌ GraphQL错误: {data['errors']}")
                    return None
                
                if 'data' in data and data['data'] and data['data'].get('product'):
                    print(f"✅ 成功获取完整商品数据")
                    product_info = self.parse_product_data(data['data']['product'], url)
                    
                    # 获取尺码信息
                    print(f"👉 现在获取详细尺码信息...")
                    size_info = self.get_size_info(product_id, url)
                    if size_info:
                        product_info.sizes = size_info
                        print(f"✅ 成功集成尺码信息")
                        print(f"   全部尺码: {len(size_info.get('all_sizes', []))}个")
                        print(f"   可用尺码: {len(size_info.get('available_sizes', []))}个")
                        print(f"   尺码组: {len(size_info.get('size_groups', []))}个")
                    else:
                        print(f"⚠️ 无法获取尺码信息，但基本信息已获取")
                    
                    return product_info
                else:
                    print(f"❌ 响应中无产品数据")
                    return None
            else:
                print(f"❌ API请求失败: {response.status_code}")
                print(f"   响应内容: {response.text[:500]}")
                return None
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return None



    def parse_product_data(self, product_data: Dict, url: str) -> CompleteProductInfo:
        """解析完整的产品数据"""
        product_info = CompleteProductInfo()
        product_info.scraped_at = datetime.now().isoformat()
        product_info.method = "complete_graphql_api"
        product_info.url = url
        
        # 基本信息
        product_info.product_id = product_data.get('id', '')
        product_info.name = product_data.get('name', '')
        product_info.header = product_data.get('header', '')
        product_info.sub_header = product_data.get('subHeader', '')
        product_info.description = product_data.get('description', '')
        product_info.brand = product_data.get('brand', 'PUMA')
        product_info.product_division = product_data.get('productDivision', '')
        product_info.size_chart_id = product_data.get('sizeChartId', '')
        product_info.orderable = product_data.get('orderable', False)
        
        # 评价信息
        product_info.average_rating = str(product_data.get('averageRating', ''))
        product_info.amount_of_reviews = str(product_data.get('amountOfReviews', ''))
        
        # 库存显示信息
        display_out_of_stock = product_data.get('displayOutOfStock', {})
        if display_out_of_stock:
            product_info.display_out_of_stock = display_out_of_stock
        
        # 主图片
        main_image = product_data.get('image', {})
        if main_image and main_image.get('href'):
            product_info.images = [main_image['href']]
        else:
            product_info.images = []
        
        # 促销信息
        promotions = product_data.get('promotions', [])
        if promotions:
            product_info.promotions = promotions
        
        # 处理变体信息（variations）
        variations = product_data.get('variations', [])
        if variations:
            # 使用第一个变体的信息作为主要信息
            main_variation = variations[0]
            
            # 价格信息
            product_info.price = str(main_variation.get('price', ''))
            product_info.sale_price = str(main_variation.get('salePrice', ''))
            
            # 产品价格对象
            product_price = main_variation.get('productPrice', {})
            if product_price:
                # 最优价格处理
                best_price = product_price.get('bestPrice', '')
                if best_price:
                    product_info.best_price = str(best_price)
                
                # 促销价格处理
                promotion_price = product_price.get('promotionPrice', '')
                if promotion_price:
                    product_info.promotion_price = str(promotion_price)
                    
                # 如果没有销售价格，使用产品价格对象中的
                if not product_info.sale_price:
                    sale_price = product_price.get('salePrice', '')
                    if sale_price:
                        product_info.sale_price = str(sale_price)
            
            # 颜色信息
            product_info.color_name = main_variation.get('colorName', '')
            product_info.color_value = main_variation.get('colorValue', '')
            
            # 其他变体信息
            product_info.style_number = main_variation.get('styleNumber', '')
            product_info.ean = main_variation.get('ean', '')
            product_info.is_final_sale = main_variation.get('isFinalSale', False)
            
            # 材料组成
            material_comp = main_variation.get('materialComposition', [])
            if material_comp:
                product_info.material_composition = material_comp
            
            # 制造商信息
            manufacturer_info = main_variation.get('manufacturerInfo', {})
            if manufacturer_info:
                product_info.manufacturer_info = manufacturer_info
            
            # 变体图片
            variant_images = main_variation.get('images', [])
            if variant_images:
                for img in variant_images:
                    if img.get('href') and img['href'] not in product_info.images:
                        product_info.images.append(img['href'])
            
            # 徽章信息
            badges = main_variation.get('badges', [])
            if badges:
                product_info.badges = badges
            
            # 变体库存信息
            variant_stock = main_variation.get('displayOutOfStock', {})
            if variant_stock:
                product_info.display_out_of_stock = variant_stock
        
        return product_info

    def scrape_product_from_url(self, url: str) -> Optional[CompleteProductInfo]:
        """从URL获取商品信息"""
        product_id = self.extract_product_id_from_url(url)
        if not product_id:
            print(f"❌ 无法从URL提取产品ID: {url}")
            return None
        
        return self.get_product_info(product_id, url)

def print_complete_product_info(product: CompleteProductInfo):
    """打印完整的商品信息"""
    if not product:
        print("❌ 没有获取到商品信息")
        return
    
    print("\n" + "="*80)
    print("🚀 完整GraphQL API 商品信息")
    print("="*80)
    
    # 基本信息
    print(f"🆔 商品ID: {product.product_id}")
    print(f"📦 商品名称: {product.name}")
    if product.header:
        print(f"📋 标题: {product.header}")
    if product.sub_header:
        print(f"📝 副标题: {product.sub_header}")
    print(f"🏷️  品牌: {product.brand}")
    
    # 价格信息
    if product.best_price:
        print(f"💰 最优价格: ${product.best_price}")
    if product.price:
        print(f"💵 基础价格: ${product.price}")
    if product.sale_price:
        print(f"🏷️  销售价格: ${product.sale_price}")
    if product.promotion_price:
        print(f"🎯 促销价格: ${product.promotion_price}")
    
    # 颜色和款式
    if product.color_name:
        print(f"🎨 颜色名称: {product.color_name}")
    if product.color_value:
        print(f"🎨 颜色值: {product.color_value}")
    if product.style_number:
        print(f"🔢 款式编号: {product.style_number}")
    
    # 订购状态
    print(f"🛒 可订购: {'是' if product.orderable else '否'}")
    if product.is_final_sale:
        print(f"⚠️  最终销售（不可退货）")
    
    # 库存状态
    if product.display_out_of_stock:
        stock_info = product.display_out_of_stock
        if stock_info.get('soldout'):
            print(f"📦 库存状态: 已售罄")
        elif stock_info.get('comingsoon'):
            print(f"📦 库存状态: 即将到货")
        elif stock_info.get('backsoon'):
            print(f"📦 库存状态: 即将补货")
        elif stock_info.get('presale'):
            print(f"📦 库存状态: 预售")
    
    # 评价信息
    if product.average_rating:
        print(f"⭐ 平均评分: {product.average_rating}")
    if product.amount_of_reviews:
        print(f"💬 评论数量: {product.amount_of_reviews}")
    
    # 图片信息
    print(f"🖼️  商品图片: {len(product.images)}张")
    
    # 尺码信息（新增和增强）
    if product.sizes:
        print(f"\n👠 详细尺码信息:")
        size_data = product.sizes
        
        if size_data.get('all_sizes'):
            print(f"   📊 全部尺码 ({len(size_data['all_sizes'])}个): {', '.join(size_data['all_sizes'])}")
        
        if size_data.get('available_sizes'):
            print(f"   ✅ 可用尺码 ({len(size_data['available_sizes'])}个): {', '.join(size_data['available_sizes'])}")
        
        if size_data.get('unavailable_sizes'):
            print(f"   ❌ 不可用尺码 ({len(size_data['unavailable_sizes'])}个): {', '.join(size_data['unavailable_sizes'])}")
        
        # 显示尺码组详情
        if size_data.get('size_groups'):
            print(f"   📎 尺码组详情:")
            for i, group in enumerate(size_data['size_groups'][:3], 1):  # 只显示前3个组
                print(f"      {i}. {group.get('label', 'N/A')} - {len(group.get('sizes', []))}个尺码")
                if group.get('description'):
                    print(f"         描述: {group['description']}")
                    
                # 显示每个尺码的详细状态
                sizes_in_group = group.get('sizes', [])
                if sizes_in_group:
                    available_in_group = [s for s in sizes_in_group if s.get('orderable', False)]
                    unavailable_in_group = [s for s in sizes_in_group if not s.get('orderable', False)]
                    
                    if available_in_group:
                        available_labels = [s.get('label', 'N/A') for s in available_in_group]
                        print(f"         ✅ 可用: {', '.join(available_labels)}")
                    
                    if unavailable_in_group:
                        unavailable_labels = [s.get('label', 'N/A') for s in unavailable_in_group]
                        print(f"         ❌ 缺货: {', '.join(unavailable_labels)}")
                        
            if len(size_data['size_groups']) > 3:
                print(f"      ... 还有{len(size_data['size_groups']) - 3}个尺码组")
        
        # 显示从productStory获取的额外信息
        if size_data.get('material_composition_from_story'):
            print(f"   🧵 详细材料组成 ({len(size_data['material_composition_from_story'])}项):")
            for material in size_data['material_composition_from_story'][:5]:
                print(f"      • {material}")
            if len(size_data['material_composition_from_story']) > 5:
                print(f"      ... 还有{len(size_data['material_composition_from_story']) - 5}项")
        
        if size_data.get('care_instructions'):
            print(f"   🧽 护理说明 ({len(size_data['care_instructions'])}项):")
            for instruction in size_data['care_instructions'][:3]:
                print(f"      • {instruction}")
            if len(size_data['care_instructions']) > 3:
                print(f"      ... 还有{len(size_data['care_instructions']) - 3}项")
        
        if size_data.get('product_keywords'):
            print(f"   🔍 产品关键词: {', '.join(size_data['product_keywords'][:10])}")
            if len(size_data['product_keywords']) > 10:
                print(f"      ... 还有{len(size_data['product_keywords']) - 10}个关键词")
                
        # 产品测量数据
        if size_data.get('product_measurements'):
            measurements = size_data['product_measurements']
            print(f"   📏 产品测量数据:")
            if measurements.get('metric'):
                print(f"      公制: {measurements['metric']}")
            if measurements.get('imperial'):
                print(f"      英制: {measurements['imperial']}")
    
    # 材料组成
    if product.material_composition:
        print(f"\n🧵 材料组成:")
        for material in product.material_composition:
            print(f"   • {material}")
    
    # 制造商信息
    if product.manufacturer_info:
        print(f"\n🏭 制造商信息:")
        if 'countryOfOrigin' in product.manufacturer_info and product.manufacturer_info['countryOfOrigin']:
            origin = product.manufacturer_info['countryOfOrigin']
            if isinstance(origin, dict) and origin.get('content'):
                print(f"   原产地: {origin.get('content', '')}")
        if 'manufacturerAddress' in product.manufacturer_info and product.manufacturer_info['manufacturerAddress']:
            address = product.manufacturer_info['manufacturerAddress']
            if isinstance(address, dict) and address.get('content'):
                print(f"   制造商地址: {address.get('content', '')}")
    
    # 促销信息
    if product.promotions:
        print(f"\n🎯 促销信息:")
        for promo in product.promotions:
            print(f"   • {promo.get('calloutMessage', '')}")
    
    # 徽章信息
    if product.badges:
        print(f"\n🏆 商品徽章:")
        for badge in product.badges:
            print(f"   • {badge.get('label', '')}")
    
    # 商品描述
    if product.description:
        desc_preview = product.description[:300] + "..." if len(product.description) > 300 else product.description
        print(f"\n📝 商品描述: {desc_preview}")
    
    # 其他信息
    if product.product_division:
        print(f"\n📂 产品分类: {product.product_division}")
    if product.size_chart_id:
        print(f"📏 尺码表ID: {product.size_chart_id}")
    if product.ean:
        print(f"🔍 EAN码: {product.ean}")
    
    # 元数据
    print(f"\n🔧 获取方法: {product.method}")
    print(f"⏰ 获取时间: {product.scraped_at}")
    print("="*80)

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='完整GraphQL API商品信息获取')
    parser.add_argument('--url', '-u', required=True, help='商品页面URL')
    parser.add_argument('--output', '-o', help='输出JSON文件名')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    # 创建API客户端
    api_client = CompleteGraphQLAPI()
    
    # 获取商品信息
    product_info = api_client.scrape_product_from_url(args.url)
    
    if product_info:
        # 显示结果
        print_complete_product_info(product_info)
        
        # 保存到文件
        if args.output:
            output_path = get_output_path(args.output)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(product_info), f, ensure_ascii=False, indent=2)
            print(f"\n✅ 数据已保存到: {output_path}")
        else:
            # 询问是否保存
            response = input("\n💾 是否保存数据到JSON文件? (y/N): ")
            if response.lower() == 'y':
                filename = f"complete_product_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                output_path = get_output_path(filename)
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(asdict(product_info), f, ensure_ascii=False, indent=2)
                print(f"✅ 数据已保存到: {output_path}")
    else:
        print("❌ 获取商品信息失败")

if __name__ == "__main__":
    main()