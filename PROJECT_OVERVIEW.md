# 项目概览 - MVP版本

## 项目信息

- **项目名称**: 企业笔试题提取系统
- **版本**: MVP 0.1.0
- **创建日期**: 2026-01-12
- **状态**: 可验证的最小可行产品

## 核心功能

### 1. LLM抽象层（核心特性）

**设计目标**: 支持灵活切换不同的LLM服务商，无需修改业务代码

**实现方式**:
- 抽象基类: `src/llm/base.py`
- 适配器模式: 每个LLM服务商一个适配器
- 工厂模式: `src/llm/factory.py` 统一创建实例

**支持的服务商**:
- Claude (Anthropic)
- OpenAI (GPT)
- 可扩展到其他服务商

**切换方式**:
```bash
# 仅需修改配置文件
LLM_PROVIDER=claude  # 或 openai
```

### 2. PDF解析

**位置**: `src/parsers/pdf_parser.py`

**功能**:
- 提取PDF文本内容
- 提取PDF中的图片
- 计算文件哈希（避免重复处理）
- 获取页数信息

**依赖**: PyMuPDF (fitz)

### 3. 题目提取

**位置**: `src/extractors/question_extractor.py`

**功能**:
- 使用LLM智能识别题目结构
- 提取题目文本、选项、答案
- 自动生成多维度标签
- 支持文本和图片题目（Vision模型）

**特点**:
- 与具体LLM服务商解耦
- 自动成本追踪
- 支持自定义提示词

### 4. 数据存储

**位置**: `src/models/database.py`, `src/storage/question_saver.py`

**数据库表**:
- pdf_sources: PDF源文件
- questions: 题目
- question_options: 选项
- tag_categories: 标签维度
- tags: 标签
- question_tags: 题目-标签关联

**特点**:
- 多维度标签系统
- 支持标签的灵活扩展
- 使用SQLAlchemy ORM

## 文件结构

```
exam-question-extractor/
├── README.md                    # 主文档
├── QUICK_VERIFY.md             # 快速验证指南
├── PROJECT_OVERVIEW.md         # 本文件
├── requirements.txt            # Python依赖
├── .env.example               # 环境变量模板
├── .gitignore                 # Git忽略规则
├── quick_start.sh             # 快速启动脚本
│
├── src/                       # 源代码
│   ├── __init__.py
│   ├── config.py             # 配置管理
│   │
│   ├── llm/                  # LLM抽象层（核心）
│   │   ├── __init__.py
│   │   ├── base.py           # 抽象基类
│   │   ├── factory.py        # LLM工厂
│   │   └── providers/        # 服务商适配器
│   │       ├── __init__.py
│   │       ├── claude.py     # Claude适配器
│   │       └── openai.py     # OpenAI适配器
│   │
│   ├── parsers/              # PDF解析
│   │   ├── __init__.py
│   │   └── pdf_parser.py
│   │
│   ├── extractors/           # 题目提取
│   │   ├── __init__.py
│   │   └── question_extractor.py
│   │
│   ├── storage/              # 数据存储
│   │   ├── __init__.py
│   │   └── question_saver.py
│   │
│   └── models/               # 数据库模型
│       ├── __init__.py
│       └── database.py
│
├── scripts/                  # 工具脚本
│   ├── test_llm.py          # 测试LLM连接
│   ├── init_database.py     # 初始化数据库
│   └── process_pdf.py       # 处理PDF文件
│
├── data/                     # 数据目录
│   ├── pdfs/                # PDF文件
│   │   └── sample_questions.txt
│   ├── images/              # 提取的图片
│   │   ├── questions/
│   │   ├── options/
│   │   └── explanations/
│   └── logs/                # 日志文件
│
└── tests/                    # 测试（待完善）
```

## 核心代码统计

| 模块 | 文件数 | 代码行数（估算） |
|------|--------|-----------------|
| LLM抽象层 | 5 | ~500 |
| PDF解析 | 1 | ~120 |
| 题目提取 | 1 | ~150 |
| 数据库 | 2 | ~200 |
| 脚本 | 3 | ~200 |
| **总计** | **12** | **~1170** |

## 依赖项

### 核心依赖
- sqlalchemy: ORM
- pydantic: 数据验证
- python-dotenv: 环境变量管理

### PDF处理
- PyMuPDF: PDF解析
- Pillow: 图片处理

