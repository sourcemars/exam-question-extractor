"""数据库模型"""

from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, Float, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()


class PDFSource(Base):
    """PDF源文件表"""
    __tablename__ = 'pdf_sources'

    id = Column(Integer, primary_key=True)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_hash = Column(String(64), unique=True)
    process_status = Column(String(20), default='pending')  # pending, processing, completed, failed
    total_questions = Column(Integer, default=0)
    extra_metadata = Column(JSON)  # 重命名避免与SQLAlchemy保留字冲突
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    questions = relationship("Question", back_populates="pdf_source", cascade="all, delete-orphan")


class Question(Base):
    """题目表"""
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True)
    pdf_source_id = Column(Integer, ForeignKey('pdf_sources.id'))
    question_text = Column(Text)
    question_image_path = Column(String(500))
    has_image = Column(Boolean, default=False)
    question_type = Column(String(50))  # single_choice, multiple_choice, true_false
    difficulty = Column(String(20))  # easy, medium, hard
    page_number = Column(Integer)
    correct_answer = Column(Text)
    explanation = Column(Text)
    extra_metadata = Column(JSON)  # 重命名避免与SQLAlchemy保留字冲突
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    pdf_source = relationship("PDFSource", back_populates="questions")
    options = relationship("QuestionOption", back_populates="question", cascade="all, delete-orphan")
    tags = relationship("QuestionTag", back_populates="question", cascade="all, delete-orphan")


class QuestionOption(Base):
    """选项表"""
    __tablename__ = 'question_options'

    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey('questions.id'))
    option_key = Column(String(10))  # A, B, C, D
    option_text = Column(Text)
    option_image_path = Column(String(500))
    has_image = Column(Boolean, default=False)
    is_correct = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    question = relationship("Question", back_populates="options")


class TagCategory(Base):
    """标签维度表"""
    __tablename__ = 'tag_categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    display_name = Column(String(100))
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    tags = relationship("Tag", back_populates="category")


class Tag(Base):
    """标签表"""
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey('tag_categories.id'))
    name = Column(String(100), nullable=False)
    slug = Column(String(100))
    description = Column(Text)
    color = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    category = relationship("TagCategory", back_populates="tags")
    question_tags = relationship("QuestionTag", back_populates="tag")


class QuestionTag(Base):
    """题目-标签关联表"""
    __tablename__ = 'question_tags'

    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey('questions.id'))
    tag_id = Column(Integer, ForeignKey('tags.id'))
    confidence = Column(Float)  # AI自动打标签时的置信度
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    question = relationship("Question", back_populates="tags")
    tag = relationship("Tag", back_populates="question_tags")


# 数据库连接和会话管理
def create_db_engine(database_url: str):
    """创建数据库引擎"""
    return create_engine(database_url, echo=False)


def init_database(database_url: str):
    """初始化数据库（创建所有表）"""
    engine = create_db_engine(database_url)
    Base.metadata.create_all(engine)
    return engine


def get_session(engine):
    """获取数据库会话"""
    Session = sessionmaker(bind=engine)
    return Session()
