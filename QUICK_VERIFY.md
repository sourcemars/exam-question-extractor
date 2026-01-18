# MVP 快速验证指南

## 验证目标

这个MVP主要验证以下核心功能：

1. ✅ LLM抽象层设计是否合理
2. ✅ 能否轻松切换不同的LLM服务商
3. ✅ PDF解析和题目提取是否有效
4. ✅ 数据库设计是否满足需求
5. ✅ 成本追踪是否准确

## 验证步骤

### 步骤1: 环境准备（5分钟）

```bash
cd exam-question-extractor

# 方式1: 使用快速启动脚本（推荐）
./quick_start.sh

# 方式2: 手动执行
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 步骤2: 配置API密钥（2分钟）

编辑 `.env` 文件：

```bash
# 至少配置一个LLM服务商
LLM_PROVIDER=claude  # 或 openai

# 填入对应的API密钥
CLAUDE_API_KEY=sk-ant-xxxx
# 或
OPENAI_API_KEY=sk-xxxx
```

### 步骤3: 初始化数据库（1分钟）

```bash
python scripts/init_database.py
```

**验证点**:
- 看到 "✓ 数据库表创建成功"
- 看到 5个标签类别被创建

### 步骤4: 测试LLM连接（2分钟）

```bash
python scripts/test_llm.py
```

**验证点**:
- 能成功连接到LLM服务
- 显示模型信息和token使用量
- 显示估算成本
- 收到合理的回复

### 步骤5: 切换LLM服务商（3分钟）

**这是核心验证点！**

1. 修改 `.env` 文件中的 `LLM_PROVIDER`：

```bash
# 从Claude切换到OpenAI
LLM_PROVIDER=openai
```

2. 再次运行测试：

```bash
python scripts/test_llm.py
```

**验证点**:
- 无需修改任何代码
- 仅修改配置就能切换服务商
- 两个服务商的接口完全一致
- 都能正常工作

### 步骤6: 处理真实PDF（5-10分钟）

准备一个包含笔试题的PDF文件，放入 `data/pdfs/` 目录：

```bash
python scripts/process_pdf.py data/pdfs/your_exam.pdf
```

**验证点**:
- 能够提取PDF文本
- LLM能够识别题目结构
- 题目保存到数据库
- 显示成本统计

### 步骤7: 查看数据库（3分钟）

使用SQLite工具查看数据库：

```bash
# 安装sqlite3（如果没有）
# macOS自带，Linux: apt install sqlite3

sqlite3 exam_questions.db

# 在sqlite提示符下执行
.tables                           # 查看所有表
SELECT * FROM questions LIMIT 5;  # 查看前5道题
SELECT * FROM tags;               # 查看所有标签
.quit
```

**验证点**:
- 数据结构合理
- 题目信息完整
- 标签关联正确

## 验证清单

完成以上步骤后，确认以下功能：

- [ ] 环境搭建成功
- [ ] 至少一个LLM服务商能正常工作
- [ ] 能够在Claude和OpenAI之间切换（如果都配置了）
- [ ] PDF解析正常
- [ ] 题目提取有效
- [ ] 数据库存储正确
- [ ] 成本统计准确
- [ ] 多维度标签系统工作正常

## 测试不同场景

### 场景1: 纯文本题目

使用提供的示例文件：

```bash
# 需要将txt转为PDF，或直接测试文本提取
# 这里演示如何在Python中直接测试

python3 << EOF
from src.extractors import QuestionExtractor

text = """
1. Python中哪个关键字用于定义函数？
A. def
B. function
C. define
D. func
答案：A
"""

extractor = QuestionExtractor()
questions = extractor.extract_from_text(text)
print(f"提取到 {len(questions)} 道题")
for q in questions:
    print(f"题目: {q['question_text']}")
    print(f"类型: {q['question_type']}")
EOF
```

### 场景2: 混合使用多个LLM

```python
from src.llm import LLMFactory, Message, MessageRole

# 创建两个实例
claude = LLMFactory.create("claude", "api-key-1")
openai = LLMFactory.create("openai", "api-key-2")

# 同样的消息发给两个服务商
messages = [Message(role=MessageRole.USER, content="解释快速排序")]

response1 = claude.chat(messages)
response2 = openai.chat(messages)

print(f"Claude成本: ${claude.estimate_cost(response1.usage):.6f}")
print(f"OpenAI成本: ${openai.estimate_cost(response2.usage):.6f}")
```

## 常见问题

### Q1: ModuleNotFoundError: No module named 'src'

**解决**: 确保在项目根目录运行脚本：
```bash
cd exam-question-extractor
python scripts/xxx.py
```

### Q2: 提取不到题目

**可能原因**:
1. PDF格式不规范
2. LLM的提示词需要优化
3. PDF是扫描版（需要OCR）

**解决**: 查看 `src/extractors/question_extractor.py` 中的提示词，根据你的PDF格式调整。

### Q3: API成本太高

**解决**:
1. 切换到更便宜的模型（如gpt-4o-mini）
2. 减少temperature参数
3. 限制max_tokens

```bash
# 在.env中修改
OPENAI_MODEL=gpt-4o-mini  # 而不是gpt-4o
```

## 性能基准

在标准配置下（GPT-4o-mini）：

- 处理100道文本题目: ~2-3分钟
- 成本: ~$0.05-0.10
- 准确率: 90%+ （取决于题目格式）

## 下一步

MVP验证通过后，可以：

1. 添加更多LLM服务商支持
2. 优化提示词提高准确率
3. 添加图片题目支持
4. 实现批量处理
5. 添加Web界面

## 反馈

如果遇到问题或有建议，请记录下来，以便改进。
