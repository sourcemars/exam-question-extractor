"""查看数据库表结构工具"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dotenv import load_dotenv
load_dotenv()

from src.config import settings
from src.models import init_database, get_session, TagCategory
from sqlalchemy import inspect


def view_database_schema():
    """查看数据库表结构"""
    print("=" * 80)
    print("数据库表结构查看工具")
    print("=" * 80)
    print(f"\n数据库位置: {settings.database_url}\n")

    # 连接数据库
    engine = init_database(settings.database_url)
    inspector = inspect(engine)

    # 获取所有表名
    tables = inspector.get_table_names()
    print(f"共有 {len(tables)} 个表:\n")

    # 遍历每个表
    for table_name in tables:
        print("=" * 80)
        print(f"📊 表名: {table_name}")
        print("=" * 80)

        # 获取列信息
        columns = inspector.get_columns(table_name)
        print("\n字段列表:")
        print(f"{'字段名':<25} {'类型':<20} {'可空':<8} {'默认值':<15} {'主键'}")
        print("-" * 80)

        for col in columns:
            field_name = col['name']
            field_type = str(col['type'])
            nullable = "是" if col['nullable'] else "否"
            default = str(col['default']) if col['default'] else "-"
            primary_key = "✓" if col.get('primary_key', False) else ""

            print(f"{field_name:<25} {field_type:<20} {nullable:<8} {default:<15} {primary_key}")

        # 获取外键信息
        foreign_keys = inspector.get_foreign_keys(table_name)
        if foreign_keys:
            print("\n外键约束:")
            for fk in foreign_keys:
                print(f"  • {fk['constrained_columns']} → {fk['referred_table']}.{fk['referred_columns']}")

        # 获取索引信息
        indexes = inspector.get_indexes(table_name)
        if indexes:
            print("\n索引:")
            for idx in indexes:
                unique = "唯一" if idx['unique'] else "普通"
                print(f"  • [{unique}] {idx['name']}: {idx['column_names']}")

        print()

    # 表关系总结
    print("=" * 80)
    print("📌 表关系总结")
    print("=" * 80)
    print("""
数据模型关系:

1️⃣  PDF源文件 (pdf_sources)
    └─→ 1:N → 题目 (questions)

2️⃣  题目 (questions)
    ├─→ 1:N → 选项 (question_options)
    └─→ N:N → 标签 (tags) [通过 question_tags]

3️⃣  标签分类 (tag_categories)
    └─→ 1:N → 标签 (tags)

4️⃣  关联表 (question_tags)
    ├─→ N:1 → 题目 (questions)
    └─→ N:1 → 标签 (tags)
    """)

    # 统计信息
    session = get_session(engine)
    try:
        print("=" * 80)
        print("📈 数据统计")
        print("=" * 80)

        from src.models import PDFSource, Question, QuestionOption, Tag, QuestionTag

        pdf_count = session.query(PDFSource).count()
        question_count = session.query(Question).count()
        option_count = session.query(QuestionOption).count()
        tag_count = session.query(Tag).count()
        tag_category_count = session.query(TagCategory).count()
        question_tag_count = session.query(QuestionTag).count()

        print(f"\nPDF 文件数: {pdf_count}")
        print(f"题目数: {question_count}")
        print(f"选项数: {option_count}")
        print(f"标签类别数: {tag_category_count}")
        print(f"标签数: {tag_count}")
        print(f"题目-标签关联数: {question_tag_count}")

        # 查看标签类别
        if tag_category_count > 0:
            print("\n已创建的标签类别:")
            categories = session.query(TagCategory).all()
            for cat in categories:
                print(f"  • {cat.display_name} ({cat.name})")

    finally:
        session.close()

    print("\n" + "=" * 80)


if __name__ == "__main__":
    view_database_schema()
