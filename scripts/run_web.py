#!/usr/bin/env python3
"""启动Web服务器"""

import os
import sys

# 将项目根目录添加到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.web import create_app


def main():
    """启动开发服务器"""
    # 从环境变量获取配置
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5050))
    debug = os.environ.get('FLASK_DEBUG', 'true').lower() == 'true'

    # 数据库路径（自动检测项目根目录下的数据库文件）
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        # 尝试多个可能的数据库文件名
        db_candidates = ['exam_questions.db', 'questions.db']
        db_path = None
        for db_name in db_candidates:
            candidate_path = os.path.join(project_root, db_name)
            if os.path.exists(candidate_path):
                db_path = candidate_path
                break
        if db_path is None:
            db_path = os.path.join(project_root, 'exam_questions.db')
        database_url = f'sqlite:///{db_path}'

    # 检查数据库是否存在
    if database_url.startswith('sqlite:///'):
        db_file = database_url.replace('sqlite:///', '')
        if not os.path.exists(db_file):
            print(f"警告: 数据库文件不存在: {db_file}")
            print("请先运行题目提取程序生成数据库。")
            sys.exit(1)

    # 创建应用
    app = create_app(database_url)

    print(f"题库系统启动中...")
    print(f"访问地址: http://{host if host != '0.0.0.0' else 'localhost'}:{port}")
    print(f"数据库: {database_url}")
    print(f"调试模式: {'开启' if debug else '关闭'}")
    print("-" * 50)

    # 启动服务器
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    main()
