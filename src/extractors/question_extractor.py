"""题目提取器 - 使用LLM提取结构化题目"""

from typing import List, Dict
import json
from src.llm import LLMFactory, Message, MessageRole
from src.config import settings


class QuestionExtractor:
    """基于LLM的题目提取器"""

    def __init__(self):
        """初始化提取器"""
        self.llm = self._create_llm_from_config()
        self.total_cost = 0.0

    def _create_llm_from_config(self):
        """根据配置创建LLM实例"""
        provider = settings.llm_provider

        # 根据provider选择对应的API key
        api_key_map = {
            "claude": settings.claude_api_key,
            "openai": settings.openai_api_key,
            "zhipu": settings.openai_api_key,  # 智谱AI使用OPENAI_API_KEY
        }

        api_key = api_key_map.get(provider)
        if not api_key:
            raise ValueError(f"未配置 {provider} 的API密钥")

        # 额外配置
        extra_config = {}
        if provider == "claude":
            extra_config["default_model"] = settings.claude_model
        elif provider == "openai":
            extra_config["default_model"] = settings.openai_model
            if settings.openai_base_url:
                extra_config["base_url"] = settings.openai_base_url
        elif provider == "zhipu":
            extra_config["default_model"] = settings.openai_model  # 使用OPENAI_MODEL配置

        return LLMFactory.create(provider, api_key, **extra_config)

    def extract_from_text(self, text: str, batch_size: int = 3000) -> List[Dict]:
        """
        从文本提取题目（自动分批处理）

        Args:
            text: PDF提取的文本内容
            batch_size: 每批处理的字符数（默认 3000）

        Returns:
            List[Dict]: 题目列表
        """
        # 如果文本较长，分批处理
        if len(text) > batch_size:
            print(f"  文本较长（{len(text)} 字符），分批处理...")
            return self._extract_in_batches(text, batch_size)

        # 文本较短，直接处理
        return self._extract_single_batch(text)

    def _extract_single_batch(self, text: str) -> List[Dict]:
        """处理单批文本"""
        prompt = self._build_text_extraction_prompt(text)

        messages = [
            Message(
                role=MessageRole.SYSTEM,
                content="你是一个专业的试题解析助手，擅长从文本中提取结构化的题目信息。"
            ),
            Message(
                role=MessageRole.USER,
                content=prompt
            )
        ]

        # 调用LLM
        response = self.llm.chat(messages, temperature=0.3, max_tokens=16000)

        # 记录成本
        cost = self.llm.estimate_cost(response.usage)
        self.total_cost += cost
        print(f"    本次调用成本: ${cost:.4f}, 累计成本: ${self.total_cost:.4f}")
        print(f"    Token使用: {response.usage}")

        # 解析返回的JSON
        questions = self._parse_response(response.content)

        return questions

    def _extract_in_batches(self, text: str, batch_size: int) -> List[Dict]:
        """分批提取题目"""
        all_questions = []

        # 简单分批：按字符数切分
        batches = []
        start = 0
        while start < len(text):
            end = start + batch_size
            # 尝试在段落结束处切分
            if end < len(text):
                # 查找最近的换行符
                newline_pos = text.rfind('\n', start, end)
                if newline_pos > start:
                    end = newline_pos

            batch_text = text[start:end]
            batches.append(batch_text)
            start = end

        print(f"  分为 {len(batches)} 批处理")

        # 逐批处理
        for i, batch_text in enumerate(batches, 1):
            print(f"\n  处理第 {i}/{len(batches)} 批（{len(batch_text)} 字符）...")
            batch_questions = self._extract_single_batch(batch_text)
            all_questions.extend(batch_questions)
            print(f"    提取到 {len(batch_questions)} 道题目")

        return all_questions

    def extract_from_image(self, image_path: str, context: str = "") -> List[Dict]:
        """
        从图片提取题目

        Args:
            image_path: 图片路径
            context: 上下文文本（可选）

        Returns:
            List[Dict]: 题目列表
        """
        if not self.llm.supports_vision():
            raise ValueError(f"{self.llm.__class__.__name__} 不支持视觉输入")

        prompt = self._build_image_extraction_prompt(context)

        messages = [
            Message(
                role=MessageRole.SYSTEM,
                content="你是一个专业的试题解析助手，擅长从图片中识别和提取题目信息。"
            ),
            Message(
                role=MessageRole.USER,
                content=prompt,
                images=[image_path]
            )
        ]

        response = self.llm.chat(messages, temperature=0.3, max_tokens=8000)
        cost = self.llm.estimate_cost(response.usage)
        self.total_cost += cost
        print(f"本次调用成本: ${cost:.4f}, 累计成本: ${self.total_cost:.4f}")

        questions = self._parse_response(response.content)

        return questions

    def extract_from_page_image(self, image_path: str, page_num: int) -> List[Dict]:
        """
        从整页图片提取题目（带图片区域识别）

        Args:
            image_path: 页面图片路径
            page_num: 页码（用于上下文）

        Returns:
            List[Dict]: 题目列表（包含figure_bbox信息）
        """
        if not self.llm.supports_vision():
            model_name = self.llm.get_default_model()
            raise ValueError(
                f"当前模型 '{model_name}' 不支持视觉输入。\n"
                f"请在 .env 文件中切换到支持视觉的模型：\n"
                f"  - 通义千问: qwen-vl-plus 或 qwen-vl-max\n"
                f"  - OpenAI: gpt-4o 或 gpt-4o-mini\n"
                f"  - 智谱AI: glm-4v"
            )

        prompt = self._build_page_vision_prompt(page_num)

        messages = [
            Message(
                role=MessageRole.SYSTEM,
                content="你是一个专业的试题解析助手，擅长从试卷图片中识别题目和图形区域。"
            ),
            Message(
                role=MessageRole.USER,
                content=prompt,
                images=[image_path]
            )
        ]

        response = self.llm.chat(messages, temperature=0.3, max_tokens=16000)
        cost = self.llm.estimate_cost(response.usage)
        self.total_cost += cost
        print(f"    本次调用成本: ${cost:.4f}, 累计成本: ${self.total_cost:.4f}")
        print(f"    Token使用: {response.usage}")

        questions = self._parse_response(response.content)

        # 为每道题添加页码信息
        for q in questions:
            q['page_number'] = page_num

        return questions

    def _build_text_extraction_prompt(self, text: str) -> str:
        """构建文本提取提示词"""
        return f"""
请从以下文本中提取所有题目信息，按照JSON格式返回：

文本内容：
{text}

返回格式：
{{
    "questions": [
        {{
            "question_text": "题目内容",
            "question_type": "single_choice/multiple_choice",
            "options": [
                {{"key": "A", "text": "选项内容", "is_correct": null}},
                {{"key": "B", "text": "选项内容", "is_correct": null}}
            ],
            "correct_answer": null,
            "explanation": null,
            "tags": {{
                "company": ["企业名称"],
                "question_type": ["文字理解/数字推理/图形推理等"],
                "subject": ["相关学科"],
                "skill": ["具体技能点"]
            }},
            "difficulty": "easy/medium/hard"
        }}
    ]
}}

重要说明：
1. question_type 只能是 "single_choice"（单选）或 "multiple_choice"（多选）
2. **如果文本中提供了答案**：
   - 设置对应选项的 is_correct 为 true（正确）或 false（错误）
   - 设置 correct_answer 为答案（如 "A" 或 "ABC"）
3. **如果文本中没有提供答案**：
   - 所有选项的 is_correct 设为 null（表示未知）
   - correct_answer 设为 null
4. **如果文本中提供了解析**：
   - 设置 explanation 字段
5. **如果文本中没有提供解析**：
   - explanation 设为 null

要求：
1. 准确识别题目边界
2. 正确提取所有选项
3. 根据内容推断合适的标签
4. 评估题目难度
5. 必须返回有效的JSON格式
"""

    def _build_image_extraction_prompt(self, context: str) -> str:
        """构建图片提取提示词"""
        return f"""
请分析图片中的题目内容，提取结构化信息。

{f"上下文：{context}" if context else ""}

返回JSON格式（与文本提取相同）：
- question_type: 只能是 "single_choice" 或 "multiple_choice"
- 如果图片中有答案，设置 is_correct 和 correct_answer
- 如果图片中没有答案，is_correct 和 correct_answer 都设为 null
- 如果图片中有解析，设置 explanation；否则设为 null

注意：
1. 如果图片包含图形、图表，在tags中标记
2. 尽可能提取图片中的所有文字内容
3. 必须返回有效的JSON格式
"""

    def _build_page_vision_prompt(self, page_num: int) -> str:
        """构建整页识别提示词（带图形区域检测）"""
        return f"""
你正在分析第{page_num}页的试卷图片。请识别并提取所有题目。

返回JSON格式：
{{
    "questions": [
        {{
            "question_text": "题目文字内容",
            "question_type": "single_choice/multiple_choice",
            "has_figure": true/false,
            "figure_description": "图形描述（如：流程图、几何图形等）",
            "figure_bbox": [x1, y1, x2, y2],
            "options": [
                {{
                    "key": "A",
                    "text": "选项文字",
                    "has_figure": false,
                    "figure_bbox": null
                }},
                {{
                    "key": "B",
                    "text": "选项文字",
                    "has_figure": true,
                    "figure_bbox": [x1, y1, x2, y2]
                }}
            ],
            "correct_answer": null,
            "explanation": null,
            "tags": {{
                "company": [],
                "question_type": [],
                "subject": [],
                "skill": []
            }},
            "difficulty": "easy/medium/hard"
        }}
    ]
}}

重要说明：
1. **has_figure字段**：仅当题目或选项包含真正的图片（图表、几何图形、流程图等）时设为true。纯文字内容设为false。

2. **figure_bbox坐标**（⚠️ 重要）：
   - 格式：[左上x, 左上y, 右下x, 右下y]
   - **必须使用绝对像素坐标，不要使用归一化坐标！**
   - 从图片左上角(0,0)开始计算
   - 例如：如果图片宽度1600px，高度1200px，图形在图片中间位置(400, 300)到(800, 600)，
     则返回 [400, 300, 800, 600]
   - **不要**返回 [0.25, 0.25, 0.5, 0.5] 这样的归一化坐标
   - **不要**返回 [250, 250, 500, 500] 这样基于1000范围的坐标
   - 如果没有图片，设为null
   - 坐标应尽量精确地框住图形区域，可以留10-20像素的边距

3. **question_type**：只能是 "single_choice"（单选）或 "multiple_choice"（多选）

4. **答案处理**：
   - 如果图片中标注了答案，设置correct_answer
   - 如果没有答案，设为null

5. **选项图片**：如果某个选项本身是一张图片（如图形选择题），为该选项设置has_figure=true和对应的figure_bbox

6. **JSON格式要求（非常重要！）**：
   - 必须返回完整的JSON，包含页面中的所有题目
   - 不要使用注释（// ...）或省略号（...）
   - 不要简化或跳过任何题目
   - 如果页面有9道题目，就返回全部9道，不要只返回部分
   - 确保JSON可以被标准JSON解析器解析

请仔细分析图片，完整提取页面中的所有题目（不要省略）。必须返回完整、有效的JSON格式，包含所有题目，不使用注释或省略符号。
"""

    def _parse_response(self, content: str) -> List[Dict]:
        """解析LLM返回的JSON"""
        try:
            # 尝试提取JSON（有些LLM会在markdown代码块中返回）
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            # 清理JSON：移除注释和不完整的内容
            content = self._clean_json(content.strip())

            data = json.loads(content)
            return data.get("questions", [])
        except Exception as e:
            print(f"解析LLM响应失败: {e}")
            print(f"原始响应: {content[:500]}...")
            return []

    def _clean_json(self, content: str) -> str:
        """清理JSON字符串，移除注释和不完整的内容"""
        import re

        # 逐行处理，移除单行注释
        lines = []
        for line in content.split('\n'):
            # 移除行内注释 //
            if '//' in line:
                line = line.split('//')[0]
            lines.append(line)
        content = '\n'.join(lines)

        # 移除多行注释 /* ... */
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)

        # 如果响应是数组格式（直接返回questions数组），转换为标准格式
        content = content.strip()
        if content.startswith('['):
            # 移除数组中的尾随逗号
            content = re.sub(r',\s*(?=\])', '', content)

            # 如果数组没有正确关闭，尝试修复
            if not content.endswith(']'):
                # 查找最后一个完整的 }
                last_brace = content.rfind('}')
                if last_brace > 0:
                    content = content[:last_brace + 1] + '\n]'

            content = f'{{"questions": {content}}}'

        return content

    def get_total_cost(self) -> float:
        """获取累计成本"""
        return self.total_cost
