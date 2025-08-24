#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量爬取Puma商品信息示例
"""

import subprocess
import time
import json
from datetime import datetime

def batch_scrape_puma():
    """批量爬取多个Puma商品"""
    
    # 商品URL列表
    urls = [
        "https://us.puma.com/us/en/pd/evospeed-mid-distance-nitro-elite-3-track--field-distance-spikes/312637?swatch=01",
        # 可以添加更多Puma商品URL
    ]
    
    results = []
    
    print(f"🚀 开始批量爬取 {len(urls)} 个商品...")
    
    for i, url in enumerate(urls, 1):
        print(f"\n📦 正在爬取第 {i}/{len(urls)} 个商品...")
        print(f"🔗 URL: {url}")
        
        # 生成输出文件名
        output_file = f"batch_product_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            # 调用puma_crawler.py
            result = subprocess.run([
                'python', 'puma_crawler.py',
                '--url', url,
                '--method', 'enhanced',
                '--output', output_file
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print(f"✅ 成功爬取并保存到: {output_file}")
                
                # 读取结果
                try:
                    with open(output_file, 'r', encoding='utf-8') as f:
                        product_data = json.load(f)
                        results.append(product_data)
                except:
                    pass
            else:
                print(f"❌ 爬取失败: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print("⏰ 爬取超时")
        except Exception as e:
            print(f"❌ 执行错误: {e}")
        
        # 添加延迟避免被封IP
        if i < len(urls):
            print("⏳ 等待3秒...")
            time.sleep(3)
    
    print(f"\n🎉 批量爬取完成！成功获取 {len(results)} 个商品信息")
    
    # 汇总结果
    if results:
        summary_file = f"batch_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"📊 汇总文件已保存: {summary_file}")

if __name__ == "__main__":
    batch_scrape_puma()