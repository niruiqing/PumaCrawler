# 🎯 Puma商品URL抓取完整指南

## 基本用法

### 1. 抓取指定URL
```bash
# 最简单的用法 - 抓取指定URL
python puma_crawler.py --url "https://us.puma.com/us/en/pd/product-name/123456"

# 使用短参数
python puma_crawler.py -u "https://us.puma.com/us/en/pd/product-name/123456"
```

### 2. 选择不同的爬取方法
```bash
# 使用增强版方法（推荐获取图片）
python puma_crawler.py --url "URL" --method enhanced

# 使用GraphQL方法（获取最完整数据，包括尺码）
python puma_crawler.py --url "URL" --method graphql

# 使用基础方法
python puma_crawler.py --url "URL" --method requests

# 使用自动模式（默认，智能选择最佳方法）
python puma_crawler.py --url "URL" --method auto
```

### 3. 保存结果到文件
```bash
# 保存到指定文件
python puma_crawler.py --url "URL" --output my_product.json

# 保存并使用详细模式
python puma_crawler.py --url "URL" --output result.json --verbose
```

## 完整参数示例

```bash
# 所有参数的完整示例
python puma_crawler.py \
  --url "https://us.puma.com/us/en/pd/product-name/123456" \
  --method auto \
  --output product_info.json \
  --verbose \
  --validate
```

## 支持的URL格式

Puma商品页面URL通常格式如下：
```
https://us.puma.com/us/en/pd/{product-name}/{product-id}?swatch={color-code}
```

### 示例URL：
```
https://us.puma.com/us/en/pd/evospeed-mid-distance-nitro-elite-3-track--field-distance-spikes/312637?swatch=01
https://us.puma.com/us/en/pd/suede-classic-xxi-sneakers/374915?swatch=11
https://us.puma.com/us/en/pd/rs-x-efekt-sneakers/393573?swatch=01
```

## 不同方法的优势

| 方法 | 优势 | 获取数据 |
|------|------|----------|
| **enhanced** | 🖼️ 最佳图片获取 | 基本信息 + 6张高质量图片 |
| **graphql** | 📊 最完整数据 | 详细尺码 + 材料组成 + 技术规格 |
| **requests** | ⚡ 速度最快 | 基本商品信息 |
| **auto** | 🤖 智能选择 | 自动选择最佳方法获取完整数据 |

## 获取的数据内容

### 基本信息
- ✅ 商品名称、价格、描述
- ✅ 品牌、颜色代码、产品ID
- ✅ 爬取时间和方法

### 图片信息（enhanced/auto方法）
- ✅ 6张高质量商品图片（600x600）
- ✅ 不同角度和视图
- ✅ 官方CDN链接

### 详细信息（graphql/auto方法）
- ✅ 完整尺码信息（男码+女码，含库存状态）
- ✅ 材料组成详情
- ✅ 产品特性和技术规格
- ✅ 产品测量数据（公制/英制）

## 实用脚本

### 快速抓取脚本
```bash
#!/bin/bash
# 保存为 quick_scrape.sh

URL="$1"
OUTPUT="product_$(date +%Y%m%d_%H%M%S).json"

if [ -z "$URL" ]; then
    echo "用法: ./quick_scrape.sh 'https://us.puma.com/us/en/pd/product-name/123456'"
    exit 1
fi

echo "🚀 开始抓取: $URL"
python puma_crawler.py --url "$URL" --method auto --output "$OUTPUT" --verbose

if [ -f "$OUTPUT" ]; then
    echo "✅ 抓取完成，结果保存到: $OUTPUT"
    # 显示基本信息
    python -c "
import json
with open('$OUTPUT', 'r', encoding='utf-8') as f:
    data = json.load(f)
print(f'商品名称: {data.get(\"name\", \"N/A\")}')
print(f'价格: {data.get(\"currency\", \"USD\")} \${data.get(\"price\", \"N/A\")}')
print(f'图片数量: {len(data.get(\"images\", []))} 张')
print(f'尺码数量: {len(data.get(\"sizes\", []))} 个')
"
else
    echo "❌ 抓取失败"
fi
```

### Python批量抓取脚本
```python
# 保存为 batch_scrape.py
import subprocess
import sys
from datetime import datetime

def scrape_urls(urls):
    """批量抓取URL列表"""
    results = []
    
    for i, url in enumerate(urls, 1):
        print(f"\n📦 抓取第 {i}/{len(urls)} 个商品")
        print(f"🔗 URL: {url}")
        
        # 生成输出文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"product_{i}_{timestamp}.json"
        
        # 执行抓取
        cmd = [
            sys.executable, "puma_crawler.py",
            "--url", url,
            "--method", "auto",
            "--output", output_file
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ 成功保存到: {output_file}")
                results.append((url, output_file, True))
            else:
                print(f"❌ 抓取失败: {result.stderr}")
                results.append((url, None, False))
        except Exception as e:
            print(f"❌ 执行出错: {e}")
            results.append((url, None, False))
    
    # 输出摘要
    successful = len([r for r in results if r[2]])
    print(f"\n📊 批量抓取完成:")
    print(f"   总计: {len(urls)} 个")
    print(f"   成功: {successful} 个")
    print(f"   失败: {len(urls) - successful} 个")
    
    return results

# 使用示例
if __name__ == "__main__":
    # 在这里添加你要抓取的URL列表
    urls = [
        "https://us.puma.com/us/en/pd/evospeed-mid-distance-nitro-elite-3-track--field-distance-spikes/312637?swatch=01",
        # 添加更多URL...
    ]
    
    scrape_urls(urls)
```

## 故障排除

### 常见问题

1. **URL格式错误**
   ```bash
   # 错误 ❌
   python puma_crawler.py --url "puma.com/product/123"
   
   # 正确 ✅
   python puma_crawler.py --url "https://us.puma.com/us/en/pd/product-name/123456"
   ```

2. **验证URL有效性**
   ```bash
   python puma_crawler.py --url "URL" --validate
   ```

3. **查看详细错误信息**
   ```bash
   python puma_crawler.py --url "URL" --verbose
   ```

### 性能优化建议

- 🚀 **推荐方法顺序**: `auto` > `enhanced` > `graphql` > `requests`
- 📊 **获取完整数据**: 使用 `auto` 方法
- 🖼️ **仅需图片**: 使用 `enhanced` 方法
- ⚡ **快速抓取**: 使用 `requests` 方法

## 输出文件示例

生成的JSON文件包含以下结构：
```json
{
  "name": "商品名称",
  "price": "190",
  "currency": "USD",
  "description": "商品描述...",
  "images": ["图片URL1", "图片URL2", ...],
  "sizes": ["尺码1", "尺码2", ...],
  "features": ["特性1", "特性2", ...],
  "material_composition": ["材料1", "材料2", ...],
  "scraped_at": "2025-08-22T23:43:31.498114",
  "method": "auto"
}
```

现在你可以轻松抓取任何Puma商品页面的完整信息了！🎉