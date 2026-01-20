"""Flask应用工厂"""

import os
from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session


def create_app(database_url: str = None):
    """创建Flask应用"""
    app = Flask(__name__,
                template_folder='templates',
                static_folder='static')

    # 配置
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

    # 数据库配置
    if database_url is None:
        # 自动检测项目根目录下的数据库文件
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        db_candidates = ['exam_questions.db', 'questions.db']
        db_path = None
        for db_name in db_candidates:
            candidate_path = os.path.join(project_root, db_name)
            if os.path.exists(candidate_path):
                db_path = candidate_path
                break
        if db_path is None:
            db_path = os.path.join(project_root, 'exam_questions.db')
        database_url = f"sqlite:///{db_path}"

    app.config['DATABASE_URL'] = database_url

    # 创建数据库会话
    engine = create_engine(database_url, echo=False)
    session_factory = sessionmaker(bind=engine)
    Session = scoped_session(session_factory)

    # 将Session挂载到app上
    app.db_session = Session

    # 注册路由
    from src.web.routes.questions import questions_bp
    app.register_blueprint(questions_bp)

    # 请求结束时清理会话
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        Session.remove()

    return app
