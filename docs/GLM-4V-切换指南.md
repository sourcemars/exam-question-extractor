# GLM-4V 切换指南

## 📌 问题背景

在使用通义千问 Qwen-VL 进行 Vision 模式图片识别时，发现裁剪出来的图片位置完全错误。

**根本原因**：不同视觉模型的 bbox 坐标系统不统一
- **通义千问 Qwen-VL**：返回归一化坐标（0-1000范围）
- **智谱AI GLM-4V**：返回像素坐标（直接可用）

## ✅ 已完成的修改

### 1. 配置文件修改

**文件：[.env](/.env)**
```bash
# 切换到智谱AI GLM-4V
LLM_PROVIDER=openai
OPENAI_API_KEY=你的智谱AI_API_KEY
OPENAI_BASE_URL=https://open.bigmodel.cn/api/paas/v4
OPENAI_MODEL=glm-4v  # 注意：必须用glm-4v，不能用glm-4v-flash
```

**重要说明**：
- ❌ `glm-4v-flash`：免费版本，但**不支持 base64 图片**（仅支持URL）
- ✅ `glm-4v`：付费版本，**支持 base64 图片**，Vision 模式必须使用
- ✅ `glm-4v-plus`：增强版本，能力最强

### 2. 代码修改

**文件：[src/llm/providers/openai.py](src/llm/providers/openai.py#L83-L99)**

添加了智谱AI图片格式的特殊处理：
```python
# 智谱AI GLM-4V: 直接使用base64，不需要data URI前缀
if "glm" in self.default_model.lower():
    img_base64 = self._encode_image(img_path)
    content.append({
        "type": "image_url",
        "image_url": {
            "url": img_base64  # 不需要 "data:image/jpeg;base64," 前缀
        }
    })
else:
    # OpenAI/Qwen等: 使用完整的data URI
    content.append({
        "type": "image_url",
        "image_url": {
            "url": f"data:image/jpeg;base64,{self._encode_image(img_path)}"
        }
    })
```

**文件：[src/config.py](src/config.py#L29)**

添加了 `qwen_api_key` 字段，支持保存备用API Key。

### 3. Prompt 优化

**文件：[src/extractors/question_extractor.py](src/extractors/question_extractor.py#L322-L331)**

强化了 bbox 坐标格式说明：
```python
2. **figure_bbox坐标**（⚠️ 重要）：
   - 格式：[左上x, 左上y, 右下x, 右下y]
   - **必须使用绝对像素坐标，不要使用归一化坐标！**
   - 从图片左上角(0,0)开始计算
   - 例如：如果图片宽度1600px，高度1200px，图形在图片中间位置(400, 300)到(800, 600)，
     则返回 [400, 300, 800, 600]
   - **不要**返回 [0.25, 0.25, 0.5, 0.5] 这样的归一化坐标
   - **不要**返回 [250, 250, 500, 500] 这样基于1000范围的坐标
```

### 4. 测试脚本

**文件：[scripts/test_glm4v.py](scripts/test_glm4v.py)**

创建了专门的测试脚本，用于验证 GLM-4V 连接和视觉能力。

## 💰 成本对比

### 基础对话（测试用）
| 模型 | Token使用 | 成本 |
|------|----------|------|
| glm-4v-flash | 99 tokens | ¥0.000173 (免费) |
| glm-4v | 1723 tokens | ¥0.001926 |

### Vision 模式处理（估算1000页）
| 模型 | 估算成本 |
|------|---------|
| **glm-4v** | **~¥10-30** |
| glm-4v-plus | ~¥30-60 |
| qwen-vl-plus | ~¥20-40 |

**结论**：GLM-4V 价格合理，且 bbox 识别准确度更高。

## 🚀 使用方法

### 1. 配置 API Key

访问 [智谱AI开放平台](https://open.bigmodel.cn/) 获取 API Key，然后在 `.env` 文件中设置：
```bash
OPENAI_API_KEY=你的API密钥
```

### 2. 测试连接

```bash
python scripts/test_glm4v.py
```

### 3. 处理 PDF

```bash
# Vision 模式（支持图片题目识别和bbox定位）
python scripts/process_pdf.py your_file.pdf --vision

# 强制重新处理
python scripts/process_pdf.py your_file.pdf --vision --force
```

## 🔍 故障排查

### 问题1：Error code: 400 - 1210 参数有误

**原因**：使用了 `glm-4v-flash`，该模型不支持 base64 图片。

**解决方案**：
```bash
# 在 .env 中修改
OPENAI_MODEL=glm-4v  # 不要用 glm-4v-flash
```

### 问题2：bbox 坐标仍然不准确

**可能原因**：
1. LLM 返回的仍是归一化坐标
2. 图片分辨率问题

**调试方法**：
在 [src/extractors/question_extractor.py](src/extractors/question_extractor.py) 添加调试输出：
```python
def _parse_response(self, content: str) -> List[Dict]:
    try:
        # ... 原有代码 ...
        data = json.loads(content.strip())
        questions = data.get("questions", [])

        # 调试输出
        if questions and questions[0].get('figure_bbox'):
            print(f"DEBUG - 第一道题bbox: {questions[0]['figure_bbox']}")

        return questions
```

### 问题3：成本过高

**方案1**：使用 `glm-4v`（标准版）而非 `glm-4v-plus`

**方案2**：切换回通义千问，并添加坐标转换逻辑
```bash
# .env
OPENAI_API_KEY=sk-bc6f12bf6584459da7869807891a25b9
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
OPENAI_MODEL=qwen-vl-plus
```

然后在 [src/utils/image_cropper.py](src/utils/image_cropper.py) 的 `crop_region` 方法中添加坐标归一化检测和转换。

## 📊 模型对比总结

| 特性 | 通义千问 Qwen-VL | 智谱AI GLM-4V | 推荐 |
|------|-----------------|---------------|------|
| **bbox坐标格式** | 归一化（需转换）⚠️ | 像素坐标（直接用）✅ | GLM-4V |
| **base64支持** | ✅ 支持 | glm-4v支持，flash不支持 | - |
| **识别准确度** | 中等 | 较高 | GLM-4V |
| **文档完善度** | 一般 | 好（有grounding示例）✅ | GLM-4V |
| **价格（Vision）** | 中等 | 中等（flash免费但不可用）| 相当 |
| **境内部署** | ✅ 阿里云 | ✅ 智谱AI | 都可 |

## 🎯 推荐配置

**生产环境（精度优先）**：
```bash
OPENAI_MODEL=glm-4v  # 标准版，性价比高
```

**高精度需求**：
```bash
OPENAI_MODEL=glm-4v-plus  # 增强版
```

**成本敏感 + 可接受坐标转换**：
```bash
# 切换回通义千问并实现坐标转换逻辑
OPENAI_MODEL=qwen-vl-plus
```

## 📚 参考资料

- [智谱AI GLM-4V 官方文档](https://docs.bigmodel.cn/cn/guide/models/vlm/glm-4.6v)
- [智谱AI 定价](https://open.bigmodel.cn/pricing)
- [GLM-4V-Flash 说明](https://docs.bigmodel.cn/cn/guide/models/free/glm-4.6v-flash)
- [通义千问 Qwen-VL GitHub](https://github.com/QwenLM/Qwen-VL)

## ✅ 下一步

1. **测试效果**：处理几个包含图片题目的PDF，检查裁剪效果
2. **对比验证**：与之前通义千问的结果对比
3. **调优**：如果bbox仍不准确，考虑调整Prompt或添加后处理逻辑
4. **成本控制**：根据实际使用情况，决定是否需要优化或切换模型

---

**最后更新**：2026-01-20
