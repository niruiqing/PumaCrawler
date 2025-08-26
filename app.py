#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PUMA商品信息查询Web应用
提供网页界面输入商品URL，显示完整的商品信息、图片和尺码信息
"""

import sys
import os

# 首先检查并安装必要的依赖
try:
    import requests
except ImportError:
    print("正在安装requests...")
    os.system("pip install requests")
    import requests

try:
    from flask import Flask, render_template, request, jsonify, url_for
except ImportError:
    print("正在安装Flask...")
    os.system("pip install flask")
    from flask import Flask, render_template, request, jsonify, url_for

import json
from datetime import datetime
import traceback
import re
from html import unescape

# 添加src目录到Python路径
src_path = os.path.join(os.path.dirname(__file__), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# 尝试导入新的GraphQL API客户端
new_api_client_available = False
try:
    from new_puma_graphql_api import NewPumaGraphQLAPI
    from dataclasses import asdict
    new_api_client_available = True
    print("✅ 成功导入NewPumaGraphQLAPI（新的GraphQL API客户端）")
except ImportError as e:
    print(f"⚠️ 导入NewPumaGraphQLAPI失败: {e}")
    print("❌ 无法使用新的GraphQL API，系统将无法获取商品信息")
    
    # 创建模拟的数据转换函数
    def asdict(obj):
        return {}

# 添加OpenAI SDK支持
try:
    from openai import OpenAI
except ImportError:
    print("正在安装openai...")
    os.system("pip install openai")
    from openai import OpenAI

# 添加腾讯云SDK支持
try:
    from tencentcloud.common import credential
    from tencentcloud.common.profile.client_profile import ClientProfile
    from tencentcloud.common.profile.http_profile import HttpProfile
    from tencentcloud.hunyuan.v20230901 import hunyuan_client, models
    tencent_sdk_available = True
    print("✅ 成功导入腾讯云SDK")
except ImportError as e:
    print(f"⚠️ 导入腾讯云SDK失败: {e}")
    tencent_sdk_available = False

# 导入大模型配置
try:
    from llm_config import get_llm_config, get_api_key, get_secret_key, get_region, is_llm_enabled, use_tencent_sdk
    llm_config_available = True
    print("✅ 成功导入大模型配置")
except ImportError as e:
    print(f"⚠️ 导入大模型配置失败: {e}")
    llm_config_available = False
    # 创建默认配置
    def get_llm_config():
        return {
            "api_key": "LKEAP_API_KEY",
            "secret_key": "",
            "region": "ap-beijing",
            "base_url": "https://api.lkeap.cloud.tencent.com/v1",
            "default_model": "deepseek-r1",
            "temperature": 0.7,
            "max_tokens": 3000,
            "timeout": 60,
            "enable_llm": True,
            "use_sdk": True
        }
    
    def get_api_key():
        return "LKEAP_API_KEY"
    
    def get_secret_key():
        return ""
        
    def get_region():
        return "ap-beijing"
    
    def is_llm_enabled():
        return True
        
    def use_tencent_sdk():
        return True

app = Flask(__name__)
app.secret_key = 'puma_scraper_secret_key'

# 全局API客户端实例
new_api_client = None

def get_api_client():
    """获取API客户端实例（仅使用新的GraphQL API）"""
    global new_api_client
    
    # 仅使用新的GraphQL API客户端
    if new_api_client is None and new_api_client_available:
        try:
            if 'NewPumaGraphQLAPI' in globals():
                new_api_client = NewPumaGraphQLAPI()
                print("✅ 初始化NewPumaGraphQLAPI成功")
                return new_api_client
            else:
                print("❌ NewPumaGraphQLAPI类未找到")
                return None
        except Exception as e:
            print(f"❌ 初始化NewPumaGraphQLAPI失败: {e}")
            new_api_client = None
            return None
    elif new_api_client is not None:
        return new_api_client
    
    # 如果新API不可用，直接返回None
    print("❌ 新的GraphQL API客户端不可用")
    return None

@app.route('/')
def index():
    """主页面"""
    return render_template('index.html')

@app.route('/api/scrape', methods=['POST'])
def scrape_product():
    """处理商品信息爬取请求"""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({
                'success': False,
                'error': '请输入有效的商品URL'
            })
        
        # 简单的URL验证
        if 'puma.com' not in url.lower():
            return jsonify({
                'success': False,
                'error': '请输入有效的PUMA商品页面URL'
            })
        
        print(f"🔍 开始爬取商品信息: {url}")
        print(f"🔧 新GraphQL API客户端可用: {new_api_client_available}")
        
        # 仅使用新的GraphQL API获取商品信息
        client = get_api_client()
        if not client:
            return jsonify({
                'success': False,
                'error': '新的GraphQL API客户端初始化失败，无法获取商品信息'
            })
            
        print(f"📊 使用API客户端类型: {type(client).__name__}")
        
        # 调用相应的API方法爬取商品信息
        product_info = client.scrape_product(url)
        print(f"📊 获取结果类型: {type(product_info)}")
        
        if product_info:
            print(f"✅ 成功获取商品信息")
            
            # 转换为ProductInfo对象为字典格式
            if hasattr(product_info, '__dict__'):
                # ProductInfo对象，使用dataclass的asdict
                try:
                    product_dict = asdict(product_info)
                    print(f"📋 使用asdict转换ProductInfo对象")
                except Exception as e:
                    # 如果不是dataclass，手动转换
                    product_dict = {
                        'name': getattr(product_info, 'name', ''),
                        'header': getattr(product_info, 'header', ''),
                        'sub_header': getattr(product_info, 'sub_header', ''),
                        'brand': getattr(product_info, 'brand', '') or 'PUMA',
                        'product_id': getattr(product_info, 'product_id', ''),
                        'variant_id': getattr(product_info, 'variant_id', ''),
                        'sku': getattr(product_info, 'sku', ''),
                        'style_number': getattr(product_info, 'style_number', ''),
                        'ean': getattr(product_info, 'ean', ''),
                        'price': getattr(product_info, 'price', 0),
                        'original_price': getattr(product_info, 'original_price', 0),
                        'sale_price': getattr(product_info, 'sale_price', 0),
                        'promotion_price': getattr(product_info, 'promotion_price', None),
                        'best_price': getattr(product_info, 'best_price', None),
                        'discount': getattr(product_info, 'discount', 0),
                        'tax': getattr(product_info, 'tax', 0),
                        'tax_rate': getattr(product_info, 'tax_rate', 0),
                        'description': getattr(product_info, 'description', ''),
                        'color': getattr(product_info, 'color', ''),
                        'color_name': getattr(product_info, 'color_name', ''),
                        'color_value': getattr(product_info, 'color_value', ''),
                        'color_code': getattr(product_info, 'color_code', ''),
                        'sizes': getattr(product_info, 'sizes', []),
                        'available_sizes': getattr(product_info, 'available_sizes', []),
                        'unavailable_sizes': getattr(product_info, 'unavailable_sizes', []),
                        'size_chart_id': getattr(product_info, 'size_chart_id', ''),
                        'images': getattr(product_info, 'images', []),
                        'main_images': getattr(product_info, 'main_images', []),
                        'sku_images': getattr(product_info, 'sku_images', []),
                        'preview_image': getattr(product_info, 'preview_image', ''),
                        'vertical_images': getattr(product_info, 'vertical_images', []),
                        'orderable': getattr(product_info, 'orderable', True),
                        'availability': getattr(product_info, 'availability', ''),
                        'stock_status': getattr(product_info, 'stock_status', ''),
                        'is_final_sale': getattr(product_info, 'is_final_sale', None),
                        'rating': getattr(product_info, 'rating', None),
                        'reviews_count': getattr(product_info, 'reviews_count', None),
                        'badges': getattr(product_info, 'badges', []),
                        'promotions': getattr(product_info, 'promotions', []),
                        'materials': getattr(product_info, 'materials', []),
                        'material_composition': getattr(product_info, 'material_composition', []),
                        'care_instructions': getattr(product_info, 'care_instructions', []),
                        'tech_specs': getattr(product_info, 'tech_specs', {}),
                        'features': getattr(product_info, 'features', []),
                        'manufacturer_info': getattr(product_info, 'manufacturer_info', {}),
                        'country_of_origin': getattr(product_info, 'country_of_origin', ''),
                        'valid_until': getattr(product_info, 'valid_until', ''),
                        'is_app_exclusive': getattr(product_info, 'is_app_exclusive', False),
                        'primary_category_id': getattr(product_info, 'primary_category_id', ''),
                        'product_division': getattr(product_info, 'product_division', ''),
                        'breadcrumb': getattr(product_info, 'breadcrumb', []),
                        'navigation_path': getattr(product_info, 'navigation_path', ''),
                        'all_variations': getattr(product_info, 'all_variations', []),
                        'current_variation': getattr(product_info, 'current_variation', {}),
                        'scraped_at': getattr(product_info, 'scraped_at', '') or datetime.now().isoformat(),
                        'method': 'new_graphql',
                        'url': url
                    }
                    print(f"📋 手动转换ProductInfo对象")
            else:
                product_dict = product_info if isinstance(product_info, dict) else {}
                print(f"📋 直接使用字典数据")
            
            print(f"📊 商品数据键: {list(product_dict.keys()) if isinstance(product_dict, dict) else 'N/A'}")
            # 格式化一些字段以便前端显示
            formatted_product = format_product_for_display(product_dict)
            
            product_name = formatted_product.get('basic_info', {}).get('name', 'Unknown')
            print(f"✅ 成功获取商品信息: {product_name}")
            
            return jsonify({
                'success': True,
                'product': formatted_product
            })
        else:
            print(f"❌ 未能获取到商品信息")
            return jsonify({
                'success': False,
                'error': '无法获取商品信息，可能原因：\n1. 商品URL不正确\n2. 网络连接问题\n3. 商品不存在或已下架\n4. 认证token已过期\n请检查URL或稍后再试'
            })
            
    except Exception as e:
        error_msg = str(e)
        print(f"❌ 爬取过程中发生错误: {error_msg}")
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': f'处理请求时发生错误: {error_msg}\n\n可能原因：\n1. 网络连接问题\n2. 服务器限制或认证问题\n3. 商品URL格式错误\n\n请稍后再试或检查网络连接'
        })

def parse_long_description_html(html_content):
    """
    解析longDescription中的HTML内容，提取标题和列表项
    
    Args:
        html_content (str): HTML格式的长描述内容
    
    Returns:
        dict: 包含解析后的结构化数据
    """
    if not html_content or not isinstance(html_content, str):
        return {}
    
    try:
        # 解析结果存储
        parsed_data = {}
        
        # HTML实体解码
        html_content = unescape(html_content)
        
        # 查找所有h3标题和对应的ul列表
        # 匹配模式：<h3>标题</h3>后面可能跟着文本或<ul>列表
        pattern = r'<h3[^>]*>\s*([^<]+?)\s*</h3>([\s\S]*?)(?=<h3|$)'
        
        matches = re.findall(pattern, html_content, re.IGNORECASE | re.DOTALL)
        
        for title, content in matches:
            # 清理标题
            clean_title = title.strip()
            
            # 初始化该标题的数据
            section_data = {
                'title': clean_title,
                'text': '',
                'list_items': []
            }
            
            # 查找该部分中的列表项
            li_pattern = r'<li[^>]*>\s*([\s\S]*?)\s*</li>'
            list_items = re.findall(li_pattern, content, re.IGNORECASE | re.DOTALL)
            
            for item in list_items:
                # 移除HTML标签，保留纯文本
                clean_item = re.sub(r'<[^>]+>', '', item)
                # 清理多余的空白字符
                clean_item = re.sub(r'\s+', ' ', clean_item).strip()
                if clean_item:
                    section_data['list_items'].append(clean_item)
            
            # 提取非列表的文本内容
            # 移除ul标签及其内容
            text_content = re.sub(r'<ul[^>]*>[\s\S]*?</ul>', '', content, flags=re.IGNORECASE)
            # 移除所有HTML标签
            text_content = re.sub(r'<[^>]+>', '', text_content)
            # 清理空白字符
            text_content = re.sub(r'\s+', ' ', text_content).strip()
            
            if text_content:
                section_data['text'] = text_content
            
            # 使用标题作为key存储
            parsed_data[clean_title] = section_data
        
        return parsed_data
        
    except Exception as e:
        print(f"❌ 解析longDescription HTML时发生错误: {e}")
        return {}

def format_product_for_display(product_dict):
    """格式化商品信息以便前端显示（适配PumaScraper数据结构）"""
    
    # 处理价格信息（支持新API的更多字段）
    price_info = {}
    if product_dict.get('price'):
        price_info['price'] = product_dict['price']
    if product_dict.get('original_price'):
        price_info['original_price'] = product_dict['original_price']
    if product_dict.get('sale_price'):
        price_info['sale_price'] = product_dict['sale_price']
    if product_dict.get('promotion_price'):
        price_info['promotion_price'] = product_dict['promotion_price']
    if product_dict.get('best_price'):
        price_info['best_price'] = product_dict['best_price']
    if product_dict.get('discount'):
        price_info['discount'] = product_dict['discount']
    if product_dict.get('tax'):
        price_info['tax'] = product_dict['tax']
    if product_dict.get('tax_rate'):
        price_info['tax_rate'] = product_dict['tax_rate']
    
    # 尺码信息（增强版）
    sizes_info = {}
    if product_dict.get('sizes') or product_dict.get('available_sizes') or product_dict.get('unavailable_sizes'):
        all_sizes = product_dict.get('sizes', [])
        available_sizes = product_dict.get('available_sizes', [])
        unavailable_sizes = product_dict.get('unavailable_sizes', [])
        
        # 合并所有尺码
        if not all_sizes:
            all_sizes = available_sizes + unavailable_sizes
        
        sizes_info = {
            'all_sizes': all_sizes,
            'available_sizes': available_sizes,
            'unavailable_sizes': unavailable_sizes,
            'size_groups': product_dict.get('size_groups', [])  # 添加详细尺码组信息
        }
        
        # 添加尺码统计
        sizes_info['stats'] = {
            'total': len(all_sizes),
            'available': len(available_sizes),
            'unavailable': len(unavailable_sizes)
        }
    
    # 添加尺码测量表信息
    metric_measurements = product_dict.get('metric_measurements', [])
    imperial_measurements = product_dict.get('imperial_measurements', [])
    if metric_measurements or imperial_measurements:
        if not sizes_info:
            sizes_info = {}
        sizes_info['metric_measurements'] = metric_measurements
        sizes_info['imperial_measurements'] = imperial_measurements
    
    # 处理图片信息（增强版，支持主要图片和SKU图片分离）
    images = product_dict.get('images', [])
    main_images = product_dict.get('main_images', [])
    sku_images = product_dict.get('sku_images', [])
    preview_image = product_dict.get('preview_image', '')
    
    # 如果没有分离的图片数据，使用原有图片作为主要图片
    if not main_images and not sku_images and images:
        main_images = images[:1]  # 第一张作为主要图片
        sku_images = images[1:]   # 其余作为SKU图片
    
    # 处理材料组成（增强版）
    materials = product_dict.get('materials', [])
    if not materials and product_dict.get('features'):
        # 如果没有材料信息，使用features作为替代
        materials = product_dict.get('features', [])
    
    # 处理描述（移除HTML标签）
    description = product_dict.get('description', '')
    if '<' in description and '>' in description:
        # 简单的HTML标签移除
        import re
        description = re.sub(r'<[^>]+>', '', description)
        description = description.replace('&nbsp;', ' ').strip()
    
    # 处理制造商信息（PumaScraper通常没有这些信息）
    manufacturer = {}
    
    # 新增：处理技术规格
    tech_specs = product_dict.get('tech_specs', {})
    
    # 新增：处理商品徽章
    badges = product_dict.get('badges', [])
    
    # 新增：处理护理说明
    care_instructions = product_dict.get('care_instructions', [])
    
    return {
        'basic_info': {
            'name': product_dict.get('name', ''),
            'header': product_dict.get('header', '') or product_dict.get('name', ''),
            'sub_header': product_dict.get('sub_header', ''),
            'brand': product_dict.get('brand') or 'PUMA',
            'product_id': product_dict.get('product_id', ''),
            'variant_id': product_dict.get('variant_id', ''),
            'sku': product_dict.get('sku', ''),
            'style_number': product_dict.get('style_number', ''),
            'ean': product_dict.get('ean', ''),
            'description': description,
            'orderable': product_dict.get('orderable', True),
            'is_final_sale': product_dict.get('is_final_sale', False),
            'category': product_dict.get('category', ''),
            'subcategory': product_dict.get('subcategory', ''),
            'primary_category_id': product_dict.get('primary_category_id', ''),
            'product_division': product_dict.get('product_division', ''),
            'gender': product_dict.get('gender', ''),
            'age_group': product_dict.get('age_group', ''),
            'promotion': product_dict.get('promotion', ''),
            'valid_until': product_dict.get('valid_until', ''),
            'is_app_exclusive': product_dict.get('is_app_exclusive', False),
            'size_chart_id': product_dict.get('size_chart_id', ''),
            'breadcrumb': product_dict.get('breadcrumb', []),
            'navigation_path': product_dict.get('navigation_path', '')
        },
        'price_info': price_info,
        'color_info': {
            'name': product_dict.get('color_name', '') or product_dict.get('color', ''),
            'value': product_dict.get('color_value', '') or product_dict.get('color_code', '')
        },
        'images': images,
        'main_images': main_images,
        'sku_images': sku_images,
        'preview_image': preview_image,
        'all_variations': product_dict.get('all_variations', []),
        'current_variation': process_current_variation(product_dict.get('current_variation', {})),
        'sizes': sizes_info,
        'metric_measurements': product_dict.get('metric_measurements', []),
        'imperial_measurements': product_dict.get('imperial_measurements', []),
        'size_groups': product_dict.get('size_groups', []),
        'materials': materials,
        'care_instructions': care_instructions,
        'tech_specs': tech_specs,
        'badges': badges,
        'features': product_dict.get('features', []),
        'manufacturer': manufacturer,
        'ratings': {
            'average': product_dict.get('rating', ''),
            'count': product_dict.get('reviews_count', '')
        },
        'availability': {
            'status': product_dict.get('availability', ''),
            'stock_status': product_dict.get('stock_status', '')
        },
        'scraped_at': product_dict.get('scraped_at', ''),
        'method': product_dict.get('method', 'requests'),
        'url': product_dict.get('url', '')
    }

def process_current_variation(current_variation):
    """
    处理当前变体信息，解析longDescription中HTML内容
    
    Args:
        current_variation (dict): 当前变体信息
    
    Returns:
        dict: 处理后的变体信息
    """
    if not current_variation:
        return {}
    
    # 复制原始数据，避免修改原对象
    processed_variation = current_variation.copy()
    
    # 处理longDescription
    long_description = current_variation.get('longDescription', '')
    if long_description:
        # 解析HTML内容
        parsed_content = parse_long_description_html(long_description)
        
        # 添加解析后的结构化数据
        processed_variation['parsed_long_description'] = parsed_content
        
        # 保留原始HTML内容
        processed_variation['longDescription_raw'] = long_description
        
        # 生成纯文本版本（去除HTML标签）
        text_only = re.sub(r'<[^>]+>', '', long_description)
        text_only = re.sub(r'\s+', ' ', text_only).strip()
        processed_variation['longDescription_text'] = text_only
    
    return processed_variation

# 大模型API配置
tencent_client = None

def get_llm_client():
    """获取腾讯云大模型API客户端实例"""
    global tencent_client
    
    # 检查是否启用大模型功能
    if not is_llm_enabled():
        print("⏭️ 大模型功能未启用")
        return None
        
    # 仅使用腾讯云SDK
    if tencent_sdk_available:
        if tencent_client is None:
            try:
                # 获取配置
                config = get_llm_config()
                api_key = get_api_key()
                secret_key = get_secret_key()
                region = get_region()
                
                if not api_key or api_key == "LKEAP_API_KEY":
                    print("❌ 未配置有效的API Key，请检查配置")
                    return None
                
                # 初始化腾讯云凭证
                cred = credential.Credential(api_key, secret_key)
                
                # 配置HTTP
                httpProfile = HttpProfile()
                httpProfile.endpoint = "hunyuan.tencentcloudapi.com"
                
                # 配置客户端
                clientProfile = ClientProfile()
                clientProfile.httpProfile = httpProfile
                
                # 初始化客户端
                tencent_client = hunyuan_client.HunyuanClient(cred, region, clientProfile)
                print("✅ 成功初始化腾讯云大模型API客户端")
            except Exception as e:
                print(f"❌ 初始化腾讯云大模型API客户端失败: {e}")
                tencent_client = None
        return tencent_client
    else:
        print("❌ 腾讯云SDK不可用")
        return None

@app.route('/api/llm/chat', methods=['POST'])
def llm_chat():
    """大模型对话接口"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({
                'success': False,
                'error': '请输入有效的消息内容'
            })
        
        client = get_llm_client()
        if not client:
            return jsonify({
                'success': False,
                'error': '大模型API客户端不可用，请检查API Key配置'
            })
        
        print(f"💬 大模型对话请求: {message[:100]}..." if len(message) > 100 else f"💬 大模型对话请求: {message}")
        
        # 使用腾讯云SDK调用
        config = get_llm_config()
        
        # 构造请求
        req = models.ChatCompletionsRequest()
        params = {
            "Model": config.get("default_model", "deepseek-r1"),
            "Messages": [
                {
                    "Role": "user",
                    "Content": message
                }
            ],
            "Temperature": config.get("temperature", 0.7),
            "TopP": 1.0
        }
        req.from_json_string(json.dumps(params))
        
        # 发送请求
        resp = client.ChatCompletions(req)
        
        # 解析响应
        response_content = resp.Choices[0].Message.Content if resp.Choices else ""
        
        print(f"✅ 大模型响应成功，长度: {len(response_content)} 字符")
        
        return jsonify({
            'success': True,
            'response': response_content,
            'model': config.get("default_model", "deepseek-r1"),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ 大模型调用失败: {error_msg}")
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': f'大模型调用失败: {error_msg}'
        })

