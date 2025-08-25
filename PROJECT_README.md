# PumaCrawler - PUMA商品信息爬虫工具

一个功能强大的PUMA商品信息爬虫工具，支持多种爬取方法和完整的数据获取。

## 📁 项目目录结构

```
PumaCrawler/
│
├── 📂 src/                     # 源代码目录
│   ├── 🐍 config.py           # 项目配置文件
│   ├── 🐍 main.py             # 基础版本入口
│   ├── 🐍 puma_crawler.py     # 主爬虫程序（推荐）
│   ├── 🐍 complete_graphql_api.py  # 完整GraphQL API版本
│   ├── 🐍 puma_graphql_scraper.py  # GraphQL API爬虫
│   ├── 🐍 enhanced_puma_scraper.py # 增强版爬虫
│   ├── 🐍 puma_scraper.py      # 基础requests爬虫
│   └── 🐍 其他辅助工具...
│
├── 📂 data/                    # 数据目录
│   ├── 📂 outputs/            # JSON输出文件
│   └── 📂 logs/               # 日志文件
│
├── 📂 tests/                   # 测试文件
├── 📂 docs/                    # 文档目录
├── 📄 requirements.txt         # 项目依赖
└── 📄 README.md               # 项目说明
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 基本使用

```bash
# 进入源码目录
cd src

# 使用自动模式（推荐）
python puma_crawler.py --url "https://us.puma.com/us/en/pd/product-name/123456" --verbose

# 使用完整GraphQL API（获取最详细数据）
python puma_crawler.py --url "商品URL" --method complete_graphql --verbose

# 指定输出文件
python puma_crawler.py --url "商品URL" --output my_product.json --verbose
```

## 🔧 爬取方法

| 方法 | 描述 | 数据完整度 | 推荐指数 |
|------|------|-----------|----------|
| `complete_graphql` | 完整GraphQL API | ⭐⭐⭐⭐⭐ | 🌟🌟🌟🌟🌟 |
| `graphql` | 标准GraphQL API | ⭐⭐⭐⭐ | 🌟🌟🌟🌟 |
| `enhanced` | 增强版requests | ⭐⭐⭐ | 🌟🌟🌟 |
| `requests` | 基础requests | ⭐⭐ | 🌟🌟 |
| `auto` | 自动选择 | ⭐⭐⭐⭐⭐ | 🌟🌟🌟🌟🌟 |

## 📊 数据输出

所有JSON输出文件自动保存到 `data/outputs/` 目录：

- 🕐 文件名包含时间戳：`puma_product_20250825_101142.json`
- 📋 完整的商品信息：名称、价格、描述、尺码、图片等
- 🎨 高质量图片链接（最高2000x2000像素）
- 🧵 详细材料组成信息
- 🏭 制造商信息和产地

## 💡 使用示例

### 单个商品爬取

```bash
# 获取详细商品信息（推荐）
python puma_crawler.py \
  --url "https://us.puma.com/us/en/pd/speedcat-metallic-sneakers-women/405357?swatch=01" \
  --method auto \
  --verbose

# 使用完整API获取最详细数据
python complete_graphql_api.py \
  --url "https://us.puma.com/us/en/pd/speedcat-metallic-sneakers-women/405357?swatch=01" \
  --verbose
```

### 批量爬取

```bash
# 批量处理（需要编辑URL列表）
python batch_scrape.py
```

## 🎯 获取的数据

### 基本信息
- ✅ 商品名称、副标题、头部信息
- ✅ 价格信息（当前价、销售价、促销价、最优价）
- ✅ 商品描述和详细说明
- ✅ 品牌信息（PUMA）
- ✅ 商品ID和款式编号

### 详细信息
- ✅ 颜色名称和颜色值
- ✅ 尺码信息（按性别分类，包含库存状态）
- ✅ 商品图片（高质量链接）
- ✅ 材料组成详细列表
- ✅ 制造商信息和原产地

### 特殊信息
- ✅ 商品徽章和标签
- ✅ 促销信息和折扣
- ✅ 库存状态（售罄、即将到货、预售等）
- ✅ 是否最终销售（不可退货）
- ✅ 评分和评论数量

## 🛠️ 配置选项

### 命令行参数

- `--url, -u`: 商品页面URL（必需）
- `--method, -m`: 爬取方法（可选，默认auto）
- `--output, -o`: 输出文件名（可选）
- `--verbose, -v`: 详细输出模式
- `--validate`: 验证URL有效性

### 输出格式

```json
{
  "name": "Speedcat Metallic",
  "price": "100",
  "description": "商品描述...",
  "color_name": "Metallic Silver",
  "images": ["高质量图片链接..."],
  "material_composition": ["材料成分列表..."],
  "manufacturer_info": {
    "countryOfOrigin": {"content": "Vietnam"},
    "manufacturerAddress": {"content": "制造商地址"}
  },
  "scraped_at": "2025-08-25T10:11:42",
  "method": "complete_graphql_api"
}
```

## 🔍 故障排除

### 常见问题

1. **GraphQL错误**: "Unsupported locale"
   - 🔧 解决方案：使用auto模式，会自动切换到其他方法

2. **网络超时**
   - 🔧 解决方案：检查网络连接，增加 `--verbose` 参数查看详细信息

3. **数据不完整**
   - 🔧 解决方案：尝试 `complete_graphql` 方法获取最完整数据

### 调试模式

```bash
# 启用详细输出查看问题
python puma_crawler.py --url "URL" --verbose

# 验证URL格式
python puma_crawler.py --url "URL" --validate
```

## 📈 性能优化

- 🚀 智能方法选择：auto模式自动选择最佳爬取方法
- 🔄 备用机制：主方法失败时自动切换到备用方案
- ⚡ 高效请求：优化的请求头和会话管理
- 💾 自动保存：结果自动保存到结构化目录

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 📄 许可证

MIT License - 详见LICENSE文件

---

🎉 享受使用PumaCrawler获取PUMA商品数据的便利！