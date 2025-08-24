#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Puma商品信息爬虫主程序
整合requests和Selenium两种方法
"""

import argparse
import logging
from puma_scraper import PumaScraper
from puma_scraper_selenium import PumaSeleniumScraper
import json
from dataclasses import asdict

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def scrape_puma_product(url: str, method: str = "auto") -> dict:
    """
    爬取Puma商品信息
    
    Args:
        url: 商品页面URL
        method: 爬取方法 ("requests", "selenium", "auto")
    
    Returns:
        商品信息字典
    """
    
    if method == "requests":
        logger.info("使用requests方法爬取")
        scraper = PumaScraper()
        product = scraper.scrape_product(url)
        
    elif method == "selenium":
        logger.info("使用Selenium方法爬取")
        scraper = PumaSeleniumScraper(headless=True)
        product = scraper.scrape_with_selenium(url)
        
    else:  # auto
        logger.info("自动选择最佳方法")
        
        # 首先尝试requests方法
        logger.info("首先尝试requests方法...")
        scraper = PumaScraper()
        product = scraper.scrape_product(url)
        
        # 如果requests方法失败或获取信息不完整，尝试Selenium
        if not product or not product.name:
            logger.info("requests方法失败，尝试Selenium方法...")
            selenium_scraper = PumaSeleniumScraper(headless=True)
            product = selenium_scraper.scrape_with_selenium(url)
    
    return asdict(product) if product else {}

def print_product_info(product_dict: dict):
    """打印商品信息"""
    if not product_dict or not product_dict.get('name'):
        print("❌ 未能获取到商品信息")
        return
    
    print("\n" + "="*60)
    print("🛍️  PUMA商品信息")
    print("="*60)
    
    print(f"📦 商品名称: {product_dict.get('name', 'N/A')}")
    print(f"💰 当前价格: {product_dict.get('price', 'N/A')}")
    
    if product_dict.get('original_price'):
        print(f"💸 原价: {product_dict.get('original_price')}")
    
    print(f"🎨 颜色: {product_dict.get('color', 'N/A')}")
    print(f"🏷️  商品ID: {product_dict.get('product_id', 'N/A')}")
    
    if product_dict.get('availability'):
        print(f"📦 库存状态: {product_dict.get('availability')}")
    
    if product_dict.get('rating'):
        print(f"⭐ 评分: {product_dict.get('rating')}")
    
    if product_dict.get('reviews_count'):
        print(f"💬 评论数: {product_dict.get('reviews_count')}")
    
    # 尺码信息
    sizes = product_dict.get('sizes', [])
    if sizes:
        print(f"👟 可用尺码: {', '.join(sizes)}")
    
    # 图片数量
    images = product_dict.get('images', [])
    print(f"🖼️  图片数量: {len(images)}张")
    
    # 产品特性
    features = product_dict.get('features', [])
    if features:
        print(f"✨ 产品特性: {len(features)}个")
        for i, feature in enumerate(features[:3], 1):
            print(f"   {i}. {feature}")
        if len(features) > 3:
            print(f"   ... 还有{len(features) - 3}个特性")
    
    # 商品描述
    description = product_dict.get('description', '')
    if description:
        desc_preview = description[:150] + "..." if len(description) > 150 else description
        print(f"📝 商品描述: {desc_preview}")
    
    print("="*60)

def save_product_info(product_dict: dict, filename: str = "puma_product.json"):
    """保存商品信息到文件"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(product_dict, f, ensure_ascii=False, indent=2)
        print(f"✅ 商品信息已保存到: {filename}")
    except Exception as e:
        print(f"❌ 保存文件失败: {e}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Puma商品信息爬虫')
    parser.add_argument('--url', '-u', 
                       default='https://us.puma.com/us/en/pd/evospeed-mid-distance-nitro-elite-3-track--field-distance-spikes/312637?swatch=01',
                       help='商品页面URL')
    parser.add_argument('--method', '-m', 
                       choices=['requests', 'selenium', 'auto'], 
                       default='auto',
                       help='爬取方法 (默认: auto)')
    parser.add_argument('--output', '-o', 
                       default='puma_product.json',
                       help='输出文件名 (默认: puma_product.json)')
    parser.add_argument('--verbose', '-v', 
                       action='store_true',
                       help='详细输出')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    print("🚀 开始爬取Puma商品信息...")
    print(f"🔗 目标URL: {args.url}")
    print(f"⚙️  使用方法: {args.method}")
    
    # 爬取商品信息
    product_info = scrape_puma_product(args.url, args.method)
    
    # 显示结果
    print_product_info(product_info)
    
    # 保存到文件
    if product_info:
        save_product_info(product_info, args.output)
    
    return product_info

if __name__ == "__main__":
    main()