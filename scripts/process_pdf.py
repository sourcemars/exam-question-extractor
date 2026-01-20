"""处理单个PDF文件 - 完整流程演示"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.parsers import PDFParser
from src.extractors import QuestionExtractor
from src.storage import QuestionSaver
from src.models import init_database, get_session
from src.config import settings
from src.utils import ImageCropper


def process_pdf(pdf_path: str, use_vision: bool = False, force: bool = False):
    """
    处理单个PDF文件

    Args:
        pdf_path: PDF文件路径
        use_vision: 是否使用Vision模式（整页截图识别）
        force: 强制重新处理（删除已有记录）
    """
    if not os.path.exists(pdf_path):
        print(f"错误: 文件不存在 - {pdf_path}")
        return

    print("="*60)
    print(f"处理PDF: {pdf_path}")
    print(f"模式: {'Vision（整页截图识别）' if use_vision else '文本提取'}")
    print("="*60)

    # 1. 解析PDF
    print("\n[1/4] 解析PDF...")
    parser = PDFParser()

    pdf_hash = parser.get_file_hash(pdf_path)
    print(f"  ✓ 文件哈希: {pdf_hash}")

    page_count = parser.get_page_count(pdf_path)
    print(f"  ✓ 页数: {page_count}")

    # 2. 提取题目
    print("\n[2/4] 提取题目...")
    print(f"  使用LLM: {settings.llm_provider}")

    extractor = QuestionExtractor()
    questions = []

    if use_vision:
        # Vision模式：整页截图识别
        print("  渲染页面为图片...")
        page_images = parser.render_all_pages(pdf_path)
        print(f"  ✓ 渲染了 {len(page_images)} 页")

        # 初始化图片裁剪工具
        cropper = ImageCropper()

        # 逐页识别
        for page_info in page_images:
            page_num = page_info['page']
            image_path = page_info['image_path']

            print(f"\n  识别第 {page_num}/{len(page_images)} 页...")
            page_questions = extractor.extract_from_page_image(image_path, page_num)
            print(f"    ✓ 提取到 {len(page_questions)} 道题目")

            # 处理图片裁剪
            for q in page_questions:
                q = cropper.process_question_figures(image_path, q)
                questions.append(q)
    else:
        # 文本模式：提取文本后识别
        text_content = parser.extract_text(pdf_path)
        print(f"  ✓ 提取文本: {len(text_content)} 字符")

        images = parser.extract_images(pdf_path)
        print(f"  ✓ 提取图片: {len(images)} 张")

        if text_content.strip():
            questions = extractor.extract_from_text(text_content)
            print(f"  ✓ 提取到 {len(questions)} 道题目")
        else:
            print("  ⚠ 没有文本内容，跳过提取")

    if not questions:
        print("\n没有提取到题目，处理结束。")
        return

    # 显示提取的题目摘要
    print("\n  题目摘要:")
    for i, q in enumerate(questions[:3], 1):  # 只显示前3道
        q_text = q.get('question_text', '')[:50] if q.get('question_text') else '(无文字)'
        print(f"    {i}. {q_text}...")
        print(f"       类型: {q.get('question_type')}, 难度: {q.get('difficulty')}")
        if q.get('has_figure'):
            print(f"       包含图片: 是")
    if len(questions) > 3:
        print(f"    ... 还有 {len(questions) - 3} 道题目")

    # 3. 保存到数据库
    print("\n[3/4] 保存到数据库...")
    engine = init_database(settings.database_url)
    session = get_session(engine)

    saver = QuestionSaver(session)
    saved_count = saver.save_questions(questions, pdf_path, pdf_hash, force=force)

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
    parser.add_argument('--vision', action='store_true',
                        help='使用Vision模式（整页截图识别，支持图片题目）')
    parser.add_argument('--force', action='store_true',
                        help='强制重新处理（删除已有记录）')

    args = parser.parse_args()

    # 加载环境变量
    from dotenv import load_dotenv
    load_dotenv()

    # 处理PDF
    process_pdf(args.pdf_path, use_vision=args.vision, force=args.force)


if __name__ == "__main__":
    main()
