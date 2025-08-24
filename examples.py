#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Puma商品信息爬虫使用示例
演示不同的使用场景和方法
"""

import json
from puma_crawler import main as crawler_main
from enhanced_puma_scraper import enhanced_scrape_puma
import sys
import os

def example_1_basic_usage():
    """示例1: 基本用法"""
    print("=" * 60)
    print("示例1: 基本用法 - 使用默认URL和自动模式")
    print("=" * 60)
    
    # 模拟命令行参数
    original_argv = sys.argv
    sys.argv = ['puma_crawler.py', '--method', 'auto']
    
    try:
        result = crawler_main()
        return result
    except SystemExit:
        pass
    finally:
        sys.argv = original_argv

def example_2_custom_url():
    """示例2: 自定义URL"""
    print("\\n" + "=" * 60)
    print("示例2: 自定义URL爬取")
    print("=" * 60)
    
    # 其他Puma商品URL示例
    url = "https://us.puma.com/us/en/pd/evospeed-mid-distance-nitro-elite-3-track--field-distance-spikes/312637?swatch=01"
    
    print(f"爬取URL: {url}")
    
    # 使用增强版爬虫
    result = enhanced_scrape_puma(url)
    
    if result:
        print(f"✅ 成功获取商品: {result.get('name', 'N/A')}")
        print(f"💰 价格: {result.get('currency', 'USD')} ${result.get('price', 'N/A')}")
        return result
    else:
        print("❌ 爬取失败")
        return None

def example_3_batch_scraping():
    """示例3: 批量爬取（演示概念）"""
    print("\\n" + "=" * 60)
    print("示例3: 批量爬取概念演示")
    print("=" * 60)
    
    # 注意：实际使用时请遵守网站的robots.txt和使用条款
    # 这里只是演示概念，实际批量爬取需要添加合适的延迟
    
    urls = [
        "https://us.puma.com/us/en/pd/evospeed-mid-distance-nitro-elite-3-track--field-distance-spikes/312637?swatch=01",
        # 可以添加更多URL
    ]
    
    results = []
    
    for i, url in enumerate(urls, 1):
        print(f"\\n正在爬取第 {i} 个商品...")
        print(f"URL: {url}")
        
        try:
            result = enhanced_scrape_puma(url)
            if result:
                results.append(result)
                print(f"✅ 成功: {result.get('name', 'N/A')}")
            else:
                print("❌ 失败")
                
        except Exception as e:
            print(f"❌ 错误: {e}")
        
        # 在实际批量爬取中，应该添加延迟以避免被封IP
        # import time
        # time.sleep(2)  # 延迟2秒
    
    print(f"\\n批量爬取完成，成功获取 {len(results)} 个商品信息")
    return results

def example_4_data_analysis():
    """示例4: 数据分析"""
    print("\\n" + "=" * 60)
    print("示例4: 简单数据分析")
    print("=" * 60)
    
    # 读取之前保存的JSON文件
    json_files = [f for f in os.listdir('.') if f.endswith('.json') and 'puma' in f]
    
    if not json_files:
        print("❌ 没有找到商品数据文件")
        return
    
    products = []
    for file in json_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if data.get('name'):
                    products.append(data)
        except:
            continue
    
    if not products:
        print("❌ 没有有效的商品数据")
        return
    
    print(f"📊 分析 {len(products)} 个商品数据:")
    
    # 价格分析
    prices = []
    for product in products:
        price = product.get('price', '')
        if price and price.replace('.', '').isdigit():
            prices.append(float(price))
    
    if prices:
        print(f"💰 价格统计:")
        print(f"   平均价格: ${sum(prices)/len(prices):.2f}")
        print(f"   最高价格: ${max(prices):.2f}")
        print(f"   最低价格: ${min(prices):.2f}")
    
    # 品牌统计
    brands = {}
    for product in products:
        brand = product.get('brand', 'Unknown')
        brands[brand] = brands.get(brand, 0) + 1
    
    print(f"🏷️  品牌统计:")
    for brand, count in brands.items():
        print(f"   {brand}: {count} 个商品")
    
    # 描述长度分析
    desc_lengths = []
    for product in products:
        desc = product.get('description', '')
        if desc:
            desc_lengths.append(len(desc))
    
    if desc_lengths:
        print(f"📝 描述统计:")
        print(f"   平均描述长度: {sum(desc_lengths)/len(desc_lengths):.0f} 字符")
        print(f"   最长描述: {max(desc_lengths)} 字符")
        print(f"   最短描述: {min(desc_lengths)} 字符")

def example_5_export_csv():
    """示例5: 导出为CSV格式"""
    print("\\n" + "=" * 60)
    print("示例5: 导出CSV格式")
    print("=" * 60)
    
    try:
        import csv
        
        # 读取JSON数据
        json_files = [f for f in os.listdir('.') if f.endswith('.json') and 'puma' in f]
        
        if not json_files:
            print("❌ 没有找到商品数据文件")
            return
        
        products = []
        for file in json_files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data.get('name'):
                        products.append(data)
            except:
                continue
        
        if not products:
            print("❌ 没有有效的商品数据")
            return
        
        # 定义CSV字段
        fieldnames = ['name', 'brand', 'price', 'currency', 'color', 'product_id', 'description', 'url']
        
        csv_filename = 'puma_products.csv'
        
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for product in products:
                row = {}
                for field in fieldnames:
                    value = product.get(field, '')
                    # 处理描述字段，限制长度
                    if field == 'description' and value:
                        value = value[:200] + '...' if len(value) > 200 else value
                    row[field] = value
                writer.writerow(row)
        
        print(f"✅ CSV文件已导出: {csv_filename}")
        print(f"📊 包含 {len(products)} 个商品")
        
    except ImportError:
        print("❌ CSV模块不可用")
    except Exception as e:
        print(f"❌ 导出CSV失败: {e}")

def main():
    """主函数 - 运行所有示例"""
    print("🚀 Puma商品信息爬虫使用示例")
    print("=" * 60)
    
    try:
        # 示例1: 基本用法
        example_1_basic_usage()
        
        # 示例2: 自定义URL
        example_2_custom_url()
        
        # 示例3: 批量爬取
        example_3_batch_scraping()
        
        # 示例4: 数据分析
        example_4_data_analysis()
        
        # 示例5: 导出CSV
        example_5_export_csv()
        
        print("\\n🎉 所有示例运行完成!")
        
    except KeyboardInterrupt:
        print("\\n❌ 用户中断")
    except Exception as e:
        print(f"\\n❌ 运行出错: {e}")

if __name__ == "__main__":
    main()