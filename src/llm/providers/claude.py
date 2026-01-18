"""Anthropic Claude适配器"""

import anthropic
import base64
from pathlib import Path
from typing import List, Optional, Dict
from ..base import BaseLLMProvider, Message, LLMResponse, MessageRole


class ClaudeProvider(BaseLLMProvider):
    """Anthropic Claude适配器"""

    # 定价（每百万tokens，美元）
    PRICING = {
        "claude-3-5-sonnet-20241022": {
            "input": 3.0,
            "output": 15.0
        },
        "claude-3-5-haiku-20241022": {
            "input": 1.0,
            "output": 5.0
        }
    }

    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        self.client = anthropic.Anthropic(api_key=api_key)
        self.default_model = kwargs.get("default_model", "claude-3-5-sonnet-20241022")

    def chat(
        self,
        messages: List[Message],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> LLMResponse:
        """发送Claude API请求"""

        model = model or self.default_model

        # 转换消息格式
        claude_messages = self._convert_messages(messages)

        # 提取system消息
        system_message = None
        for msg in messages:
            if msg.role == MessageRole.SYSTEM:
                system_message = msg.content
                break

        # 调用API
        response = self.client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_message,
            messages=claude_messages
        )

        # 转换响应格式
        return LLMResponse(
            content=response.content[0].text,
            model=response.model,
            usage={
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            },
            raw_response=response.model_dump() if hasattr(response, 'model_dump') else None
        )

    def _convert_messages(self, messages: List[Message]) -> List[dict]:
        """转换为Claude消息格式"""
        claude_messages = []

        for msg in messages:
            if msg.role == MessageRole.SYSTEM:
                continue  # system消息单独处理

            content = []

            # 添加文本内容
            if msg.content:
                content.append({
                    "type": "text",
                    "text": msg.content
                })

            # 添加图片
            if msg.images:
                for img_path in msg.images:
                    content.append(self._encode_image(img_path))

            claude_messages.append({
                "role": msg.role.value,
                "content": content
            })

        return claude_messages

    def _encode_image(self, image_path: str) -> dict:
        """编码图片为base64"""
        with open(image_path, "rb") as img_file:
            image_data = base64.standard_b64encode(img_file.read()).decode("utf-8")

        # 检测图片格式
        suffix = Path(image_path).suffix.lower()
        media_type_map = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp"
        }
        media_type = media_type_map.get(suffix, "image/jpeg")

        return {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": media_type,
                "data": image_data
            }
        }

    def supports_vision(self) -> bool:
        return True

    def get_default_model(self) -> str:
        return self.default_model

    def estimate_cost(self, usage: Dict[str, int]) -> float:
        """估算成本"""
        model = self.default_model
        pricing = self.PRICING.get(model, self.PRICING["claude-3-5-sonnet-20241022"])

        input_cost = (usage["prompt_tokens"] / 1_000_000) * pricing["input"]
        output_cost = (usage["completion_tokens"] / 1_000_000) * pricing["output"]

        return input_cost + output_cost
