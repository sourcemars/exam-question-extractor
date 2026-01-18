"""测试通义千问连接"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dotenv import load_dotenv
load_dotenv()

from src.config import settings
from src.llm import LLMFactory, Message, MessageRole


def test_qwen():
    """测试通义千问连接"""
    print("=" * 60)
    print("通义千问（Qwen）连接测试")
    print("=" * 60)

    print(f"\n配置信息:")
    print(f"  LLM Provider: {settings.llm_provider}")
    print(f"  API Key: {settings.openai_api_key[:20]}..." if settings.openai_api_key else "  API Key: 未配置")
    print(f"  Base URL: {settings.openai_base_url}")
    print(f"  Model: {settings.openai_model}")

    if not settings.openai_api_key:
        print("\n✗ 错误: 未配置 OPENAI_API_KEY")
        print("请在 .env 文件中设置通义千问的 API Key")
        return False

    if not settings.openai_base_url:
        print("\n✗ 错误: 未配置 OPENAI_BASE_URL")
        print("请在 .env 文件中设置: OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1")
        return False

    try:
        # 创建LLM实例
        print("\n正在创建通义千问实例...")
        llm = LLMFactory.create(
            "openai",
            settings.openai_api_key,
            base_url=settings.openai_base_url,
            default_model=settings.openai_model
        )

        print(f"✓ 成功创建实例")
        print(f"  默认模型: {llm.get_default_model()}")
        print(f"  支持视觉输入: {llm.supports_vision()}")

        # 发送测试消息
        messages = [
            Message(
                role=MessageRole.USER,
                content="你好！请用一句话介绍你自己。"
            )
        ]

        print("\n正在发送测试消息...")
        response = llm.chat(messages, temperature=0.7, max_tokens=100)

        print(f"\n✓ 测试成功！")
        print(f"\n响应信息:")
        print(f"  使用的模型: {response.model}")
        print(f"  Token 使用统计:")
        print(f"    - 输入 tokens: {response.usage.get('prompt_tokens', 0)}")
        print(f"    - 输出 tokens: {response.usage.get('completion_tokens', 0)}")
        print(f"    - 总计 tokens: {response.usage.get('total_tokens', 0)}")

        cost = llm.estimate_cost(response.usage)
        print(f"  估算成本: ¥{cost * 7:.6f} (${cost:.6f})")

        print(f"\n  AI 回复内容:")
        print(f"  {'-' * 50}")
        print(f"  {response.content}")
        print(f"  {'-' * 50}")

        print("\n✓ 通义千问配置正确，可以正常使用！")
        return True

    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        print("\n可能的原因:")
        print("  1. API Key 不正确")
        print("  2. 没有开通通义千问服务")
        print("  3. Base URL 配置错误")
        print("  4. 网络连接问题")
        print("\n请检查 .env 文件中的配置")
        return False


if __name__ == "__main__":
    success = test_qwen()
    sys.exit(0 if success else 1)
