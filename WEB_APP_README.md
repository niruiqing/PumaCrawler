# PUMA商品信息查询Web应用

## 🌟 功能介绍

这是一个基于Flask的Web应用，可以通过网页界面输入PUMA商品页面地址，自动获取并显示详细的商品信息，包括：

- ✅ **基本信息**：商品名称、品牌、商品ID、款式编号等
- ✅ **价格信息**：当前价格、销售价、促销价等
- ✅ **颜色信息**：颜色名称和颜色代码
- ✅ **高清图片**：多张2000x2000像素的商品图片
- ✅ **详细尺码**：所有尺码、可用尺码、缺货尺码信息
- ✅ **材料组成**：详细的材料成分列表
- ✅ **商品描述**：完整的产品描述和特性

## 🚀 启动应用

### 方法1：直接运行
```bash
python app.py
```

### 方法2：通过Flask命令
```bash
set FLASK_APP=app.py
flask run
```

## 📱 使用方法

1. **启动应用**：运行 `python app.py`
2. **打开浏览器**：访问 `http://localhost:5000`
3. **输入URL**：在输入框中粘贴PUMA商品页面地址
4. **点击查询**：点击"查询商品"按钮
5. **查看结果**：系统将自动显示完整的商品信息

## 🔧 技术架构

- **后端框架**：Flask
- **数据获取**：增强版GraphQL API ([working_complete_graphql_api.py](src/working_complete_graphql_api.py))
- **前端技术**：Bootstrap 5 + JavaScript
- **数据格式**：JSON API响应

## 📊 API接口

### POST /api/scrape
获取商品信息的API接口

**请求格式**：
```json
{
    "url": "https://us.puma.com/us/en/pd/product-name/123456"
}
```

**响应格式**：
```json
{
    "success": true,
    "product": {
        "basic_info": {...},
        "price_info": {...},
        "color_info": {...},
        "images": [...],
        "sizes": {...},
        "materials": [...],
        "manufacturer": {...}
    }
}
```

### GET /api/health
健康检查接口

## 🎨 界面特色

- 🎨 **现代化设计**：渐变背景、圆角卡片、阴影效果
- 📱 **响应式布局**：支持手机、平板、桌面设备
- ⚡ **实时加载**：显示加载状态和进度指示
- 🖼️ **图片预览**：点击图片可在新窗口查看高清大图
- 🏷️ **尺码标签**：可用尺码显示为绿色，缺货尺码显示为红色
- ❌ **错误处理**：友好的错误提示信息

## 📋 示例商品URL

可以使用以下示例URL进行测试：

```
https://us.puma.com/us/en/pd/suede-xl-leopard-jr-youth/404299?swatch=02
https://us.puma.com/us/en/pd/speedcat-metallic-sneakers-women/405357?swatch=01
```

## 🔍 故障排除

### 1. 导入错误
如果出现模块导入错误，请确保：
- `working_complete_graphql_api.py` 在 `src/` 目录中
- 已安装所有必要的依赖包

### 2. 网络错误
- 检查网络连接
- 确保能访问PUMA官网
- 检查防火墙设置

### 3. 商品信息获取失败
- 确认URL格式正确
- 检查商品是否存在
- 尝试使用其他商品URL

## 📝 开发说明

### 添加新功能
要添加新的功能，可以：
1. 修改 `app.py` 添加新的API接口
2. 更新 `templates/index.html` 添加前端界面
3. 扩展 `working_complete_graphql_api.py` 增强数据获取能力

### 自定义样式
所有CSS样式都在 `templates/index.html` 的 `<style>` 标签中，可以根据需要进行修改。

## ⚡ 性能优化

- API客户端采用单例模式，减少重复初始化
- 图片懒加载和点击查看大图
- 错误处理和用户友好的提示信息
- 响应式设计适配各种设备

## 🔐 安全考虑

- URL验证确保只处理PUMA官网链接
- 错误信息过滤避免敏感信息泄露
- CSRF保护和安全请求头

享受使用PUMA商品信息查询工具！🎉