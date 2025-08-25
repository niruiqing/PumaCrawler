#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接测试变体匹配逻辑
"""

import sys
import os

# 添加src目录到Python路径
src_path = os.path.join(os.path.dirname(__file__), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

def test_matching_logic():
    """直接测试匹配逻辑"""
    print("🧪 直接测试变体匹配逻辑...")
    
    # 模拟你提供的API响应数据（简化版）
    mock_variations = [
        {
            "id": "309708_01", 
            "colorValue": "01",
            "colorName": "Some Other Color",
            "variantId": "111111111111"
        },
        {
            "id": "309708_04",
            "colorValue": "04", 
            "colorName": "Pale Plum-Midnight Plum-Sun Stream",
            "variantId": "197670277549"
        },
        {
            "id": "309708_02",
            "colorValue": "02",
            "colorName": "Another Color", 
            "variantId": "222222222222"
        }
    ]
    
    test_swatch = "04"
    
    print(f"📋 测试数据:")
    print(f"   swatch参数: '{test_swatch}' (类型: {type(test_swatch)})")
    print(f"   variations总数: {len(mock_variations)}")
    
    print(f"\n📋 所有variations的colorValue:")
    for i, var in enumerate(mock_variations):
        cv = var.get('colorValue', 'N/A')
        print(f"   {i+1}. colorValue='{cv}' (类型: {type(cv)}) | variantId='{var.get('variantId', 'N/A')}'")
    
    # 手动测试匹配逻辑
    print(f"\n🔍 手动测试匹配:")
    found_match = False
    for i, variation in enumerate(mock_variations):
        color_value = variation.get('colorValue', '')
        matches = (color_value == test_swatch)
        print(f"   #{i+1}: '{color_value}' == '{test_swatch}' ? {matches}")
        if matches:
            print(f"   ✅ 找到匹配! variantId={variation.get('variantId')}")
            found_match = True
            break
    
    if not found_match:
        print(f"   ❌ 没有找到匹配")
    
    # 测试NewPumaGraphQLAPI的匹配逻辑
    print(f"\n🔧 测试NewPumaGraphQLAPI的匹配逻辑:")
    try:
        from new_puma_graphql_api import NewPumaGraphQLAPI
        
        api_client = NewPumaGraphQLAPI()
        matched_variation = api_client.find_matching_variation(mock_variations, test_swatch)
        
        if matched_variation:
            print(f"✅ API匹配结果:")
            print(f"   variantId: {matched_variation.get('variantId', 'N/A')}")
            print(f"   colorValue: {matched_variation.get('colorValue', 'N/A')}")
            print(f"   colorName: {matched_variation.get('colorName', 'N/A')}")
            
            # 验证是否是正确的匹配
            if matched_variation.get('colorValue') == test_swatch:
                print(f"🎯 ✅ 匹配正确!")
            else:
                print(f"⚠️ 匹配有问题: 期望colorValue={test_swatch}, 实际={matched_variation.get('colorValue')}")
        else:
            print(f"❌ API没有返回匹配结果")
            
    except Exception as e:
        print(f"❌ 测试API匹配逻辑时发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_matching_logic()