"""LLM工厂类"""

from typing import Optional
from .base import BaseLLMProvider
from .providers.claude import ClaudeProvider
from .providers.openai import OpenAIProvider
from .providers.zhipu import ZhipuProvider


class LLMFactory:
    """LLM工厂类"""

    _providers = {
        "claude": ClaudeProvider,
        "openai": OpenAIProvider,
        "zhipu": ZhipuProvider,  # 智谱AI原生SDK
    }

    @classmethod
    def create(
        cls,
        provider_name: str,
        api_key: str,
        **kwargs
    ) -> BaseLLMProvider:
        """
        创建LLM实例

        Args:
            provider_name: 服务商名称 (claude/openai)
            api_key: API密钥
            **kwargs: 额外配置

        Returns:
            BaseLLMProvider: LLM实例
        """
        provider_class = cls._providers.get(provider_name.lower())

        if not provider_class:
            raise ValueError(
                f"不支持的LLM服务商: {provider_name}. "
                f"支持的服务商: {', '.join(cls._providers.keys())}"
            )

        return provider_class(api_key=api_key, **kwargs)

    @classmethod
    def register_provider(cls, name: str, provider_class: type):
        """
        注册新的LLM服务商

        Args:
            name: 服务商名称
            provider_class: 服务商类（必须继承BaseLLMProvider）
        """
        if not issubclass(provider_class, BaseLLMProvider):
            raise TypeError(f"{provider_class} 必须继承 BaseLLMProvider")

        cls._providers[name.lower()] = provider_class

    @classmethod
    def list_providers(cls) -> list:
        """列出所有支持的服务商"""
        return list(cls._providers.keys())
