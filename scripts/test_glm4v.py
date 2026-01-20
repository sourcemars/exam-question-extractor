"""测试智谱AI GLM-4V连接和bbox识别能力"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dotenv import load_dotenv
load_dotenv()

from src.config import settings
from src.llm import LLMFactory, Message, MessageRole


def test_glm4v_connection():
    """测试GLM-4V基本连接"""
    print("=" * 60)
    print("智谱AI GLM-4V 连接测试")
    print("=" * 60)

    print(f"\n配置信息:")
    print(f"  LLM Provider: {settings.llm_provider}")
    print(f"  API Key: {settings.openai_api_key[:20]}..." if settings.openai_api_key else "  API Key: 未配置")
    print(f"  Base URL: {settings.openai_base_url}")
    print(f"  Model: {settings.openai_model}")

    if not settings.openai_api_key or settings.openai_api_key == "your-zhipu-api-key-here":
        print("\n✗ 错误: 未配置智谱AI API Key")
        print("\n请按以下步骤操作:")
        print("  1. 访问 https://open.bigmodel.cn/ 注册并获取API Key")
        print("  2. 在 .env 文件中设置: OPENAI_API_KEY=你的API密钥")
        print("  3. 确保已设置: OPENAI_BASE_URL=https://open.bigmodel.cn/api/paas/v4")
        print("  4. 确保已设置: OPENAI_MODEL=glm-4v-flash")
        return False

    if not settings.openai_base_url or "bigmodel.cn" not in settings.openai_base_url:
        print("\n✗ 错误: Base URL 配置不正确")
        print("请在 .env 文件中设置: OPENAI_BASE_URL=https://open.bigmodel.cn/api/paas/v4")
        return False

    try:
        # 创建LLM实例
        print("\n正在创建GLM-4V实例...")
        llm = LLMFactory.create(
            "openai",
            settings.openai_api_key,
            base_url=settings.openai_base_url,
            default_model=settings.openai_model
        )

        print(f"✓ 成功创建实例")
        print(f"  默认模型: {llm.get_default_model()}")
        print(f"  支持视觉输入: {llm.supports_vision()}")

        if not llm.supports_vision():
            print(f"\n⚠ 警告: 模型 {settings.openai_model} 不支持视觉输入")
            print("请在 .env 中设置: OPENAI_MODEL=glm-4v-flash 或 glm-4v")
            return False

        # 发送测试消息
        messages = [
            Message(
                role=MessageRole.USER,
                content="你好！请用一句话介绍你自己，并说明你是否支持图片识别和坐标定位。"
            )
        ]

        print("\n正在发送测试消息...")
        response = llm.chat(messages, temperature=0.7, max_tokens=200)

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

        print("\n✓ 智谱AI GLM-4V 配置正确，可以正常使用！")
        return True

    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        print("\n可能的原因:")
        print("  1. API Key 不正确或已过期")
        print("  2. 没有开通智谱AI服务")
        print("  3. Base URL 配置错误")
        print("  4. 网络连接问题")
        print("  5. 模型名称错误（应为 glm-4v-flash 或 glm-4v）")
        print("\n请检查 .env 文件中的配置")
        return False


def test_glm4v_vision():
    """测试GLM-4V视觉能力（如果有测试图片）"""
    print("\n" + "=" * 60)
    print("智谱AI GLM-4V 视觉能力测试")
    print("=" * 60)

    # 检查是否有测试图片
    test_image_paths = [
        "data/images/test.png",
        "data/images/test.jpg",
        "data/images/questions/pages/test_page_1.png"
    ]

    test_image = None
    for path in test_image_paths:
        if os.path.exists(path):
            test_image = path
            break

    if not test_image:
        print("\n⚠ 未找到测试图片，跳过视觉测试")
        print("如需测试视觉能力，请将测试图片放置在以下位置之一:")
        for path in test_image_paths:
            print(f"  - {path}")
        return True

    try:
        print(f"\n使用测试图片: {test_image}")

        llm = LLMFactory.create(
            "openai",
            settings.openai_api_key,
            base_url=settings.openai_base_url,
            default_model=settings.openai_model
        )

        messages = [
            Message(
                role=MessageRole.USER,
                content="请描述这张图片的内容。如果图片中有题目，请识别题目文字。",
                images=[test_image]
            )
        ]

        print("\n正在识别图片...")
        response = llm.chat(messages, temperature=0.3, max_tokens=1000)

        print(f"\n✓ 视觉识别成功！")
        print(f"\n识别结果:")
        print(f"  {'-' * 50}")
        print(f"  {response.content}")
        print(f"  {'-' * 50}")

        cost = llm.estimate_cost(response.usage)
        print(f"\n  Token使用: {response.usage.get('total_tokens', 0)}")
        print(f"  估算成本: ¥{cost * 7:.6f}")

        return True

    except Exception as e:
        print(f"\n✗ 视觉测试失败: {e}")
        return False


if __name__ == "__main__":
    print("\n开始测试智谱AI GLM-4V...\n")

    # 测试1: 基本连接
    connection_ok = test_glm4v_connection()

    if not connection_ok:
        print("\n连接测试失败，请先解决上述问题。")
        sys.exit(1)

    # 测试2: 视觉能力（可选）
    test_glm4v_vision()

    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
    print("\n下一步:")
    print("  1. 确保你的 .env 文件中已正确设置智谱AI API Key")
    print("  2. 运行 Vision 模式处理 PDF:")
    print("     python scripts/process_pdf.py your_file.pdf --vision")
    print("\n")

    sys.exit(0)
