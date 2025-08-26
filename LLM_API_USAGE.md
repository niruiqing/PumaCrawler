# 大模型API集成使用说明（腾讯云SDK版）

## 功能概述

本项目已集成腾讯云大模型API功能，可以实现：
1. 通用对话功能
2. 商品信息智能分析
3. 购买建议生成
4. 产品描述优化

## 配置说明

### 1. 获取腾讯云API密钥

访问腾讯云控制台获取API密钥：
- 控制台地址：https://console.cloud.tencent.com/cam/capi
- 创建API密钥（SecretId和SecretKey）
- 获取腾讯云大模型访问权限：https://cloud.tencent.com/document/product/1787

### 2. 配置API密钥

有两种方式配置API密钥：

#### 方法一：环境变量（推荐）
```bash
# Windows
set LKEAP_API_KEY=AKIDyour-actual-secret-id
set LKEAP_SECRET_KEY=your-actual-secret-key

# Linux/Mac
export LKEAP_API_KEY=AKIDyour-actual-secret-id
export LKEAP_SECRET_KEY=your-actual-secret-key
```

#### 方法二：直接修改配置文件
编辑 `llm_config.py` 文件：
```python
LLM_CONFIG = {
    "api_key": "AKIDyour-actual-secret-id",    # 替换为你的实际SecretId
    "secret_key": "your-actual-secret-key",    # 替换为你的实际SecretKey
    "region": "ap-beijing",                    # 腾讯云区域
    "default_model": "hunyuan-lite",           # 可选模型：hunyuan-lite, hunyuan-standard, hunyuan-pro
    // ... 其他配置
}
```

## API接口说明

### 1. 通用对话接口
```
POST /api/llm/chat
```

**请求参数：**
```json
{
  "message": "你的问题"
}
```

**响应示例：**
```json
{
  "success": true,
  "response": "回答内容",
  "model": "hunyuan-lite",
  "timestamp": "2025-08-25T10:00:00"
}
```

### 2. 商品分析接口
```
POST /api/llm/analyze-product
```

**请求参数：**
```json
{
  "product": { /* 商品数据 */ },
  "type": "general"  // 可选: general, description, recommendation
}
```

**响应示例：**
```json
{
  "success": true,
  "analysis": "分析结果",
  "analysis_type": "general",
  "product_name": "商品名称",
  "model": "hunyuan-lite",
  "timestamp": "2025-08-25T10:00:00"
}
```

### 3. 健康检查接口
```
GET /api/health
```

## 使用示例

### Python客户端示例
```python
import requests

# 通用对话
response = requests.post('http://localhost:5000/api/llm/chat', json={
    'message': '请解释RESTful API的设计原则'
})

# 商品分析
response = requests.post('http://localhost:5000/api/llm/analyze-product', json={
    'product': {
        'basic_info': {
            'name': 'PUMA运动鞋',
            'description': '舒适透气'
        },
        'price_info': {
            'price': 599
        }
    },
    'type': 'recommendation'
})
```

### JavaScript前端示例
```javascript
// 通用对话
fetch('/api/llm/chat', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({message: '请解释RESTful API的设计原则'})
})
.then(response => response.json())
.then(data => console.log(data.response));

// 商品分析
fetch('/api/llm/analyze-product', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        product: { /* 商品数据 */ },
        type: 'recommendation'
    })
})
.then(response => response.json())
.then(data => console.log(data.analysis));
```

## 支持的腾讯云大模型

1. **hunyuan-lite** - 轻量级模型，响应速度快，适合简单问答
2. **hunyuan-standard** - 标准模型，平衡性能与效果，适合一般应用
3. **hunyuan-pro** - 专业模型，效果最佳，适合复杂任务

## 功能特点

1. **腾讯云原生支持**：直接使用腾讯云SDK，稳定可靠
2. **多模型支持**：支持腾讯云多种大模型
3. **参数可配置**：温度、最大token数等参数均可配置
4. **错误处理**：完善的错误处理和日志记录
5. **性能优化**：客户端单例模式，避免重复初始化
6. **安全设计**：API密钥保护机制

## 注意事项

1. 请妥善保管API密钥，不要泄露
2. 注意API调用频率限制
3. 大模型响应可能需要几秒到十几秒时间
4. 确保网络连接正常
5. 部分功能需要商品数据结构支持

## 故障排除

### 1. API密钥错误
- 检查SecretId和SecretKey是否正确配置
- 确认API密钥是否有足够权限
- 检查腾讯云账户是否已开通大模型服务

### 2. 网络连接问题
- 检查网络连接
- 确认腾讯云API服务地址是否可达
- 检查防火墙设置

### 3. 模型调用失败
- 检查模型名称是否正确
- 确认账户余额是否充足
- 查看详细错误日志

### 4. SDK初始化失败
- 检查腾讯云SDK是否正确安装
- 确认API密钥格式是否正确
- 检查区域设置是否正确

如遇到其他问题，请查看Flask应用日志获取详细错误信息。