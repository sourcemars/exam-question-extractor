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

        return LLMFactory.create(provider, api_key, **extra_config)

    def extract_from_text(self, text: str) -> List[Dict]:
        """
        从文本提取题目

        Args:
            text: PDF提取的文本内容

        Returns:
            List[Dict]: 题目列表
        """
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

        # 调用LLM（无论是什么服务商，接口都一样）
        response = self.llm.chat(messages, temperature=0.3)

        # 记录成本
        cost = self.llm.estimate_cost(response.usage)
        self.total_cost += cost
        print(f"本次调用成本: ${cost:.4f}, 累计成本: ${self.total_cost:.4f}")
        print(f"Token使用: {response.usage}")

        # 解析返回的JSON
        questions = self._parse_response(response.content)

        return questions

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

        response = self.llm.chat(messages, temperature=0.3)
        cost = self.llm.estimate_cost(response.usage)
        self.total_cost += cost
        print(f"本次调用成本: ${cost:.4f}, 累计成本: ${self.total_cost:.4f}")

        questions = self._parse_response(response.content)

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
            "question_type": "single_choice/multiple_choice/true_false",
            "options": [
                {{"key": "A", "text": "选项内容", "is_correct": false}},
                {{"key": "B", "text": "选项内容", "is_correct": true}}
            ],
            "correct_answer": "B",
            "explanation": "解析内容（如果有）",
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

返回JSON格式（同文本提取格式）。

注意：
1. 如果图片包含图形、图表，在tags中标记
2. 尽可能提取图片中的文字内容
3. 必须返回有效的JSON格式
"""

    def _parse_response(self, content: str) -> List[Dict]:
        """解析LLM返回的JSON"""
        try:
            # 尝试提取JSON（有些LLM会在markdown代码块中返回）
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            data = json.loads(content.strip())
            return data.get("questions", [])
        except Exception as e:
            print(f"解析LLM响应失败: {e}")
            print(f"原始响应: {content}")
            return []

    def get_total_cost(self) -> float:
        """获取累计成本"""
        return self.total_cost
