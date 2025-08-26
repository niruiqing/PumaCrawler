#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的腾讯云SDK集成测试脚本
"""

import sys
import os

# 添加项目路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

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
        # 直接导入配置，避免循环导入问题
        import importlib.util
        spec = importlib.util.spec_from_file_location("llm_config", os.path.join(project_root, "llm_config.py"))
        llm_config_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(llm_config_module)
        
        config = llm_config_module.get_llm_config()
        print("✅ LLM配置导入成功")
        print(f"  默认模型: {config.get('default_model', 'unknown')}")
        print(f"  区域: {config.get('region', 'unknown')}")
        return True
    except Exception as e:
        print(f"❌ LLM配置测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试腾讯云SDK集成...")
    print("=" * 50)
    
    tests = [
        test_tencent_sdk_import,
        test_llm_config
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"✅ 测试完成: {passed}/{len(tests)} 通过")
    
    if passed == len(tests):
        print("🎉 腾讯云SDK基础集成测试通过！")
    else:
        print("⚠️ 部分测试未通过，请检查配置和依赖")

if __name__ == "__main__":
    main()