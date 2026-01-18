"""LLM提供商抽象基类"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum


class MessageRole(Enum):
    """消息角色"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class Message:
    """统一的消息格式"""
    role: MessageRole
    content: str
    images: Optional[List[str]] = None  # 图片路径或base64


@dataclass
class LLMResponse:
    """统一的响应格式"""
    content: str
    model: str
    usage: Dict[str, int]  # {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150}
    raw_response: Optional[Dict] = None  # 原始响应，用于调试


class BaseLLMProvider(ABC):
    """LLM提供商抽象基类"""

    def __init__(self, api_key: str, **kwargs):
        """
        初始化LLM提供商

        Args:
            api_key: API密钥
            **kwargs: 额外配置（如base_url、timeout等）
        """
        self.api_key = api_key
        self.config = kwargs

    @abstractmethod
    def chat(
        self,
        messages: List[Message],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> LLMResponse:
        """
        发送聊天请求

        Args:
            messages: 消息列表
            model: 模型名称（如果为None，使用默认模型）
            temperature: 温度参数
            max_tokens: 最大token数
            **kwargs: 其他模型特定参数

        Returns:
            LLMResponse: 统一的响应对象
        """
        pass

    @abstractmethod
    def supports_vision(self) -> bool:
        """是否支持视觉输入"""
        pass

    @abstractmethod
    def get_default_model(self) -> str:
        """获取默认模型名称"""
        pass

    @abstractmethod
    def estimate_cost(self, usage: Dict[str, int]) -> float:
        """
        估算API调用成本（美元）

        Args:
            usage: token使用情况

        Returns:
            float: 成本（美元）
        """
        pass
