"""清理数据库和图片 - 重置系统到初始状态"""

import sys
import os
import shutil
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.models import init_database, Base
from src.config import settings
from sqlalchemy import text


def clean_database():
    """清空数据库所有表"""
    print("=" * 60)
    print("清理数据库")
    print("=" * 60)

    try:
        # 连接数据库
        engine = init_database(settings.database_url)

        # 删除所有表
        print("\n正在删除所有数据表...")
        Base.metadata.drop_all(engine)
        print("  ✓ 所有表已删除")

        # 重新创建表结构
        print("\n正在重新创建表结构...")
        Base.metadata.create_all(engine)
        print("  ✓ 表结构已重建")

        # 验证
        with engine.connect() as conn:
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = [row[0] for row in result]
            print(f"\n  当前表: {', '.join(tables)}")

        engine.dispose()
        print("\n✓ 数据库清理完成！")
        return True

    except Exception as e:
        print(f"\n✗ 数据库清理失败: {e}")
        return False


def clean_images():
    """清理所有题目图片"""
    print("\n" + "=" * 60)
    print("清理图片文件")
    print("=" * 60)

    image_dirs = [
        "data/images/questions",           # PDF提取的原始图片
        "data/images/questions/pages",     # 渲染的PDF页面图片
        "src/web/static/images/questions"  # 裁剪的题目图片
    ]

    total_deleted = 0

    for dir_path in image_dirs:
        if not os.path.exists(dir_path):
            print(f"\n跳过不存在的目录: {dir_path}")
            continue

        print(f"\n清理目录: {dir_path}")

        # 统计文件
        files = list(Path(dir_path).glob("*.*"))
        file_count = len(files)

        if file_count == 0:
            print("  目录为空，无需清理")
            continue

        # 删除文件
        deleted = 0
        for file in files:
            try:
                file.unlink()
                deleted += 1
            except Exception as e:
                print(f"  ✗ 删除失败: {file.name} - {e}")

        total_deleted += deleted
        print(f"  ✓ 删除了 {deleted}/{file_count} 个文件")

    print(f"\n✓ 图片清理完成！共删除 {total_deleted} 个文件")
    return True


def confirm_clean():
    """确认清理操作"""
    print("\n" + "=" * 60)
    print("⚠️  数据清理警告")
    print("=" * 60)
    print("\n此操作将：")
    print("  1. 清空数据库所有题目数据")
    print("  2. 删除所有提取的图片文件")
    print("  3. 删除所有渲染的PDF页面图片")
    print("  4. 删除所有裁剪的题目图片")
    print("\n此操作不可恢复！")
    print("=" * 60)

    # 获取用户确认
    response = input("\n确认执行清理操作？(yes/no): ").strip().lower()

    if response in ['yes', 'y']:
        return True
    else:
        print("\n操作已取消")
        return False


def show_statistics():
    """显示清理前的统计信息"""
    print("\n" + "=" * 60)
    print("当前数据统计")
    print("=" * 60)

    # 数据库统计
    try:
        from src.models import get_session
        engine = init_database(settings.database_url)
        session = get_session(engine)

        from sqlalchemy import text
        result = session.execute(text("SELECT COUNT(*) FROM questions"))
        question_count = result.scalar()

        session.close()
        engine.dispose()

        print(f"\n数据库:")
        print(f"  题目数量: {question_count}")
    except Exception as e:
        print(f"\n数据库: 无法读取 ({e})")

    # 图片统计
    print(f"\n图片文件:")

    image_dirs = {
        "data/images/questions": "PDF提取的原始图片",
        "data/images/questions/pages": "渲染的PDF页面",
        "src/web/static/images/questions": "裁剪的题目图片"
    }

    for dir_path, desc in image_dirs.items():
        if os.path.exists(dir_path):
            file_count = len(list(Path(dir_path).glob("*.*")))
            print(f"  {desc}: {file_count} 个文件")
        else:
            print(f"  {desc}: 目录不存在")

    print("=" * 60)


def main():
    """主函数"""
    print("\n数据清理工具")

    # 显示统计信息
    show_statistics()

    # 确认清理
    if not confirm_clean():
        sys.exit(0)

    # 执行清理
    print("\n开始清理...")

    success = True

    # 1. 清理数据库
    if not clean_database():
        success = False

    # 2. 清理图片
    if not clean_images():
        success = False

    # 完成
    print("\n" + "=" * 60)
    if success:
        print("✓ 所有清理操作完成！")
        print("\n系统已重置到初始状态，可以重新处理PDF了。")
    else:
        print("⚠ 部分清理操作失败，请检查错误信息")
    print("=" * 60 + "\n")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
