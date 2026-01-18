# 企业笔试题提取系统 (Exam Question Extractor)

一个基于LLM的PDF笔试题提取系统，支持自动识别题目、选项、答案，并进行多维度标签分类。

## 核心特性

- **灵活的LLM抽象层**: 轻松切换不同的LLM服务商（Claude、OpenAI等）
- **智能题目提取**: 自动识别题目、选项、答案和解析
- **多维度标签**: 支持按企业、题型、学科、技能等多维度分类
- **图片支持**: 支持提取和处理PDF中的图片（使用Vision模型）
- **成本追踪**: 实时显示API调用成本

## 项目结构

```
exam-question-extractor/
├── src/
│   ├── llm/                    # LLM抽象层
│   │   ├── base.py            # 抽象基类
│   │   ├── factory.py         # LLM工厂
│   │   └── providers/         # 各服务商适配器
│   │       ├── claude.py
│   │       └── openai.py
│   ├── parsers/               # PDF解析
│   ├── extractors/            # 题目提取
│   ├── storage/               # 数据存储
│   └── models/                # 数据库模型
├── scripts/                   # 工具脚本
├── data/                      # 数据目录
└── tests/                     # 测试
```

## 快速开始

### 1. 安装依赖

```bash
cd exam-question-extractor

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件，填入你的API密钥
# 至少需要配置一个LLM服务商的API密钥
```

`.env` 文件示例：

```bash
# 选择使用的LLM服务商
LLM_PROVIDER=claude  # 或 openai

# API密钥（根据选择的provider填写）
CLAUDE_API_KEY=your-claude-api-key-here
OPENAI_API_KEY=your-openai-api-key-here

# 模型配置（可选）
CLAUDE_MODEL=claude-3-5-sonnet-20241022
OPENAI_MODEL=gpt-4o-mini

# 数据库配置
DATABASE_URL=sqlite:///./exam_questions.db
```

### 3. 初始化数据库

```bash
python scripts/init_database.py
```

### 4. 测试LLM连接

```bash
python scripts/test_llm.py
```

这个脚本会测试你配置的LLM服务商是否能正常工作。

### 5. 处理PDF文件

```bash
# 处理单个PDF
python scripts/process_pdf.py data/pdfs/your_exam.pdf
```

## LLM服务商切换

这是本项目的核心特性 - 你可以轻松切换不同的LLM服务商，而无需修改代码。

### 方式1: 修改配置文件

编辑 `.env` 文件：

```bash
# 从Claude切换到OpenAI
LLM_PROVIDER=openai
```

### 方式2: 在代码中动态切换

```python
from src.llm import LLMFactory, Message, MessageRole

# 使用Claude
claude = LLMFactory.create("claude", api_key="xxx")

# 使用OpenAI
openai = LLMFactory.create("openai", api_key="xxx")

# 接口完全一致
messages = [Message(role=MessageRole.USER, content="你好")]
response1 = claude.chat(messages)
response2 = openai.chat(messages)
```

### 支持的LLM服务商

#### 国际服务
- **Claude** (Anthropic): claude-3-5-sonnet, claude-3-5-haiku
- **OpenAI**: gpt-4o, gpt-4o-mini

#### 国内服务（推荐）

本项目支持所有兼容 OpenAI API 格式的服务商，特别推荐以下国内服务：

**1. 通义千问（阿里云）⭐ 推荐**
- **优势**: 完全兼容 OpenAI API，速度快，价格低（¥0.4/百万tokens输入）
- **支持 Vision**: qwen-vl-plus 模型支持图片识别
- **配置示例**:
  ```bash
  LLM_PROVIDER=openai
  OPENAI_API_KEY=your-qwen-api-key
  OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
  OPENAI_MODEL=qwen-plus  # 或 qwen-vl-plus (支持图片)
  ```

**2. Kimi（月之暗面）**
- **优势**: 超长上下文（128K tokens），适合处理长PDF文档
- **价格**: ¥0.3/百万tokens（输入）
- **配置示例**:
  ```bash
  LLM_PROVIDER=openai
  OPENAI_API_KEY=your-kimi-api-key
  OPENAI_BASE_URL=https://api.moonshot.cn/v1
  OPENAI_MODEL=moonshot-v1-8k  # 或 moonshot-v1-128k
  ```

