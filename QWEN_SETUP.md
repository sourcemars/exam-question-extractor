# 通义千问（Qwen）快速配置指南

本指南将帮助您快速配置项目以使用阿里云的通义千问 LLM 服务。

## 为什么选择通义千问？

- ✅ **完全兼容 OpenAI API 格式** - 无需修改代码
- ✅ **国内访问稳定快速** - 针对中国境内优化
- ✅ **价格实惠** - 仅 ¥0.4/百万tokens（输入），约为国际服务的 1/50
- ✅ **支持 Vision** - qwen-vl-plus 模型支持图片识别
- ✅ **长文本支持** - 适合处理 PDF 文档
- ✅ **有免费额度** - 新用户可获得免费测试额度

## 步骤 1: 获取 API 密钥

1. 访问阿里云官网：https://www.aliyun.com
2. 注册/登录阿里云账号
3. 进入 **阿里云百炼** 控制台：https://bailian.console.aliyun.com/
4. 在 **模型广场** 中找到 **通义千问**
5. 开通服务并获取 **API Key**

## 步骤 2: 配置项目

### 方式 A: 修改 .env 文件（推荐）

编辑项目根目录下的 `.env` 文件：

```bash
# ==================== LLM配置 ====================
# 使用 openai provider（通义千问兼容 OpenAI API）
LLM_PROVIDER=openai

# ==================== API密钥 ====================
# 填入你的通义千问 API Key
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxx

# ==================== 通义千问端点和模型 ====================
# 通义千问 API 端点（兼容 OpenAI 格式）
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# 选择模型（根据需求选择）
OPENAI_MODEL=qwen-plus  # 推荐：性价比高

# 其他可选模型：
# OPENAI_MODEL=qwen-vl-plus    # 支持图片识别（Vision）
# OPENAI_MODEL=qwen-max        # 最强性能
# OPENAI_MODEL=qwen-turbo      # 最快速度
```

### 方式 B: 从模板创建（如果还没有 .env 文件）

```bash
# 复制模板文件
cp .env.example .env

# 编辑 .env 文件，取消注释通义千问相关配置
nano .env  # 或使用你喜欢的编辑器
```

## 步骤 3: 安装依赖（如果还没安装）

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

## 步骤 4: 测试连接

运行测试脚本验证配置是否正确：

```bash
python scripts/test_llm.py
```

如果配置正确，你会看到类似以下输出：

```
=== LLM连接测试 ===
当前使用的provider: openai
当前使用的模型: qwen-plus
API端点: https://dashscope.aliyuncs.com/compatible-mode/v1

正在发送测试消息...

✓ 测试成功！
响应内容: 你好！我是通义千问...
使用的模型: qwen-plus
Token使用: 输入=15, 输出=42, 总计=57
估算成本: ¥0.00003
```

## 步骤 5: 开始使用

现在你可以正常使用项目了：

```bash
# 初始化数据库（首次运行）
python scripts/init_database.py

# 处理 PDF 文件
python scripts/process_pdf.py data/pdfs/your_exam.pdf
```

## 模型选择建议

| 模型 | 适用场景 | 价格（每百万tokens） | Vision 支持 |
|------|----------|---------------------|-------------|
| **qwen-turbo** | 简单任务，追求速度 | 输入¥0.3 / 输出¥0.6 | ❌ |
| **qwen-plus** ⭐ | 日常使用，性价比高 | 输入¥0.4 / 输出¥1.2 | ❌ |
| **qwen-max** | 复杂任务，追求质量 | 输入¥4.0 / 输出¥12.0 | ❌ |
| **qwen-vl-plus** | 需要识别图片 | 输入¥0.8 / 输出¥2.0 | ✅ |

### 推荐配置

**处理纯文本题目**（推荐）：
```bash
OPENAI_MODEL=qwen-plus
```

**处理包含图片的题目**：
```bash
OPENAI_MODEL=qwen-vl-plus
```

**大批量处理（成本优先）**：
```bash
OPENAI_MODEL=qwen-turbo
```

## 常见问题

### Q1: 提示 "Invalid API Key"

**解决方法**：
- 检查 API Key 是否正确复制（注意不要有多余空格）
- 确认在阿里云控制台已开通通义千问服务
- 检查 API Key 是否已激活（新创建的 Key 可能需要几分钟生效）

### Q2: 提示连接超时

**解决方法**：
- 检查网络连接
- 确认 `OPENAI_BASE_URL` 设置正确
- 如果在企业网络，检查是否需要配置代理

### Q3: 成本如何控制？

**建议**：
- 使用 `qwen-plus` 或 `qwen-turbo` 进行日常处理
- 项目内置成本追踪，每次处理会显示实际花费
- 通义千问价格远低于国际服务（约 1/50）

### Q4: 如何切换回 Claude 或其他服务？

只需修改 `.env` 文件：

```bash
# 切换到 Claude
LLM_PROVIDER=claude
CLAUDE_API_KEY=your-claude-key

# 切换到 Kimi
LLM_PROVIDER=openai
OPENAI_API_KEY=your-kimi-key
OPENAI_BASE_URL=https://api.moonshot.cn/v1
OPENAI_MODEL=moonshot-v1-8k
```

## 更多资源

- 通义千问官方文档：https://help.aliyun.com/zh/dashscope/
- API 参考：https://help.aliyun.com/zh/dashscope/developer-reference/api-details
- 定价说明：https://help.aliyun.com/zh/dashscope/developer-reference/tongyi-qianwen-metering-and-billing
- 控制台：https://bailian.console.aliyun.com/

## 技术支持

如遇到问题：
1. 查看本文档的常见问题部分
2. 查看项目主 README.md
3. 提交 Issue 到项目仓库

---

**祝使用愉快！** 🎉
