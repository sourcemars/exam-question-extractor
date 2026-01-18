"""初始化数据库"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.models import init_database, get_session, TagCategory
from src.config import settings


def create_initial_tags(session):
    """创建初始标签类别"""
    categories = [
        {
            "name": "company",
            "display_name": "企业",
            "description": "题目来源企业"
        },
        {
            "name": "question_type",
            "display_name": "题型",
            "description": "题目类型分类"
        },
        {
            "name": "subject",
            "display_name": "学科/领域",
            "description": "知识领域分类"
        },
        {
            "name": "skill",
            "display_name": "能力点",
            "description": "考察的具体技能"
        },
        {
            "name": "difficulty",
            "display_name": "难度",
            "description": "题目难度等级"
        }
    ]

    for cat_data in categories:
        # 检查是否已存在
        existing = session.query(TagCategory).filter_by(name=cat_data["name"]).first()
        if not existing:
            category = TagCategory(**cat_data)
            session.add(category)
            print(f"✓ 创建标签类别: {cat_data['display_name']}")
        else:
            print(f"  标签类别已存在: {cat_data['display_name']}")

    session.commit()


def main():
    """主函数"""
    print("初始化数据库")
    print("="*60)
    print(f"数据库URL: {settings.database_url}\n")

    # 创建数据库和表
    engine = init_database(settings.database_url)
    print("✓ 数据库表创建成功\n")

    # 创建初始标签
    session = get_session(engine)
    create_initial_tags(session)

    print("\n" + "="*60)
    print("数据库初始化完成！")


if __name__ == "__main__":
    main()
