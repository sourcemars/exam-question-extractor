"""处理单个PDF文件 - 完整流程演示"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.parsers import PDFParser
from src.extractors import QuestionExtractor
from src.storage import QuestionSaver
from src.models import init_database, get_session
from src.config import settings


def process_pdf(pdf_path: str):
    """
    处理单个PDF文件

    Args:
        pdf_path: PDF文件路径
    """
    if not os.path.exists(pdf_path):
        print(f"错误: 文件不存在 - {pdf_path}")
        return

    print("="*60)
    print(f"处理PDF: {pdf_path}")
    print("="*60)

    # 1. 解析PDF
    print("\n[1/4] 解析PDF...")
    parser = PDFParser()

    text_content = parser.extract_text(pdf_path)
    print(f"  ✓ 提取文本: {len(text_content)} 字符")

    images = parser.extract_images(pdf_path)
    print(f"  ✓ 提取图片: {len(images)} 张")

    pdf_hash = parser.get_file_hash(pdf_path)
    print(f"  ✓ 文件哈希: {pdf_hash}")

    # 2. 提取题目
    print("\n[2/4] 提取题目...")
    print(f"  使用LLM: {settings.llm_provider}")

    extractor = QuestionExtractor()

    # 对于MVP，我们只处理文本题目
    if text_content.strip():
        questions = extractor.extract_from_text(text_content)
        print(f"  ✓ 提取到 {len(questions)} 道题目")
    else:
        print("  ⚠ 没有文本内容，跳过提取")
        questions = []

    if not questions:
        print("\n没有提取到题目，处理结束。")
        return

    # 显示提取的题目摘要
    print("\n  题目摘要:")
    for i, q in enumerate(questions[:3], 1):  # 只显示前3道
        print(f"    {i}. {q.get('question_text', '')[:50]}...")
        print(f"       类型: {q.get('question_type')}, 难度: {q.get('difficulty')}")
    if len(questions) > 3:
        print(f"    ... 还有 {len(questions) - 3} 道题目")

    # 3. 保存到数据库
    print("\n[3/4] 保存到数据库...")
    engine = init_database(settings.database_url)
    session = get_session(engine)

    saver = QuestionSaver(session)
    saved_count = saver.save_questions(questions, pdf_path, pdf_hash)

    session.close()

    # 4. 总结
    print("\n[4/4] 处理完成")
    print(f"  ✓ 成功保存: {saved_count} 道题目")
    print(f"  ✓ 累计成本: ${extractor.get_total_cost():.4f}")

    print("\n" + "="*60)
    print("处理成功！")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='处理PDF文件并提取题目')
    parser.add_argument('pdf_path', help='PDF文件路径')

    args = parser.parse_args()

    # 加载环境变量
    from dotenv import load_dotenv
    load_dotenv()

    # 处理PDF
    process_pdf(args.pdf_path)


if __name__ == "__main__":
    main()
