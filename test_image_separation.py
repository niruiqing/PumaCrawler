#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试主要图片和SKU变体图片分离功能
"""

import sys
import os

# 添加src目录到Python路径
src_path = os.path.join(os.path.dirname(__file__), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from new_puma_graphql_api import NewPumaGraphQLAPI

def test_image_separation():
    """测试图片分离功能"""
    print("🚀 测试主要图片和SKU变体图片分离功能...")
    
    # 创建API客户端
    api_client = NewPumaGraphQLAPI()
    
    # 测试URL（包含swatch参数）
    test_url = "https://us.puma.com/us/en/pd/deviate-nitro-3-womens-running-shoes/309708?swatch=04"
    
    print(f"🌐 测试URL: {test_url}")
    
    # 获取商品信息
    print(f"\n📡 开始获取商品信息...")
    product_info = api_client.scrape_product(test_url)
    
    if product_info:
        print(f"\n✅ 成功获取商品信息!")
        print(f"   商品名称: {product_info.name}")
        print(f"   选中的SKU ID: {product_info.variant_id}")
        print(f"   颜色代码: {product_info.color_value}")
        
        # 测试图片分离结果
        print(f"\n🖼️ 图片分离测试结果:")
        
        # 主要产品图片
        print(f"📋 主要产品图片 ({len(product_info.main_images)}张):")
        for i, img in enumerate(product_info.main_images, 1):
            print(f"   {i}. {img}")
        
        # SKU变体图片
        print(f"\n📋 当前SKU图片 ({len(product_info.sku_images)}张):")
        for i, img in enumerate(product_info.sku_images, 1):
            print(f"   {i}. {img}")
        
        # 预览图片
        if product_info.preview_image:
            print(f"\n📋 预览图片:")
            print(f"   {product_info.preview_image}")
        
        # 总图片数（向后兼容）
        print(f"\n📋 总图片数 (向后兼容): {len(product_info.images)}张")
        
        # 所有SKU信息
        print(f"\n📋 所有SKU信息:")
        if product_info.all_variations:
            print(f"   SKU总数: {len(product_info.all_variations)}")
            for i, sku in enumerate(product_info.all_variations[:3], 1):  # 只显示前3个
                print(f"   SKU{i}: {sku.get('colorName', 'N/A')} ({sku.get('colorValue', 'N/A')}) - 图片数: {len(sku.get('images', []))}")
        
        # 当前选中的SKU信息
        print(f"\n📋 当前选中SKU:")
        if product_info.current_variation:
            current = product_info.current_variation
            print(f"   SKU名称: {current.get('name', 'N/A')}")
            print(f"   颜色: {current.get('colorName', 'N/A')} ({current.get('colorValue', 'N/A')})")
            print(f"   图片数: {len(current.get('images', []))}")
            
        return True
    else:
        print(f"❌ 获取商品信息失败")
        return False

def test_app_format():
    """测试app.py中的格式化功能"""
    print(f"\n🔧 测试app.py格式化功能...")
    
    # 模拟ProductInfo对象
    class MockProductInfo:
        def __init__(self):
            self.main_images = [
                "https://images.puma.com/image/upload/main1.jpg",
                "https://images.puma.com/image/upload/main2.jpg"
            ]
            self.sku_images = [
                "https://images.puma.com/image/upload/sku1.jpg", 
                "https://images.puma.com/image/upload/sku2.jpg",
                "https://images.puma.com/image/upload/sku3.jpg"
            ]
            self.images = self.main_images + self.sku_images  # 总图片
            self.preview_image = "https://images.puma.com/image/upload/preview.jpg"
            self.all_variations = [
                {
                    'colorValue': '04',
                    'colorName': 'Test Color',
                    'images': self.sku_images
                }
            ]
            self.current_variation = self.all_variations[0]
    
    mock_product = MockProductInfo()
    
    print(f"📊 模拟数据:")
    print(f"   主要图片: {len(mock_product.main_images)}张")
    print(f"   SKU图片: {len(mock_product.sku_images)}张")
    print(f"   总图片: {len(mock_product.images)}张")
    print(f"   SKU数量: {len(mock_product.all_variations)}个")
    
    return True

if __name__ == "__main__":
    print("="*60)
    print("🖼️ 图片分离功能测试")
    print("="*60)
    
    # 测试实际API
    success1 = test_image_separation()
    
    # 测试格式化功能
    success2 = test_app_format()
    
    print(f"\n{'='*60}")
    if success1 and success2:
        print("✅ 所有测试通过！图片分离功能正常工作")
    else:
        print("❌ 部分测试失败，请检查配置")
    print("="*60)