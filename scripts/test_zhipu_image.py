"""测试智谱AI原生SDK的图片格式"""

import sys
import os
import base64
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dotenv import load_dotenv
load_dotenv()

from zhipuai import ZhipuAI

# 创建客户端
api_key = os.getenv("OPENAI_API_KEY")
client = ZhipuAI(api_key=api_key)

# 查找测试图片
test_image_path = "data/images/questions/pages/c61b7521_page_1.png"

if not os.path.exists(test_image_path):
    print(f"错误：测试图片不存在 - {test_image_path}")
    sys.exit(1)

print(f"使用测试图片: {test_image_path}")

# 读取并编码图片
with open(test_image_path, "rb") as img_file:
    img_base64 = base64.b64encode(img_file.read()).decode("utf-8")

print(f"Base64长度: {len(img_base64)}")

# 尝试方式1: 纯base64
print("\n测试方式1: 纯base64字符串...")
try:
    response = client.chat.completions.create(
        model="glm-4v",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": img_base64  # 纯base64
                        }
                    },
                    {
                        "type": "text",
                        "text": "请描述这张图片的内容"
                    }
                ]
            }
        ]
    )
    print("✓ 方式1成功！")
    print(f"响应: {response.choices[0].message.content[:200]}...")
    sys.exit(0)
except Exception as e:
    print(f"✗ 方式1失败: {e}")

# 尝试方式2: data URI前缀
print("\n测试方式2: 使用data URI前缀...")
try:
    response = client.chat.completions.create(
        model="glm-4v",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{img_base64}"
                        }
                    },
                    {
                        "type": "text",
                        "text": "请描述这张图片的内容"
                    }
                ]
            }
        ]
    )
    print("✓ 方式2成功！")
    print(f"响应: {response.choices[0].message.content[:200]}...")
    sys.exit(0)
except Exception as e:
    print(f"✗ 方式2失败: {e}")

print("\n两种方式都失败了！")
sys.exit(1)
