"""智谱AI原生SDK适配器"""

import base64
from typing import List, Optional, Dict
from zhipuai import ZhipuAI
from ..base import BaseLLMProvider, Message, LLMResponse, MessageRole


class ZhipuProvider(BaseLLMProvider):
    """智谱AI原生SDK适配器"""

    PRICING = {
        "glm-4v": {
            "input": 0.01,   # ¥0.01/千tokens (约$0.0014)
            "output": 0.03   # ¥0.03/千tokens (约$0.0043)
        },
        "glm-4v-plus": {
            "input": 0.05,
            "output": 0.15
        },
        "glm-4v-flash": {
            "input": 0.0,    # 免费
            "output": 0.0
        }
    }

    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        self.client = ZhipuAI(api_key=api_key)
        self.default_model = kwargs.get("default_model", "glm-4v")

    def chat(
        self,
        messages: List[Message],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> LLMResponse:
        """发送智谱AI API请求"""

        model = model or self.default_model

        # 智谱AI GLM-4V的max_tokens限制（根据官方文档）
        # GLM-4V: 最大输出约4096-8192（保守）
        # GLM-4.6/4.7: 最大输出可达128K
        # 为保险起见，限制在30000以内
        max_limit = 30000
        if max_tokens > max_limit:
            print(f"  ⚠ max_tokens={max_tokens} 超过安全限制，调整为{max_limit}")
            max_tokens = max_limit

        # 转换消息格式
        zhipu_messages = self._convert_messages(messages)

        # 构建API参数（只包含必需参数，避免1210错误）
        api_params = {
            "model": model,
            "messages": zhipu_messages,
        }

        # 只在非默认值时添加可选参数
        if temperature != 0.95:  # GLM-4V默认值是0.95
            api_params["temperature"] = temperature
        # max_tokens: 不传递，使用模型默认值（避免1210错误）
        # GLM-4V默认会自动使用最大可用输出

        # 添加其他kwargs
        api_params.update(kwargs)

        # 调用API
        response = self.client.chat.completions.create(**api_params)

        # 提取响应
        choice = response.choices[0]
        content = choice.message.content

        return LLMResponse(
            content=content,
            model=response.model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            },
            raw_response=response.model_dump() if hasattr(response, 'model_dump') else None
        )

    def _convert_messages(self, messages: List[Message]) -> List[dict]:
        """转换为智谱AI消息格式

        智谱AI的特殊处理：
        1. 不支持SYSTEM角色在多模态对话中
        2. 需要将SYSTEM消息合并到第一条USER消息
        """
        zhipu_messages = []
        system_prompt = None

        # 提取SYSTEM消息
        for msg in messages:
            if msg.role.value == "system":
                system_prompt = msg.content
                break

        # 转换消息
        for msg in messages:
            # 跳过SYSTEM消息（已提取）
            if msg.role.value == "system":
                continue

            role = msg.role.value

            # 如果没有图片，直接使用文本
            if not msg.images:
                # 第一条USER消息需要合并SYSTEM提示
                content = msg.content
                if system_prompt and role == "user" and len(zhipu_messages) == 0:
                    content = f"{system_prompt}\n\n{content}"
                    system_prompt = None  # 只在第一条USER消息中添加

                zhipu_messages.append({
                    "role": role,
                    "content": content
                })
                continue

            # 有图片的情况，使用content数组
            content = []

            # 智谱AI要求：图片必须在文本之前！
            # 先添加图片（智谱AI使用纯base64字符串，不需要data URI前缀）
            for img_path in msg.images:
                img_base64 = self._encode_image(img_path)
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": img_base64  # 纯base64字符串
                    }
                })

            # 后添加文本（第一条USER消息需要合并SYSTEM提示）
            if msg.content:
                text_content = msg.content
                if system_prompt and role == "user" and len(zhipu_messages) == 0:
                    text_content = f"{system_prompt}\n\n{text_content}"
                    system_prompt = None

                content.append({
                    "type": "text",
                    "text": text_content
                })

            zhipu_messages.append({
                "role": role,
                "content": content
            })

        return zhipu_messages

    def _encode_image(self, image_path: str) -> str:
        """编码图片为base64"""
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")

    def supports_vision(self) -> bool:
        """检查模型是否支持视觉输入"""
        model = self.default_model.lower()
        # GLM-4V 系列都支持视觉
        return "glm-4v" in model or "glm4v" in model

    def get_default_model(self) -> str:
        return self.default_model

    def estimate_cost(self, usage: Dict[str, int]) -> float:
        """估算成本（人民币）"""
        model = self.default_model
        pricing = self.PRICING.get(model, self.PRICING["glm-4v"])

        # 智谱AI按千tokens计费
        input_cost = (usage["prompt_tokens"] / 1000) * pricing["input"]
        output_cost = (usage["completion_tokens"] / 1000) * pricing["output"]

        # 返回美元（方便统一显示）
        return (input_cost + output_cost) / 7  # 假设汇率1美元=7人民币