### LLM
- anthropic: Claude API
- openai: OpenAI API

### 工具
- tqdm: 进度条

## 配置说明

### 必需配置

```bash
# 选择LLM服务商
LLM_PROVIDER=claude  # 或 openai

# 对应的API密钥
CLAUDE_API_KEY=your-key
OPENAI_API_KEY=your-key
```

### 可选配置

```bash
# 自定义模型
CLAUDE_MODEL=claude-3-5-sonnet-20241022
OPENAI_MODEL=gpt-4o-mini

# OpenAI兼容端点
OPENAI_BASE_URL=https://api.custom.com/v1

# 数据库（默认SQLite）
DATABASE_URL=sqlite:///./exam_questions.db
```

## 使用流程

```
1. 配置环境
   └─> 安装依赖
   └─> 配置API密钥

2. 初始化数据库
   └─> python scripts/init_database.py

3. 测试LLM连接
   └─> python scripts/test_llm.py

4. 处理PDF
   └─> python scripts/process_pdf.py <pdf_path>

5. 查看数据
   └─> sqlite3 exam_questions.db
```

## MVP验证要点

### ✅ 已实现
- [x] LLM抽象层设计
- [x] 支持2个LLM服务商（Claude、OpenAI）
- [x] 配置驱动的服务商切换
- [x] PDF文本提取
- [x] PDF图片提取
- [x] 题目智能识别
- [x] 多维度标签系统
- [x] 数据库存储
- [x] 成本追踪
- [x] 完整文档

### 🚧 待实现（超出MVP范围）
- [ ] Vision模型图片题目处理（代码框架已有）
- [ ] 批量处理优化
- [ ] 错误重试机制
- [ ] 进度追踪
- [ ] Web界面
- [ ] 数据验证工具
- [ ] 更多LLM服务商
- [ ] 单元测试

## 扩展指南

### 添加新的LLM服务商

1. 在 `src/llm/providers/` 创建新文件
2. 继承 `BaseLLMProvider`
3. 实现必需方法
4. 在工厂中注册

示例：

```python
# src/llm/providers/zhipu.py
from ..base import BaseLLMProvider

class ZhipuProvider(BaseLLMProvider):
    def chat(self, messages, **kwargs):
        # 实现
        pass

    # 实现其他方法...

# 注册
from src.llm.factory import LLMFactory
LLMFactory.register_provider("zhipu", ZhipuProvider)
```

### 自定义提示词

编辑 `src/extractors/question_extractor.py` 中的：
- `_build_text_extraction_prompt()`
- `_build_image_extraction_prompt()`

### 添加新的标签维度

编辑 `scripts/init_database.py`，在 `categories` 列表中添加。

## 技术亮点

1. **解耦设计**: LLM抽象层完全解耦业务逻辑
2. **适配器模式**: 统一接口，易于扩展
3. **配置驱动**: 零代码切换LLM服务商
4. **成本透明**: 实时显示API成本
5. **灵活标签**: 多维度可扩展标签系统

## 已知限制

1. MVP版本仅处理文本题目（图片支持代码已有，需配置Vision模型）
2. 没有批量处理优化
3. 没有错误重试机制
4. 提示词可能需要根据实际PDF格式调整
5. 使用SQLite，大规模数据建议切换PostgreSQL

## 成本参考

处理20000道纯文本题目（估算）：

| 服务商 | 模型 | 估算成本 |
|--------|------|---------|
| Claude | Sonnet | $400-600 |
| Claude | Haiku | $150-250 |
| OpenAI | GPT-4o | $400-600 |
| OpenAI | GPT-4o-mini | $50-100 |

**建议**: 开发调试使用便宜模型，生产环境根据准确率要求选择。

## 下一步建议

1. **短期（1-2周）**:
   - 测试更多真实PDF
   - 优化提示词提高准确率
   - 添加错误处理

2. **中期（3-4周）**:
   - 实现批量处理
   - 添加进度追踪
   - 支持图片题目
   - 添加数据验证工具

3. **长期（2-3个月）**:
   - 开发Web界面
   - 支持更多LLM服务商
   - 实现人工审核流程
   - 性能优化

## 联系方式

如有问题或建议，请通过以下方式反馈：
- 创建GitHub Issue
- 提交Pull Request
- 邮件联系项目维护者

---

**最后更新**: 2026-01-12
**文档版本**: 1.0
