#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Puma商品页面尺码分析器
分析页面中的所有尺码相关元素
"""

import requests
from bs4 import BeautifulSoup
import json
import re

def analyze_sizes(url):
    """分析页面中的所有尺码元素"""
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    }
    
    try:
        print(f"🔍 分析页面尺码: {url}")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        print("✅ 页面获取成功，开始分析尺码...")
        
        # 1. 查找所有可能包含尺码的元素
        size_keywords = ['size', 'Size', 'SIZE', '尺码', '码数']
        
        print("\n🔍 搜索包含'size'关键词的元素...")
        for keyword in size_keywords:
            # 查找class包含size的元素
            elements_by_class = soup.find_all(attrs={'class': re.compile(keyword, re.IGNORECASE)})
            print(f"   class包含'{keyword}': {len(elements_by_class)} 个元素")
            
            # 查找data-testid包含size的元素
            elements_by_testid = soup.find_all(attrs={'data-testid': re.compile(keyword, re.IGNORECASE)})
            print(f"   data-testid包含'{keyword}': {len(elements_by_testid)} 个元素")
            
            # 查找id包含size的元素
            elements_by_id = soup.find_all(attrs={'id': re.compile(keyword, re.IGNORECASE)})
            print(f"   id包含'{keyword}': {len(elements_by_id)} 个元素")
        
        # 2. 查找所有button元素（尺码通常是按钮）
        all_buttons = soup.find_all('button')
        print(f"\n📊 页面总共找到 {len(all_buttons)} 个button元素")
        
        potential_size_buttons = []
        for i, btn in enumerate(all_buttons):
            btn_info = {
                'index': i + 1,
                'text': btn.get_text(strip=True),
                'class': btn.get('class', []),
                'id': btn.get('id', ''),
                'data_testid': btn.get('data-testid', ''),
                'type': btn.get('type', ''),
                'disabled': btn.get('disabled', False),
                'parent_class': btn.parent.get('class', []) if btn.parent else [],
            }
            
            # 判断是否可能是尺码按钮
            text = btn_info['text']
            if text and len(text) <= 15:  # 尺码文本通常很短
                # 检查是否像尺码（数字、数字.5、US/EU尺码等）
                if (text.replace('.', '').replace('½', '').isdigit() or
                    re.match(r'^\d+\.?5?$', text) or
                    re.match(r'^(US|EU|UK)?\s*\d+\.?5?$', text, re.IGNORECASE) or
                    text.upper() in ['XS', 'S', 'M', 'L', 'XL', 'XXL'] or
                    any(keyword in str(btn_info['class']).lower() for keyword in ['size', 'Size']) or
                    any(keyword in str(btn_info['data_testid']).lower() for keyword in ['size', 'Size'])):
                    potential_size_buttons.append(btn_info)
        
        print(f"🎯 找到 {len(potential_size_buttons)} 个疑似尺码按钮:")
        for btn in potential_size_buttons[:15]:  # 只显示前15个
            print(f"   #{btn['index']}: '{btn['text']}' class={btn['class']} data-testid={btn['data_testid']}")
        
        # 3. 查找select下拉框中的尺码
        select_elements = soup.find_all('select')
        print(f"\n📋 页面找到 {len(select_elements)} 个下拉框")
        
        size_options = []
        for select in select_elements:
            # 检查select是否与尺码相关
            select_attrs = {
                'name': select.get('name', ''),
                'id': select.get('id', ''),
                'class': select.get('class', [])
            }
            
            if any('size' in str(attr).lower() for attr in select_attrs.values()):
                options = select.find_all('option')
                print(f"   尺码下拉框找到 {len(options)} 个选项")
                for option in options:
                    option_text = option.get_text(strip=True)
                    if option_text and option_text not in ['Choose size', 'Select size', '选择尺码']:
                        size_options.append(option_text)
        
        # 4. 在JavaScript中查找尺码数据
        print(f"\n🔍 在JavaScript中搜索尺码数据...")
        script_tags = soup.find_all('script')
        
        js_sizes = []
        for script in script_tags:
            if script.string:
                # 查找包含尺码的JSON数据
                size_patterns = [
                    r'"sizes?":\s*\[([^\]]+)\]',
                    r'"availableSizes?":\s*\[([^\]]+)\]',
                    r'"sizeOptions?":\s*\[([^\]]+)\]',
                    r'"size":\s*"([^"]+)"',
                ]
                
                for pattern in size_patterns:
                    matches = re.findall(pattern, script.string, re.IGNORECASE)
                    for match in matches:
                        # 尝试解析尺码
                        try:
                            if '[' in match or '{' in match:
                                # 可能是JSON数组
                                sizes_data = json.loads(f'[{match}]')
                                for size_item in sizes_data:
                                    if isinstance(size_item, dict):
                                        size_val = size_item.get('size', size_item.get('value', ''))
                                    else:
                                        size_val = str(size_item)
                                    if size_val and size_val not in js_sizes:
                                        js_sizes.append(size_val)
                            else:
                                # 单个尺码值
                                if match and match not in js_sizes:
                                    js_sizes.append(match)
                        except:
                            continue
        
        print(f"📊 在JavaScript中找到 {len(js_sizes)} 个尺码: {js_sizes[:10]}")
        
        # 5. 查找所有包含数字的短文本元素（可能是尺码）
        print(f"\n🔍 搜索可能的尺码文本...")
        all_elements = soup.find_all(text=re.compile(r'^\d+\.?5?$'))
        numeric_texts = []
        for element in all_elements:
            text = element.strip()
            if text and len(text) <= 5:  # 尺码通常很短
                parent = element.parent
                if parent and parent.name in ['button', 'span', 'div', 'li', 'option']:
                    numeric_texts.append({
                        'text': text,
                        'parent_tag': parent.name,
                        'parent_class': parent.get('class', []),
                        'parent_id': parent.get('id', '')
                    })
        
        print(f"📊 找到 {len(numeric_texts)} 个数字文本:")
        for item in numeric_texts[:10]:
            print(f"   '{item['text']}' in <{item['parent_tag']}> class={item['parent_class']}")
        
        # 汇总所有找到的尺码
        all_sizes = []
        
        # 从按钮获取
        for btn in potential_size_buttons:
            if btn['text'] not in all_sizes:
                all_sizes.append(btn['text'])
        
        # 从下拉框获取
        for size in size_options:
            if size not in all_sizes:
                all_sizes.append(size)
        
        # 从JavaScript获取
        for size in js_sizes:
            if str(size) not in all_sizes:
                all_sizes.append(str(size))
        
        # 从数字文本获取
        for item in numeric_texts:
            if item['text'] not in all_sizes:
                all_sizes.append(item['text'])
        
        print(f"\n🎯 最终找到的所有尺码 ({len(all_sizes)} 个):")
        for i, size in enumerate(all_sizes[:20], 1):
            print(f"  {i}. {size}")
        
        return {
            'total_sizes': len(all_sizes),
            'sizes': all_sizes,
            'button_sizes': [btn['text'] for btn in potential_size_buttons],
            'select_sizes': size_options,
            'js_sizes': js_sizes,
            'numeric_texts': [item['text'] for item in numeric_texts]
        }
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        return {}

def main():
    """主函数"""
    url = "https://us.puma.com/us/en/pd/evospeed-mid-distance-nitro-elite-3-track--field-distance-spikes/312637?swatch=01"
    
    result = analyze_sizes(url)
    
    if result:
        # 保存分析结果
        with open('size_analysis_result.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 尺码分析结果已保存到: size_analysis_result.json")

if __name__ == "__main__":
    main()