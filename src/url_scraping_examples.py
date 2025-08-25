#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Puma商品爬虫 - URL抓取示例
展示如何抓取指定URL的商品信息
"""

import subprocess
import sys
import json
from datetime import datetime

class PumaURLScraper:
    """Puma URL抓取器"""
    
    def __init__(self):
        self.base_command = [sys.executable, "puma_crawler.py"]
    
    def scrape_url(self, url, method="auto", output_file=None, verbose=False):
        """
        抓取指定URL的商品信息
        
        Args:
            url (str): 商品页面URL
            method (str): 爬取方法 (requests/enhanced/graphql/auto)
            output_file (str): 输出文件名 (可选)
            verbose (bool): 是否显示详细信息
        
        Returns:
            dict: 商品信息
        """
        
        print(f"🚀 开始抓取商品信息...")
        print(f"🔗 目标URL: {url}")
        print(f"⚙️  使用方法: {method}")
        
        # 构建命令
        cmd = self.base_command + ["--url", url, "--method", method]
        
        if output_file:
            cmd.extend(["--output", output_file])
            print(f"💾 输出文件: {output_file}")
        
        if verbose:
            cmd.append("--verbose")
        
        try:
            # 执行爬取命令
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
            
            if result.returncode == 0:
                print("✅ 爬取成功！")
                
                # 如果有输出文件，读取结果
                if output_file:
                    try:
                        with open(output_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        return data
                    except Exception as e:
                        print(f"⚠️  读取输出文件失败: {e}")
                        return None
                else:
                    print("ℹ️  结果已显示在命令行中")
                    return True
            else:
                print(f"❌ 爬取失败: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"❌ 执行出错: {e}")
            return None
    
    def batch_scrape_urls(self, urls, method="auto", output_dir="batch_results"):
        """
        批量抓取多个URL
        
        Args:
            urls (list): URL列表
            method (str): 爬取方法
            output_dir (str): 输出目录
        """
        
        import os
        
        # 创建输出目录
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        results = []
        
        for i, url in enumerate(urls, 1):
            print(f"\n📦 批量抓取 {i}/{len(urls)}")
            
            # 生成输出文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"{output_dir}/product_{i}_{timestamp}.json"
            
            # 抓取商品信息
            result = self.scrape_url(url, method, output_file, verbose=False)
            
            if result:
                results.append({
                    'url': url,
                    'output_file': output_file,
                    'success': True
                })
                print(f"✅ 第{i}个商品抓取成功")
            else:
                results.append({
                    'url': url,
                    'output_file': None,
                    'success': False
                })
                print(f"❌ 第{i}个商品抓取失败")
        
        # 保存批量结果摘要
        summary_file = f"{output_dir}/batch_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump({
                'total_urls': len(urls),
                'successful': len([r for r in results if r['success']]),
                'failed': len([r for r in results if not r['success']]),
                'results': results,
                'scraped_at': datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n📊 批量抓取完成！摘要保存到: {summary_file}")
        return results

def main():
    """示例用法"""
    
    scraper = PumaURLScraper()
    
    # 示例1: 抓取单个URL
    print("=" * 60)
    print("示例1: 抓取单个URL")
    print("=" * 60)
    
    example_url = "https://us.puma.com/us/en/pd/evospeed-mid-distance-nitro-elite-3-track--field-distance-spikes/312637?swatch=01"
    
    # 使用不同方法抓取
    methods = ["enhanced", "graphql", "auto"]
    
    for method in methods:
        print(f"\n🔧 测试 {method} 方法:")
        output_file = f"example_{method}_result.json"
        result = scraper.scrape_url(example_url, method, output_file)
        
        if result:
            print(f"   ✅ {method} 方法成功")
        else:
            print(f"   ❌ {method} 方法失败")
    
    # 示例2: 批量抓取多个URL
    print("\n" + "=" * 60)
    print("示例2: 批量抓取多个URL")
    print("=" * 60)
    
    # 示例URL列表（可以替换为真实的不同商品URL）
    example_urls = [
        "https://us.puma.com/us/en/pd/evospeed-mid-distance-nitro-elite-3-track--field-distance-spikes/312637?swatch=01",
        # 可以添加更多URL
        # "https://us.puma.com/us/en/pd/another-product/123456",
        # "https://us.puma.com/us/en/pd/third-product/789012",
    ]
    
    if len(example_urls) > 1:
        batch_results = scraper.batch_scrape_urls(example_urls, method="auto")
        print(f"批量抓取结果: {len(batch_results)} 个URL处理完成")

if __name__ == "__main__":
    main()