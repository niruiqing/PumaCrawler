#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试尺码接口
"""

import requests
import json

def test_size_api():
    """测试尺码获取接口"""
    print("🚀 测试尺码接口...")
    
    graphql_url = 'https://us.puma.com/api/graphql'
    
    # 使用最新的认证信息
    headers = {
        'accept': 'application/graphql-response+json, application/graphql+json, application/json',
        'accept-language': 'zh-CN,zh;q=0.9',
        'authorization': 'Bearer eyJ2ZXIiOiIxLjAiLCJqa3UiOiJzbGFzL3Byb2QvYmNqcF9wcmQiLCJraWQiOiI2OGI4OWE0Mi02ZjAwLTQzYWUtYjRjNC1hZmRmMGUzZWFlNzQiLCJ0eXAiOiJqd3QiLCJjbHYiOiJKMi4zLjQiLCJhbGciOiJFUzI1NiJ9.eyJhdXQiOiJHVUlEIiwic2NwIjoic2ZjYy5zaG9wcGVyLW15YWNjb3VudC5iYXNrZXRzIHNmY2Muc2hvcHBlci1teWFjY291bnQuYWRkcmVzc2VzIHNmY2Muc2hvcHBlci1wcm9kdWN0cyBzZmNjLnNob3BwZXItbXlhY2NvdW50LnJ3IHNmY2Muc2hvcHBlci1teWFjY291bnQucGF5bWVudGluc3RydW1lbnRzIHNmY2Muc2hvcHBlci1jdXN0b21lcnMubG9naW4gc2ZjYy5zaG9wcGVyLWNvbnRleHQgc2ZjYy5zaG9wcGVyLWNvbnRleHQucncgc2ZjYy5zaG9wcGVyLW15YWNjb3VudC5vcmRlcnMgc2ZjYy5zaG9wcGVyLWN1c3RvbWVycy5yZWdpc3RlciBzZmNjLnNob3BwZXItYmFza2V0cy1vcmRlcnMgc2ZjYy5zaG9wcGVyLW15YWNjb3VudC5hZGRyZXNzZXMucncgc2ZjYy5zaG9wcGVyLW15YWNjb3VudC5wcm9kdWN0bGlzdHMucncgc2ZjYy5zaG9wcGVyLXByb2R1Y3RsaXN0cyBzZmNjLnNob3BwZXItcHJvbW90aW9ucyBzZmNjLnNob3BwZXItYmFza2V0cy1vcmRlcnMucncgc2ZjYy5zaG9wcGVyLW15YWNjb3VudC5wYXltZW50aW5zdHJ1bWVudHMucncgc2ZjYy5zaG9wcGVyLWdpZnQtY2VydGlmaWNhdGVzIHNmY2Muc2hvcHBlci1wcm9kdWN0LXNlYXJjaCBzZmNjLnNob3BwZXItbXlhY2NvdW50LnByb2R1Y3RsaXN0cyBzZmNjLnNob3BwZXItY2F0ZWdvcmllcyBzZmNjLnNob3BwZXItbXlhY2NvdW50Iiwic3ViIjoiY2Mtc2xhczo6YmNqcF9wcmQ6OnNjaWQ6MWM4YzhhM2UtNjU2ZS00MWIxLThiNmYtZmIwNmM0NTFmMDE5Ojp1c2lkOjU3Yjk3ZDc0LTIzZWEtNGIxZi05YzZkLTE4NTVlODI1Y2Q5NiIsImN0eCI6InNsYXMiLCJpc3MiOiJzbGFzL3Byb2QvYmNqcF9wcmQiLCJpc3QiOjEsImRudCI6IjAiLCJhdWQiOiJjb21tZXJjZWNsb3VkL3Byb2QvYmNqcF9wcmQiLCJuYmYiOjE3NTYwODg4ODUsInN0eSI6IlVzZXIiLCJpc2IiOiJ1aWRvOnNsYXM6OnVwbjpHdWVzdDo6dWlkbjpHdWVzdCBVc2VyOjpnY2lkOmFibHJCR21yQklsWG9Sa0hsSndxWVl3SGRLOjpjaGlkOk5BIiwiZXhwIjoxNzU2MDkwNzE1LCJpYXQiOjE3NTYwODg5MTUsImp0aSI6IkMyQy0xODQ0NjA0NzcwMDc0MDYzNDM3MzQ3NjM0MTY2MzA0NTcxMTcifQ.oXAFWFX2Thwrc0mJ0tuYq9E5sDtJHNojKeKYHgv8-Z5zVGkCePB03QjyFw-lE_6EiM4ZW7tE6fFOqOaXYcqqiA',
        'content-type': 'application/json',
        'customer-group': 'a078f6706670a82b26dee50e6d7d1dacb6d532351e60c225876bec5eb416cf4f',
        'customer-id': 'ablrBGmrBIlXoRkHlJwqYYwHdK',
        'locale': 'en-US',
        'origin': 'https://us.puma.com',
        'puma-request-source': 'web',
        'referer': 'https://us.puma.com/us/en/pd/suede-xl-leopard-jr-youth/404299?swatch=02',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
        'x-graphql-client-name': 'nitro-fe',
        'x-operation-name': 'LazyPDP'
    }
    
    # 使用完整的LazyPDP查询
    query = """query LazyPDP($id: ID!) {
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
    
    payload = {
        'operationName': 'LazyPDP',
        'query': query,
        'variables': {'id': '404299'}
    }
    
    try:
        print(f"📡 发送请求到: {graphql_url}")
        response = requests.post(graphql_url, headers=headers, json=payload, timeout=30)
        print(f"📊 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if 'errors' in data:
                print(f"❌ GraphQL错误: {data['errors']}")
            else:
                print("✅ 成功获取数据!")
                
                product = data['data']['product']
                print(f"🆔 产品ID: {product['id']}")
                
                # 显示尺码信息
                variations = product.get('variations', [])
                for i, variation in enumerate(variations):
                    print(f"\n📦 变体 {i+1}:")
                    
                    # 尺码组
                    size_groups = variation.get('sizeGroups', [])
                    if size_groups:
                        print(f"👠 找到 {len(size_groups)} 个尺码组:")
                        for group in size_groups:
                            group_label = group.get('label', '未知')
                            sizes = group.get('sizes', [])
                            print(f"  📏 {group_label} ({len(sizes)}个尺码):")
                            
                            available_count = 0
                            unavailable_count = 0
                            
                            for size in sizes:
                                orderable = size.get('orderable', False)
                                if orderable:
                                    available_count += 1
                                    print(f"    ✅ {size.get('label', 'N/A')} (可订购)")
                                else:
                                    unavailable_count += 1
                                    print(f"    ❌ {size.get('label', 'N/A')} (缺货)")
                            
                            print(f"  📊 总计: {available_count}个可用, {unavailable_count}个缺货")
                    else:
                        print("  ⚠️ 未找到尺码组信息")
                    
                    # 产品故事信息
                    product_story = variation.get('productStory', {})
                    if product_story:
                        print(f"📖 产品故事信息:")
                        
                        # 材料组成
                        material_comp = product_story.get('materialComposition', [])
                        if material_comp:
                            print(f"  🧵 材料组成 ({len(material_comp)}项):")
                            for material in material_comp[:3]:  # 只显示前3项
                                print(f"    • {material}")
                            if len(material_comp) > 3:
                                print(f"    ... 还有{len(material_comp) - 3}项")
                        
                        # 护理说明
                        care_instructions = product_story.get('careInstructions', [])
                        if care_instructions:
                            print(f"  🧽 护理说明 ({len(care_instructions)}项):")
                            for instruction in care_instructions[:2]:
                                print(f"    • {instruction}")
                        
                        # 制造商信息
                        manufacturer_info = product_story.get('manufacturerInfo', {})
                        if manufacturer_info:
                            print(f"  🏭 制造商信息:")
                            country_info = manufacturer_info.get('countryOfOrigin', {})
                            if country_info:
                                print(f"    原产地: {country_info.get('content', 'N/A')}")
                            
                            address_info = manufacturer_info.get('manufacturerAddress', {})
                            if address_info:
                                print(f"    制造商地址: {address_info.get('content', 'N/A')}")
                
                print(f"\n🎉 测试完成！成功获取详细尺码和产品信息。")
                
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"   响应内容: {response.text[:500]}")
            
    except Exception as e:
        print(f"❌ 异常: {e}")

if __name__ == "__main__":
    test_size_api()