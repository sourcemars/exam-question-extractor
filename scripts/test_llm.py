"""测试LLM抽象层 - 验证不同服务商的切换"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.llm import LLMFactory, Message, MessageRole


def test_llm_provider(provider_name: str, api_key: str, model: str = None):
    """
    测试LLM服务商

    Args:
        provider_name: 服务商名称
        api_key: API密钥
        model: 模型名称（可选）
    """
    print(f"\n{'='*60}")
    print(f"测试 {provider_name.upper()} 提供商")
    print(f"{'='*60}\n")

    try:
        # 创建LLM实例
        extra_config = {}
        if model:
            extra_config["default_model"] = model

        llm = LLMFactory.create(provider_name, api_key, **extra_config)

        print(f"✓ 成功创建 {provider_name} 实例")
        print(f"  默认模型: {llm.get_default_model()}")
        print(f"  支持视觉输入: {llm.supports_vision()}")

        # 测试简单的文本对话
        messages = [
            Message(
                role=MessageRole.USER,
                content="请用一句话介绍你自己。"
            )
        ]

        print("\n发送测试请求...")
        response = llm.chat(messages, temperature=0.7, max_tokens=100)

        print(f"\n✓ 收到响应:")
        print(f"  模型: {response.model}")
        print(f"  Token使用: {response.usage}")
        print(f"  估算成本: ${llm.estimate_cost(response.usage):.6f}")
        print(f"\n  回复内容:\n  {response.content}\n")

        return True

    except Exception as e:
        print(f"\n✗ 测试失败: {e}\n")
        return False


def main():
    """主函数"""
    print("LLM抽象层测试工具")
    print("="*60)

    # 测试Claude（如果配置了）
    claude_key = os.getenv("CLAUDE_API_KEY")
    if claude_key:
        test_llm_provider("claude", claude_key, "claude-3-5-sonnet-20241022")
    else:
        print("\n⚠ 未配置CLAUDE_API_KEY，跳过Claude测试")

    # 测试OpenAI（如果配置了）
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        test_llm_provider("openai", openai_key, "gpt-4o-mini")
    else:
        print("\n⚠ 未配置OPENAI_API_KEY，跳过OpenAI测试")

    print("\n" + "="*60)
    print("测试完成！")
    print("\n提示：通过修改.env文件中的LLM_PROVIDER可以切换服务商")


if __name__ == "__main__":
    # 加载环境变量
    from dotenv import load_dotenv
    load_dotenv()

    main()
