#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试腾讯云SDK集成
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_tencent_sdk_import():
    """测试腾讯云SDK导入"""
    print("🧪 测试腾讯云SDK导入...")
    
    try:
        from tencentcloud.common import credential
        from tencentcloud.common.profile.client_profile import ClientProfile
        from tencentcloud.common.profile.http_profile import HttpProfile
        from tencentcloud.hunyuan.v20230901 import hunyuan_client, models
        print("✅ 腾讯云SDK导入成功")
        return True
    except ImportError as e:
        print(f"❌ 腾讯云SDK导入失败: {e}")
        return False

def test_llm_config():
    """测试LLM配置"""
    print("\n🧪 测试LLM配置...")
    
    try:
        from llm_config import get_llm_config, get_api_key, is_llm_enabled, use_tencent_sdk
        config = get_llm_config()
        print("✅ LLM配置导入成功")
        print(f"  启用状态: {is_llm_enabled()}")
        print(f"  SDK模式: {'腾讯云' if use_tencent_sdk() else 'OpenAI兼容'}")
        print(f"  默认模型: {config.get('default_model', 'unknown')}")
        return True
    except Exception as e:
        print(f"❌ LLM配置测试失败: {e}")
        return False

def test_client_initialization():
    """测试客户端初始化"""
    print("\n🧪 测试客户端初始化...")
    
    try:
        from app import get_llm_client
        client = get_llm_client()
        if client:
            print("✅ 客户端初始化成功")
            return True
        else:
            print("⚠️ 客户端初始化失败（可能是配置问题）")
            return False
    except Exception as e:
        print(f"❌ 客户端初始化测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试腾讯云SDK集成...")
    print("=" * 50)
    
    tests = [
        test_tencent_sdk_import,
        test_llm_config,
        test_client_initialization
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"✅ 测试完成: {passed}/{len(tests)} 通过")
    
    if passed == len(tests):
        print("🎉 所有测试通过，腾讯云SDK集成成功！")
    else:
        print("⚠️ 部分测试未通过，请检查配置和依赖")

if __name__ == "__main__":
    main()