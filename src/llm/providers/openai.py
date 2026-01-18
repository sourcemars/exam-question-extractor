"""OpenAI GPT适配器"""

import openai
import base64
from typing import List, Optional, Dict
from ..base import BaseLLMProvider, Message, LLMResponse, MessageRole


class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT适配器"""

    PRICING = {
        "gpt-4o": {
            "input": 5.0,
            "output": 15.0
        },
        "gpt-4o-mini": {
            "input": 0.15,
            "output": 0.6
        }
    }

    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url=kwargs.get("base_url")  # 支持自定义base_url
        )
        self.default_model = kwargs.get("default_model", "gpt-4o-mini")

    def chat(
        self,
        messages: List[Message],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> LLMResponse:
        """发送OpenAI API请求"""

        model = model or self.default_model

        # 转换消息格式
        openai_messages = self._convert_messages(messages)

        # 调用API
        response = self.client.chat.completions.create(
            model=model,
            messages=openai_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )

        return LLMResponse(
            content=response.choices[0].message.content,
            model=response.model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            },
            raw_response=response.model_dump() if hasattr(response, 'model_dump') else None
        )

    def _convert_messages(self, messages: List[Message]) -> List[dict]:
        """转换为OpenAI消息格式"""
        openai_messages = []

        for msg in messages:
            content = []

            # 添加文本
            if msg.content:
                content.append({
                    "type": "text",
                    "text": msg.content
                })

            # 添加图片
            if msg.images:
                for img_path in msg.images:
                    content.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{self._encode_image(img_path)}"
                        }
                    })

            # 如果只有文本，直接使用字符串
            if len(content) == 1 and content[0]["type"] == "text":
                content = msg.content

            openai_messages.append({
                "role": msg.role.value,
                "content": content
            })

        return openai_messages

    def _encode_image(self, image_path: str) -> str:
        """编码图片为base64"""
        with open(image_path, "rb") as img_file:
            return base64.standard_b64encode(img_file.read()).decode("utf-8")

    def supports_vision(self) -> bool:
        return "gpt-4" in self.default_model or "gpt-4o" in self.default_model

    def get_default_model(self) -> str:
        return self.default_model

    def estimate_cost(self, usage: Dict[str, int]) -> float:
        model = self.default_model
        pricing = self.PRICING.get(model, self.PRICING["gpt-4o-mini"])

        input_cost = (usage["prompt_tokens"] / 1_000_000) * pricing["input"]
        output_cost = (usage["completion_tokens"] / 1_000_000) * pricing["output"]

        return input_cost + output_cost
