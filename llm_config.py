#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大模型API配置文件
请根据您的实际情况修改配置项
"""

import os

# 大模型API配置
LLM_CONFIG = {
    # 腾讯云知识引擎原子能力API配置
    "api_key": os.getenv("LKEAP_API_KEY", "LKEAP_API_KEY"),  # 请替换为您的实际API Key
    "secret_key": os.getenv("LKEAP_SECRET_KEY", ""),  # 腾讯云Secret Key
    "region": "ap-beijing",  # 腾讯云区域
    "base_url": "https://hunyuan.tencentcloudapi.com",
    "default_model": "hunyuan-lite",  # 腾讯云模型：hunyuan-lite, hunyuan-standard, hunyuan-pro
    
    # 请求参数配置
    "temperature": 0.7,
    "max_tokens": 3000,
    "timeout": 60,
    
    # 功能开关
    "enable_llm": True,  # 是否启用大模型功能
    "enable_analysis": True,  # 是否启用商品分析功能
    "use_sdk": True,  # 是否使用腾讯云SDK（固定为True）
    
    # 分析模板配置
    "analysis_types": {
        "general": "综合分析",
        "description": "详细描述分析", 
        "recommendation": "购买建议分析"
    }
}

# API Key获取指南
API_KEY_HELP = """
🔑 如何获取腾讯云API Key：

1. 访问腾讯云控制台：https://console.cloud.tencent.com/
2. 进入访问管理->访问密钥->API密钥管理：https://console.cloud.tencent.com/cam/capi
3. 点击"新建密钥"创建新的API密钥
4. 获取SecretId和SecretKey
5. 将SecretId设置为LKEAP_API_KEY环境变量
6. 将SecretKey设置为LKEAP_SECRET_KEY环境变量

📖 腾讯云大模型文档：https://cloud.tencent.com/document/product/1787

⚙️ 环境变量设置方法：
Windows: 
set LKEAP_API_KEY=AKIDyour-actual-secret-id
set LKEAP_SECRET_KEY=your-actual-secret-key

Linux/Mac:
export LKEAP_API_KEY=AKIDyour-actual-secret-id
export LKEAP_SECRET_KEY=your-actual-secret-key

🔧 配置文件修改方法：
直接修改本文件中的 LLM_CONFIG["api_key"] 和 LLM_CONFIG["secret_key"] 值
"""

def get_llm_config():
    """获取大模型配置"""
    return LLM_CONFIG.copy()

def is_llm_enabled():
    """检查大模型功能是否启用"""
    return LLM_CONFIG.get("enable_llm", True)

def use_tencent_sdk():
    """检查是否使用腾讯云SDK（固定返回True）"""
    return True

def get_api_key():
    """获取API Key (SecretId)"""
    api_key = LLM_CONFIG.get("api_key")
    if not api_key or api_key == "LKEAP_API_KEY":
        print("⚠️ 警告：未设置有效的API Key (SecretId)")
        print(API_KEY_HELP)
        return None
    return api_key

def get_secret_key():
    """获取Secret Key"""
    secret_key = LLM_CONFIG.get("secret_key")
    if not secret_key:
        print("⚠️ 警告：未设置Secret Key")
        print(API_KEY_HELP)
        return None
    return secret_key

def get_region():
    """获取区域"""
    return LLM_CONFIG.get("region", "ap-beijing")

def validate_config():
    """验证配置有效性"""
    issues = []
    
    api_key = get_api_key()
    if not api_key:
        issues.append("❌ API Key (SecretId)未正确配置")
    
    secret_key = get_secret_key()
    if not secret_key:
        issues.append("❌ Secret Key未正确配置")
    
    if not LLM_CONFIG.get("base_url"):
        issues.append("❌ API基础URL未配置")
    
    if not LLM_CONFIG.get("default_model"):
        issues.append("❌ 默认模型未配置")
    
    if issues:
        print("配置验证失败：")
        for issue in issues:
            print(f"  {issue}")
        return False
    
    print("✅ 配置验证通过")
    return True

if __name__ == "__main__":
    print("🔧 大模型API配置验证")
    print("=" * 40)
    validate_config()
    print("\n📋 当前配置：")
    config = get_llm_config()
    # 隐藏敏感信息
    config["api_key"] = "***" + config["api_key"][-4:] if len(config["api_key"]) > 4 else "***"
    config["secret_key"] = "***" + config["secret_key"][-4:] if len(config["secret_key"]) > 4 else "***"
    
    for key, value in config.items():
        print(f"  {key}: {value}")