"""测试处理单页"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dotenv import load_dotenv
load_dotenv()

from src.extractors import QuestionExtractor

# 测试第一页
image_path = "data/images/questions/pages/c61b7521_page_1.png"

if not os.path.exists(image_path):
    print(f"错误: 图片不存在 - {image_path}")
    sys.exit(1)

print("=" * 60)
print("测试单页处理")
print("=" * 60)
print(f"\n图片: {image_path}")

extractor = QuestionExtractor()

print("\n开始识别...")
questions = extractor.extract_from_page_image(image_path, 1)

print(f"\n✓ 识别完成！")
print(f"提取到 {len(questions)} 道题目")

if questions:
    print("\n前3道题目:")
    for i, q in enumerate(questions[:3], 1):
        print(f"\n题目 {i}:")
        print(f"  文本: {q.get('question_text', '')[:50]}...")
        print(f"  类型: {q.get('question_type')}")
        print(f"  has_figure: {q.get('has_figure')}")
        if q.get('figure_bbox'):
            print(f"  bbox: {q.get('figure_bbox')}")

print(f"\n成本: ${extractor.get_total_cost():.4f}")
