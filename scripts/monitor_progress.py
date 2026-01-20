"""监控PDF处理进度"""

import sys
import os
import time
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.models import init_database, get_session
from src.config import settings


def get_statistics():
    """获取当前统计信息"""
    stats = {
        'questions': 0,
        'images_original': 0,
        'images_pages': 0,
        'images_cropped': 0
    }

    # 数据库统计
    try:
        from sqlalchemy import text
        engine = init_database(settings.database_url)
        session = get_session(engine)

        result = session.execute(text("SELECT COUNT(*) FROM questions"))
        stats['questions'] = result.scalar()

        session.close()
        engine.dispose()
    except Exception as e:
        pass

    # 图片统计
    image_dirs = {
        'images_original': "data/images/questions",
        'images_pages': "data/images/questions/pages",
        'images_cropped': "src/web/static/images/questions"
    }

    for key, dir_path in image_dirs.items():
        if os.path.exists(dir_path):
            stats[key] = len(list(Path(dir_path).glob("*.*")))

    return stats


def main():
    """主函数"""
    print("\n📊 PDF处理进度监控")
    print("=" * 60)
    print("按 Ctrl+C 退出监控\n")

    try:
        last_stats = None

        while True:
            stats = get_statistics()

            # 显示统计
            print(f"\r当前进度: "
                  f"题目={stats['questions']} | "
                  f"页面图片={stats['images_pages']} | "
                  f"裁剪图片={stats['images_cropped']}",
                  end='', flush=True)

            # 检测是否有变化
            if last_stats and stats == last_stats:
                # 如果5秒无变化，可能已完成
                time.sleep(5)
                new_stats = get_statistics()
                if new_stats == stats:
                    print("\n\n✓ 处理似乎已完成（无新数据）")
                    break

            last_stats = stats
            time.sleep(2)

    except KeyboardInterrupt:
        print("\n\n监控已停止")

    # 显示最终统计
    print("\n" + "=" * 60)
    print("最终统计:")
    final_stats = get_statistics()
    print(f"  题目数量: {final_stats['questions']}")
    print(f"  原始图片: {final_stats['images_original']}")
    print(f"  页面图片: {final_stats['images_pages']}")
    print(f"  裁剪图片: {final_stats['images_cropped']}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
