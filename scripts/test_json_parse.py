"""测试JSON解析修复"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.extractors import QuestionExtractor

# 模拟GLM-4V返回的有问题的JSON
test_json = """
[
    {
        "question_text": "微观经济学的中心理论是（）.",
        "question_type": "single_choice",
        "has_figure": false,
        "figure_bbox": null,
        "options": [
            {
                "key": "A",
                "text": "价格理论",
                "has_figure": false,
                "figure_bbox": null
            },
            {
                "key": "B",
                "text": "生产理论",
                "has_figure": false,
                "figure_bbox": null
            },
            {
                "key": "C",
                "text": "市场理论",
                "has_figure": false,
                "figure_bbox": null
            },
            {
                "key": "D",
                "text": "成本理论",
                "has_figure": false,
                "figure_bbox": null
            }
        ],
        "correct_answer": "D",
        "explanation": "根据经济学相关知识，微观经济学的中心理论是成本理论，因为成本理论研究的是如何最小化成本以实现利润最大化。",
        "tags": {
            "company": ["中国南方电网有限责任公司"],
            "question_type": ["single_choice"],
            "subject": ["经济学"],
            "skill": ["中级"]
        },
        "difficulty": "medium"
    },
    // 其他题目...
]
"""

print("=" * 60)
print("测试JSON解析修复")
print("=" * 60)

extractor = QuestionExtractor()

print("\n原始JSON（有问题）:")
print(test_json[:300] + "...")

print("\n尝试解析...")
questions = extractor._parse_response(test_json)

print(f"\n✓ 解析成功！")
print(f"提取到 {len(questions)} 道题目")

if questions:
    print(f"\n第一道题目:")
    print(f"  题目: {questions[0].get('question_text')}")
    print(f"  类型: {questions[0].get('question_type')}")
    print(f"  选项数量: {len(questions[0].get('options', []))}")
    print(f"  正确答案: {questions[0].get('correct_answer')}")
