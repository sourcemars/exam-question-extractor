"""调试智谱AI请求 - 打印实际发送的消息"""

import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dotenv import load_dotenv
load_dotenv()

from src.llm import Message, MessageRole
from src.extractors import QuestionExtractor

# 创建提取器
extractor = QuestionExtractor()

# 模拟页面图片路径
image_path = "data/images/questions/pages/c61b7521_page_1.png"

if not os.path.exists(image_path):
    print(f"错误：图片不存在 - {image_path}")
    sys.exit(1)

# 构建与实际相同的消息
page_num = 1
prompt = extractor._build_page_vision_prompt(page_num)

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

print("=" * 60)
print("调试智谱AI请求")
print("=" * 60)

# 转换消息（模拟zhipu provider的转换）
zhipu_messages = extractor.llm._convert_messages(messages)

print(f"\n转换后的消息数量: {len(zhipu_messages)}")
print("\n消息详情:")
for i, msg in enumerate(zhipu_messages, 1):
    print(f"\n消息 {i}:")
    print(f"  角色: {msg['role']}")

    if isinstance(msg['content'], str):
        print(f"  内容类型: 纯文本")
        print(f"  文本长度: {len(msg['content'])} 字符")
        print(f"  文本预览: {msg['content'][:200]}...")
    elif isinstance(msg['content'], list):
        print(f"  内容类型: 数组（{len(msg['content'])} 项）")
        for j, item in enumerate(msg['content'], 1):
            if item['type'] == 'text':
                print(f"    项 {j}: 文本 ({len(item['text'])} 字符)")
                print(f"      预览: {item['text'][:150]}...")
            elif item['type'] == 'image_url':
                base64_len = len(item['image_url']['url'])
                print(f"    项 {j}: 图片 (base64长度: {base64_len})")
                print(f"      格式: {'纯base64' if not item['image_url']['url'].startswith('data:') else 'data URI'}")

print("\n" + "=" * 60)
print("尝试调用API...")
print("=" * 60)

try:
    response = extractor.llm.chat(messages, temperature=0.3, max_tokens=8192)
    print("\n✓ API调用成功！")
    print(f"\n响应长度: {len(response.content)} 字符")
    print(f"Token使用: {response.usage}")
except Exception as e:
    print(f"\n✗ API调用失败: {e}")
    print("\n这证明问题在于消息格式或参数")
