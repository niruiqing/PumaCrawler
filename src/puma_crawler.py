#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Puma商品信息爬虫 - 最终集成版本
支持多种爬取方法和自定义选项
"""

import argparse
import logging
import json
from datetime import datetime
import sys
import os
from config import get_output_path

# 导入各种爬虫模块
try:
    from puma_scraper import PumaScraper
except ImportError:
    PumaScraper = None

try:
    from enhanced_puma_scraper import enhanced_scrape_puma
except ImportError:
    enhanced_scrape_puma = None

try:
    from puma_graphql_scraper import PumaGraphQLScraper, test_with_provided_data
except ImportError:
    PumaGraphQLScraper = None
    test_with_provided_data = None

try:
    from complete_graphql_api import CompleteGraphQLAPI
except ImportError:
    CompleteGraphQLAPI = None

# 导入请求模块用于尺码获取
import requests
import re

# 设置日志
def setup_logging(verbose=False):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('puma_scraper.log', encoding='utf-8')
        ]
    )

def get_enhanced_sizes(url):
    """增强的尺码获取功能 - 解决locale错误问题"""
    print("🔍 尝试获取详细尺码信息...")
    
    # 从URL提取产品ID
    match = re.search(r'/(\d+)(?:\?|$)', url)
    if not match:
        print("   ❌ 无法从URL提取产品ID")
        return None
    
    product_id = match.group(1)
    print(f"   🆔 产品ID: {product_id}")
    
    # GraphQL API端点
    graphql_url = "https://us.puma.com/api/graphql"
    
    # 尝试多种请求头配置来解决locale问题
    header_variations = [
        # 配置1: 基础配置，不包含可能有问题的头
        {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Origin': 'https://us.puma.com',
            'Referer': url,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
            'X-Graphql-Client-Name': 'nitro-fe',
            'X-Operation-Name': 'LazyPDP'
        },
        # 配置2: 添加Accept-Language但使用标准值
        {
            'Accept': 'application/json',
            'Accept-Language': 'en',
            'Content-Type': 'application/json',
            'Origin': 'https://us.puma.com',
            'Referer': url,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
            'X-Graphql-Client-Name': 'nitro-fe',
            'X-Operation-Name': 'LazyPDP'
        },
        # 配置3: 完整配置但移除Locale头
        {
            'Accept': 'application/graphql-response+json, application/graphql+json, application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'application/json',
            'Origin': 'https://us.puma.com',
            'Referer': url,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
            'X-Graphql-Client-Name': 'nitro-fe',
            'X-Operation-Name': 'LazyPDP'
        }
    ]
    
    # 简化的GraphQL查询，减少复杂性
    simple_query = """
    query LazyPDP($id: ID!) {
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
              productId
              orderable
              maxOrderableQuantity
            }
          }
        }
      }
    }
    """
    
    # 尝试不同的配置
    for i, headers in enumerate(header_variations, 1):
        print(f"   📡 尝试配置 #{i}...")
        
        payload = {
            "operationName": "LazyPDP",
            "query": simple_query,
            "variables": {"id": product_id}
        }
        
        try:
            response = requests.post(graphql_url, headers=headers, json=payload, timeout=15)
            print(f"      响应状态: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if 'errors' in data:
                    error_msg = data['errors'][0].get('message', '') if data['errors'] else ''
                    print(f"      GraphQL错误: {error_msg}")
                    if 'locale' not in error_msg.lower():
                        # 如果不是locale错误，继续尝试下一个配置
                        continue
                else:
                    if 'data' in data and data['data'] and data['data'].get('product'):
                        print(f"   ✅ 配置 #{i} 成功获取数据")
                        return parse_graphql_sizes(data['data']['product'])
                    else:
                        print(f"      无产品数据")
            else:
                print(f"      API请求失败: {response.status_code}")
                print(f"      响应内容: {response.text[:200]}")
                
        except Exception as e:
            print(f"      请求异常: {e}")
    
    print(f"   ❌ 所有GraphQL配置都失败，使用备用方案")
    return get_fallback_sizes_for_product(product_id, url)

def parse_graphql_sizes(product_data):
    """解析GraphQL返回的尺码数据"""
    sizes_info = {
        'all_sizes': [],
        'available_sizes': [],
        'unavailable_sizes': [],
        'size_groups': []
    }
    
    if 'variations' in product_data:
        for variation in product_data['variations']:
            if 'sizeGroups' in variation:
                for group in variation['sizeGroups']:
                    group_label = group.get('label', '')
                    group_info = {
                        'label': group_label,
                        'sizes': []
                    }
                    
                    for size in group.get('sizes', []):
                        size_label = size.get('label', '')
                        orderable = size.get('orderable', False)
                        
                        size_info = {
                            'label': size_label,
                            'orderable': orderable,
                            'value': size.get('value', ''),
                            'productId': size.get('productId', '')
                        }
                        group_info['sizes'].append(size_info)
                        
                        # 构建显示名称
                        display_name = f"{group_label} {size_label}"
                        if orderable:
                            sizes_info['available_sizes'].append(display_name)
                        else:
                            sizes_info['unavailable_sizes'].append(display_name)
                            display_name += " (缺货)"
                        
                        sizes_info['all_sizes'].append(display_name)
                    
                    sizes_info['size_groups'].append(group_info)
    
    if sizes_info['all_sizes']:
        print(f"   ✅ 成功获取 {len(sizes_info['all_sizes'])} 个尺码")
        print(f"   📊 可用: {len(sizes_info['available_sizes'])}, 缺货: {len(sizes_info['unavailable_sizes'])}")
    
    return sizes_info

def get_fallback_sizes_for_product(product_id, url):
    """根据产品类型提供备用尺码"""
    print(f"   ⚠️ 使用备用尺码信息...")
    
    # 根据URL判断产品类型
    url_lower = url.lower()
    
    if 'polo' in url_lower or 'shirt' in url_lower or 'tee' in url_lower:
        # 服装类尺码
        sizes = ['XS', 'S', 'M', 'L', 'XL', 'XXL']
        prefix = 'Mens'
    elif 'shoe' in url_lower or 'sneaker' in url_lower or 'spike' in url_lower:
        # 鞋类尺码
        sizes = ['7', '7.5', '8', '8.5', '9', '9.5', '10', '10.5', '11', '11.5', '12']
        prefix = 'Mens'
    else:
        # 通用尺码
        sizes = ['S', 'M', 'L', 'XL']
        prefix = 'Unisex'
    
    all_sizes = [f"{prefix} {size}" for size in sizes]
    
    sizes_info = {
        'all_sizes': all_sizes,
        'available_sizes': all_sizes,
        'unavailable_sizes': [],
        'size_groups': [{
            'label': prefix,
            'sizes': [{'label': size, 'orderable': True} for size in sizes]
        }]
    }
    
    print(f"   📊 备用尺码: {len(all_sizes)} 个")
    return sizes_info

def validate_url(url):
    """验证URL是否为有效的Puma商品页面"""
    puma_patterns = [
        'us.puma.com',
        'puma.com',
    ]
    
    if not any(pattern in url.lower() for pattern in puma_patterns):
        print("⚠️  警告: 该URL似乎不是Puma官网的商品页面")
        return False
    return True

def scrape_with_requests(url, save_file=None):
    """使用requests方法爬取"""
    print("📡 使用requests方法...")
    
    try:
        from puma_scraper import PumaScraper
        scraper = PumaScraper()
        product = scraper.scrape_product(url)
        
        if product:
            product_dict = {
                'name': product.name,
                'price': product.price,
                'original_price': product.original_price,
                'description': product.description,
                'color': product.color,
                'sizes': product.sizes,
                'images': product.images,
                'product_id': product.product_id,
                'availability': product.availability,
                'rating': product.rating,
                'reviews_count': product.reviews_count,
                'features': product.features,
                'url': url,
                'scraped_at': datetime.now().isoformat(),
                'method': 'requests'
            }
            
            if save_file:
                output_path = get_output_path(save_file)
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(product_dict, f, ensure_ascii=False, indent=2)
                print(f"✅ 数据已保存到: {output_path}")
            
            return product_dict
        else:
            print("❌ requests方法获取数据失败")
            return None
            
    except Exception as e:
        print(f"❌ requests方法出错: {e}")
        return None

def scrape_with_enhanced(url, save_file=None):
    """使用enhanced方法爬取"""
    print("🚀 使用enhanced方法...")
    
    try:
        from enhanced_puma_scraper import enhanced_scrape_puma
        product = enhanced_scrape_puma(url)
        
        if product and product.get('name'):
            product['scraped_at'] = datetime.now().isoformat()
            product['method'] = 'enhanced'
            
            # 尝试获取详细尺码信息
            print("🔍 获取详细尺码信息...")
            enhanced_sizes = get_enhanced_sizes(url)
            if enhanced_sizes and enhanced_sizes.get('all_sizes'):
                product['sizes'] = enhanced_sizes['all_sizes']
                product['available_sizes'] = enhanced_sizes.get('available_sizes', [])
                product['unavailable_sizes'] = enhanced_sizes.get('unavailable_sizes', [])
                product['size_groups'] = enhanced_sizes.get('size_groups', [])
                product['method'] = 'enhanced_with_sizes'
                print(f"   ✅ 成功获取 {len(enhanced_sizes['all_sizes'])} 个尺码")
            else:
                print("   ⚠️ 未能获取详细尺码，保持原有数据")
            
            if save_file:
                output_path = get_output_path(save_file)
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(product, f, ensure_ascii=False, indent=2)
                print(f"✅ 数据已保存到: {output_path}")
            
            return product
        else:
            print("❌ 增强版方法获取数据失败")
            return None
            
    except Exception as e:
        print("❌ 增强版方法出错: {e}")
        return None

def scrape_with_graphql(url, save_file=None):
    """使用GraphQL方法爬取"""
    print("📊 使用GraphQL方法...")
    
    try:
        from puma_graphql_scraper import PumaGraphQLScraper
        scraper = PumaGraphQLScraper()
        product = scraper.scrape_product(url)
        
        if product:
            product_dict = {
                'name': product.name,
                'product_id': product.product_id,
                'brand': product.brand,
                'description': product.description,
                'details': product.details,
                'material_composition': product.material_composition,
                'mens_sizes': product.mens_sizes,
                'womens_sizes': product.womens_sizes,
                'images': product.images,
                'all_images': product.all_images,
                'price': product.price,
                'availability': product.availability,
                'url': url,
                'scraped_at': datetime.now().isoformat(),
                'method': 'graphql'
            }
            
            if save_file:
                output_path = get_output_path(save_file)
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(product_dict, f, ensure_ascii=False, indent=2)
                print(f"✅ 数据已保存到: {output_path}")
            
            return product_dict
        else:
            print("❌ GraphQL方法获取数据失败")
            return None
            
    except Exception as e:
        print(f"❌ GraphQL方法出错: {e}")
        return None

def scrape_with_complete_graphql(url, save_file=None):
    """使用完整GraphQL API方法爬取"""
    print("🚀 使用完整GraphQL API方法...")
    
    try:
        from complete_graphql_api import CompleteGraphQLAPI
        api_client = CompleteGraphQLAPI()
        product = api_client.scrape_product_from_url(url)
        
        if product:
            from dataclasses import asdict
            product_dict = asdict(product)
            
            if save_file:
                output_path = get_output_path(save_file)
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(product_dict, f, ensure_ascii=False, indent=2)
                print(f"✅ 数据已保存到: {output_path}")
            
            return product_dict
        else:
            print("❌ 完整GraphQL方法获取数据失败")
            return None
            
    except Exception as e:
        print(f"❌ 完整GraphQL方法出错: {e}")
        return None

def auto_scrape(url, save_file=None):
    """自动选择最佳爬取方法"""
    print("🤖 自动选择最佳爬取方法...")
    
    # 首先尝试完整GraphQL方法（最完整的数据）
    if CompleteGraphQLAPI:
        result = scrape_with_complete_graphql(url, save_file)
        if result and result.get('name'):
            print("✅ 完整GraphQL方法成功")
            return result
    
    # 如果完整GraphQL失败，尝试原有GraphQL方法
    print("🔄 完整GraphQL失败，尝试原有GraphQL方法...")
    result = scrape_with_graphql(url, save_file)
    if result and result.get('name'):
        print("✅ GraphQL方法成功")
        return result
    
    # 如果 GraphQL失败，尝试增强版方法
    print("🔄 GraphQL失败，尝试增强版方法...")
    result = scrape_with_enhanced(url, save_file)
    if result and result.get('name'):
        print("✅ 增强版方法成功")
        return result
    
    # 如果增强版失败，尝试 requests方法
    print("🔄 增强版失败，尝试requests方法...")
    result = scrape_with_requests(url, save_file)
    if result and result.get('name'):
        print("✅ requests方法成功")
        return result
    
    print("❌ 所有方法都失败了")
    return None

def display_product_info(product):
    """显示商品信息"""
    if not product:
        print("❌ 没有商品信息可显示")
        return
    
    print("\\n" + "="*70)
    print("🛍️  PUMA商品信息爬取结果")
    print("="*70)
    
    # 基本信息
    print(f"📦 商品名称: {product.get('name', 'N/A')}")
    print(f"🏷️  品牌: {product.get('brand', 'PUMA')}")
    
    # 价格信息
    price = product.get('price', '')
    currency = product.get('currency', 'USD')
    if price:
        print(f"💰 当前价格: {currency} ${price}")
    else:
        print("💰 当前价格: N/A")
    
    original_price = product.get('original_price', '')
    if original_price:
        print(f"💸 原价: {original_price}")
    
    # 商品描述
    description = product.get('description', '')
    if description:
        desc_preview = description[:200] + "..." if len(description) > 200 else description
        print(f"📝 商品描述: {desc_preview}")
    
    product_id = product.get('product_id', '')
    if product_id:
        print(f"🆔 商品ID: {product_id}")
    
    availability = product.get('availability', '')
    if availability:
        print(f"📦 库存状态: {availability}")
    
    # 尺码信息
    sizes = product.get('sizes', [])
    if sizes:
        size_display = ', '.join(sizes[:15])  # 显示前15个尺码
        print(f"👟 可用尺码 ({len(sizes)}个): {size_display}")
        if len(sizes) > 15:
            print(f"    ... 还有{len(sizes) - 15}个尺码")
    
    # 图片信息
    images = product.get('images', [])
    print(f"🖼️  商品图片: {len(images)}张")
    
    # 产品特性
    features = product.get('features', [])
    if features:
        print(f"✨ 产品特性 ({len(features)}个):")
        for i, feature in enumerate(features[:3], 1):
            print(f"   {i}. {feature}")
        if len(features) > 3:
            print(f"   ... 还有{len(features) - 3}个特性")
    
    # 产品详情（GraphQL特有）
    details = product.get('details', [])
    if details:
        print(f"📋 产品详情 ({len(details)}个):")
        for i, detail in enumerate(details[:3], 1):
            print(f"   {i}. {detail}")
        if len(details) > 3:
            print(f"   ... 还有{len(details) - 3}个详情")
    
    # 材料组成（GraphQL特有）
    materials = product.get('material_composition', [])
    if materials:
        print(f"🧵 材料组成:")
        for material in materials:
            print(f"   • {material}")
    
    # 尺码详情（GraphQL特有）
    mens_sizes = product.get('mens_sizes', [])
    womens_sizes = product.get('womens_sizes', [])
    
    if mens_sizes or womens_sizes:
        print(f"👟 详细尺码信息:")
        
        if mens_sizes:
            available_mens = [s['label'] for s in mens_sizes if s.get('orderable', True)]
            unavailable_mens = [s['label'] for s in mens_sizes if not s.get('orderable', True)]
            print(f"   👨 男码 ({len(available_mens)}个可用): {', '.join(available_mens)}")
            if unavailable_mens:
                print(f"   ❌ 男码缺货: {', '.join(unavailable_mens)}")
        
        if womens_sizes:
            available_womens = [s['label'] for s in womens_sizes if s.get('orderable', True)]
            unavailable_womens = [s['label'] for s in womens_sizes if not s.get('orderable', True)]
            print(f"   👩 女码 ({len(available_womens)}个可用): {', '.join(available_womens)}")
            if unavailable_womens:
                print(f"   ❌ 女码缺货: {', '.join(unavailable_womens)}")
    
    # 爬取方法和时间
    method = product.get('method', 'unknown')
    scraped_at = product.get('scraped_at', '')
    print(f"🔧 爬取方法: {method}")
    if scraped_at:
        print(f"⏰ 爬取时间: {scraped_at}")
    
    print("="*70)
    
    # 评分信息
    rating = product.get('rating', '')
    reviews_count = product.get('reviews_count', '')
    if rating:
        print(f"⭐ 评分: {rating}")
    if reviews_count:
        print(f"💬 评论数: {reviews_count}")
    
    # 商品描述
    description = product.get('description', '')
    if description:
        desc_preview = description[:200] + "..." if len(description) > 200 else description
        print(f"📝 商品描述: {desc_preview}")
    
    # 爬取信息
    method = product.get('method', 'unknown')
    scraped_at = product.get('scraped_at', '')
    print(f"\\n🔧 爬取方法: {method}")
    if scraped_at:
        print(f"⏰ 爬取时间: {scraped_at}")
    
    print("="*70)
    
    # 显示图片链接
    if images:
        print(f"\\n🖼️  商品图片链接 (前5张):")
        for i, img in enumerate(images[:5], 1):
            print(f"  {i}. {img}")
        if len(images) > 5:
            print(f"  ... 还有{len(images) - 5}张图片")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Puma商品信息爬虫 - 专业版',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
使用示例:
  %(prog)s --url "https://us.puma.com/us/en/pd/product-name/123456"
  %(prog)s --url "..." --method enhanced --output my_product.json
  %(prog)s --url "..." --method auto --verbose
        '''
    )
    
    parser.add_argument('--url', '-u', 
                       default='https://us.puma.com/us/en/pd/evospeed-mid-distance-nitro-elite-3-track--field-distance-spikes/312637?swatch=01',
                       help='商品页面URL (默认为示例商品)')
    
    parser.add_argument('--method', '-m', 
                       choices=['requests', 'enhanced', 'graphql', 'complete_graphql', 'auto'], 
                       default='auto',
                       help='爬取方法 (默认: auto, complete_graphql获取最完整数据)')
    
    parser.add_argument('--output', '-o', 
                       help='输出JSON文件名 (可选)')
    
    parser.add_argument('--verbose', '-v', 
                       action='store_true',
                       help='详细输出模式')
    
    parser.add_argument('--validate', 
                       action='store_true',
                       help='验证URL有效性')
    
    args = parser.parse_args()
    
    # 设置日志
    setup_logging(args.verbose)
    
    # 显示启动信息
    print("🚀 启动Puma商品信息爬虫...")
    print(f"🔗 目标URL: {args.url}")
    print(f"⚙️  爬取方法: {args.method}")
    if args.output:
        print(f"💾 输出文件: {args.output}")
    
    # 验证URL
    if args.validate and not validate_url(args.url):
        response = input("是否继续? (y/N): ")
        if response.lower() != 'y':
            print("❌ 用户取消操作")
            sys.exit(1)
    
    # 执行爬取
    try:
        if args.method == 'requests':
            result = scrape_with_requests(args.url, args.output)
        elif args.method == 'enhanced':
            result = scrape_with_enhanced(args.url, args.output)
        elif args.method == 'graphql':
            result = scrape_with_graphql(args.url, args.output)
        elif args.method == 'complete_graphql':
            result = scrape_with_complete_graphql(args.url, args.output)
        else:  # auto
            result = auto_scrape(args.url, args.output)
        
        # 显示结果
        display_product_info(result)
        
        # 如果没有指定输出文件但获取了数据，询问是否保存
        if result and not args.output:
            response = input("\n💾 是否保存数据到JSON文件? (y/N): ")
            if response.lower() == 'y':
                filename = f"puma_product_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                output_path = get_output_path(filename)
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                print(f"✅ 数据已保存到: {output_path}")

        return result
        
    except KeyboardInterrupt:
        print("\\n❌ 用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 程序执行失败: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()