**3. 智谱AI（GLM-4）**
- **优势**: 清华背景，性能强劲，支持 Vision
- **配置示例**:
  ```bash
  LLM_PROVIDER=openai
  OPENAI_API_KEY=your-zhipu-api-key
  OPENAI_BASE_URL=https://open.bigmodel.cn/api/paas/v4
  OPENAI_MODEL=glm-4  # 或 glm-4v (支持图片)
  ```

详细配置说明请参考 `.env.example` 文件。

### 添加新的LLM服务商

1. 在 `src/llm/providers/` 下创建新的适配器
2. 继承 `BaseLLMProvider` 并实现必需的方法
3. 在 `LLMFactory` 中注册

示例：

```python
from src.llm.base import BaseLLMProvider
from src.llm.factory import LLMFactory

class MyCustomProvider(BaseLLMProvider):
    def chat(self, messages, **kwargs):
        # 实现你的逻辑
        pass

    # 实现其他必需方法...

# 注册
LLMFactory.register_provider("mycustom", MyCustomProvider)
```

## 数据库设计

系统使用多维度标签设计，支持灵活的题目分类：

- **pdf_sources**: PDF源文件
- **questions**: 题目表
- **question_options**: 选项表
- **tag_categories**: 标签维度（企业、题型、学科等）
- **tags**: 具体标签
- **question_tags**: 题目-标签关联

查看完整的数据库Schema: `src/models/database.py`

## 成本估算

不同LLM服务商的定价（参考）：

| 服务商 | 模型 | 输入价格 | 输出价格 |
|--------|------|----------|----------|
| Claude | Sonnet | $3/1M tokens | $15/1M tokens |
| Claude | Haiku | $1/1M tokens | $5/1M tokens |
| OpenAI | GPT-4o | $5/1M tokens | $15/1M tokens |
| OpenAI | GPT-4o-mini | $0.15/1M tokens | $0.6/1M tokens |

处理20000道题的估算成本：$200-800（取决于题目复杂度和选择的模型）

## 使用示例

### 基础使用

```python
from src.parsers import PDFParser
from src.extractors import QuestionExtractor
from src.storage import QuestionSaver
from src.models import init_database, get_session

# 1. 解析PDF
parser = PDFParser()
text = parser.extract_text("exam.pdf")
images = parser.extract_images("exam.pdf")

# 2. 提取题目
extractor = QuestionExtractor()
questions = extractor.extract_from_text(text)

# 3. 保存到数据库
engine = init_database("sqlite:///exam.db")
session = get_session(engine)
saver = QuestionSaver(session)
saver.save_questions(questions, "exam.pdf", parser.get_file_hash("exam.pdf"))
```

### 混合使用多个LLM

```python
from src.llm import LLMFactory

# 简单任务用便宜的模型
cheap_llm = LLMFactory.create("openai", api_key="xxx", default_model="gpt-4o-mini")

# 复杂任务用强大的模型
powerful_llm = LLMFactory.create("claude", api_key="xxx")

# 根据任务复杂度选择
if is_complex_task:
    response = powerful_llm.chat(messages)
else:
    response = cheap_llm.chat(messages)
```

## MVP验证清单

这是一个MVP版本，你可以验证以下功能：

- [ ] 安装依赖成功
- [ ] 配置环境变量
- [ ] 初始化数据库
- [ ] 测试LLM连接（至少一个服务商）
- [ ] 切换不同的LLM服务商
- [ ] 处理示例PDF文件
- [ ] 查看数据库中的数据
- [ ] 验证成本统计

## 下一步开发

MVP验证通过后，可以继续开发：

1. 图片题目支持（Vision API）
2. 批量处理脚本
3. 处理进度追踪
4. 错误重试机制
5. 数据验证和质量检查
6. 人工审核界面
7. 更多LLM服务商支持

## 故障排除

### 问题1: ModuleNotFoundError

确保你在项目根目录下运行脚本：

```bash
cd exam-question-extractor
python scripts/xxx.py
```

### 问题2: API密钥错误

检查 `.env` 文件中的API密钥是否正确，并且对应的 `LLM_PROVIDER` 设置正确。

### 问题3: 数据库错误

删除数据库文件重新初始化：

```bash
rm exam_questions.db
python scripts/init_database.py
```

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！