@app.route('/api/llm/analyze-product', methods=['POST'])
def analyze_product():
    """使用大模型分析商品信息"""
    try:
        data = request.get_json()
        product_data = data.get('product', {})
        analysis_type = data.get('type', 'general')  # general, description, recommendation
        
        if not product_data:
            return jsonify({
                'success': False,
                'error': '请提供有效的商品数据'
            })
        
        client = get_llm_client()
        if not client:
            return jsonify({
                'success': False,
                'error': '大模型API客户端不可用，请检查API Key配置'
            })
        
        # 构建分析提示词
        product_name = product_data.get('basic_info', {}).get('name', '未知商品')
        product_description = product_data.get('basic_info', {}).get('description', '')
        price_info = product_data.get('price_info', {})
        materials = product_data.get('materials', [])
        features = product_data.get('features', [])
        
        if analysis_type == 'description':
            prompt = f"""作为一个专业的商品分析师，请对以下 PUMA 商品进行详细的描述性分析：

商品名称：{product_name}
商品描述：{product_description}
价格信息：{json.dumps(price_info, ensure_ascii=False, indent=2)}
材料信息：{materials}
产品特性：{features}

请从以下角度提供分析：
1. 产品定位与特色
2. 材料与品质分析
3. 价格竞争力评估
4. 适用场景推荐
5. 产品优势与亮点

请用中文回答，内容要专业而易懂。"""
        elif analysis_type == 'recommendation':
            prompt = f"""作为一个购物顾问，请为这款 PUMA 商品提供购买建议：

商品名称：{product_name}
商品描述：{product_description}
价格信息：{json.dumps(price_info, ensure_ascii=False, indent=2)}
材料信息：{materials}
产品特性：{features}

请提供：
1. 适合人群分析
2. 搭配建议
3. 尺码选择指导
4. 保养与护理建议
5. 性价比评估
6. 购买注意事项

请用中文回答，内容要实用且具有指导性。"""
        else:  # general
            prompt = f"""作为一个专业的商品分析师，请对以下 PUMA 商品进行综合分析：

商品名称：{product_name}
商品描述：{product_description}
价格信息：{json.dumps(price_info, ensure_ascii=False, indent=2)}
材料信息：{materials}
产品特性：{features}

请提供简洁而全面的分析，包括产品亮点、适用场景和购买建议。请用中文回答。"""
        
        print(f"🔍 开始分析商品: {product_name} (分析类型: {analysis_type})")
        
        # 使用腾讯云SDK调用
        config = get_llm_config()
        
        # 构造请求
        req = models.ChatCompletionsRequest()
        params = {
            "Model": config.get("default_model", "deepseek-r1"),
            "Messages": [
                {
                    "Role": "user",
                    "Content": prompt
                }
            ],
            "Temperature": config.get("temperature", 0.7),
            "TopP": 1.0
        }
        req.from_json_string(json.dumps(params))
        
        # 发送请求
        resp = client.ChatCompletions(req)
        
        # 解析响应
        analysis_result = resp.Choices[0].Message.Content if resp.Choices else ""
        
        print(f"✅ 商品分析完成，结果长度: {len(analysis_result)} 字符")
        
        return jsonify({
            'success': True,
            'analysis': analysis_result,
            'analysis_type': analysis_type,
            'product_name': product_name,
            'model': config.get("default_model", "deepseek-r1"),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ 商品分析失败: {error_msg}")
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': f'商品分析失败: {error_msg}'
        })

@app.route('/api/health')
def health_check():
    """健康检查接口"""
    llm_status = 'available' if get_llm_client() is not None else 'unavailable'
    llm_enabled = is_llm_enabled()
    sdk_mode = "tencent" if tencent_sdk_available else "unavailable"
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'PUMA商品信息查询服务',
        'features': {
            'product_scraping': 'available',
            'llm_analysis': llm_status,
            'llm_enabled': llm_enabled,
            'llm_sdk': sdk_mode,
            'graphql_api': 'available' if new_api_client_available else 'unavailable'
        }
    })

if __name__ == '__main__':
    print("🚀 启动PUMA商品信息查询Web服务...")
    print("📱 请在浏览器中访问: http://localhost:5000")
    
    # 创建templates目录（如果不存在）
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    
    os.makedirs(templates_dir, exist_ok=True)
    os.makedirs(static_dir, exist_ok=True)
    
    # 启动Flask应用
    app.run(debug=True, host='0.0.0.0', port=5000)