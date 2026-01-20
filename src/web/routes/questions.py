"""题目路由"""

from flask import Blueprint, render_template, request, current_app, abort
from src.models.database import Question, QuestionOption, QuestionTag, Tag

questions_bp = Blueprint('questions', __name__)

# 题型映射
QUESTION_TYPE_MAP = {
    'single_choice': '单选题',
    'multiple_choice': '多选题',
    'true_false': '判断题',
}

# 难度映射
DIFFICULTY_MAP = {
    'easy': '简单',
    'medium': '中等',
    'hard': '困难',
}

# 难度颜色映射
DIFFICULTY_COLOR_MAP = {
    'easy': 'green',
    'medium': 'yellow',
    'hard': 'red',
}


@questions_bp.route('/')
def index():
    """题目列表页"""
    session = current_app.db_session

    # 获取筛选参数
    question_type = request.args.get('type', '')
    difficulty = request.args.get('difficulty', '')
    has_image = request.args.get('has_image', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    # 构建查询
    query = session.query(Question)

    if question_type:
        query = query.filter(Question.question_type == question_type)
    if difficulty:
        query = query.filter(Question.difficulty == difficulty)
    if has_image == '1':
        query = query.filter(Question.has_image == True)
    elif has_image == '0':
        query = query.filter(Question.has_image == False)

    # 获取总数
    total = query.count()

    # 分页
    questions = query.order_by(Question.id.asc()).offset((page - 1) * per_page).limit(per_page).all()

    # 计算总页数
    total_pages = (total + per_page - 1) // per_page

    # 获取所有题型和难度用于筛选
    question_types = session.query(Question.question_type).distinct().all()
    question_types = [t[0] for t in question_types if t[0]]

    difficulties = session.query(Question.difficulty).distinct().all()
    difficulties = [d[0] for d in difficulties if d[0]]

    return render_template('index.html',
                         questions=questions,
                         page=page,
                         per_page=per_page,
                         total=total,
                         total_pages=total_pages,
                         question_type=question_type,
                         difficulty=difficulty,
                         has_image=has_image,
                         question_types=question_types,
                         difficulties=difficulties,
                         type_map=QUESTION_TYPE_MAP,
                         difficulty_map=DIFFICULTY_MAP,
                         difficulty_color_map=DIFFICULTY_COLOR_MAP)


@questions_bp.route('/question/<int:question_id>')
def question_detail(question_id):
    """题目详情页"""
    session = current_app.db_session

    # 获取题目
    question = session.query(Question).filter(Question.id == question_id).first()
    if not question:
        abort(404)

    # 获取选项（按option_key排序）
    options = session.query(QuestionOption).filter(
        QuestionOption.question_id == question_id
    ).order_by(QuestionOption.option_key).all()

    # 获取标签
    question_tags = session.query(QuestionTag, Tag).join(
        Tag, QuestionTag.tag_id == Tag.id
    ).filter(QuestionTag.question_id == question_id).all()
    tags = [qt[1] for qt in question_tags]

    # 获取上一题和下一题
    prev_question = session.query(Question).filter(Question.id < question_id).order_by(Question.id.desc()).first()
    next_question = session.query(Question).filter(Question.id > question_id).order_by(Question.id.asc()).first()

    return render_template('question_detail.html',
                         question=question,
                         options=options,
                         tags=tags,
                         prev_question=prev_question,
                         next_question=next_question,
                         type_map=QUESTION_TYPE_MAP,
                         difficulty_map=DIFFICULTY_MAP,
                         difficulty_color_map=DIFFICULTY_COLOR_MAP)
