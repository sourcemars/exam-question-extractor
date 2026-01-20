"""题目数据保存器"""

from typing import List, Dict
from sqlalchemy.orm import Session
from src.models import PDFSource, Question, QuestionOption, Tag, TagCategory, QuestionTag


class QuestionSaver:
    """题目数据保存器"""

    def __init__(self, session: Session):
        """
        初始化保存器

        Args:
            session: SQLAlchemy会话
        """
        self.session = session

    def save_questions(self, questions: List[Dict], pdf_path: str, pdf_hash: str, force: bool = False) -> int:
        """
        保存题目到数据库

        Args:
            questions: 题目列表
            pdf_path: PDF文件路径
            pdf_hash: PDF文件哈希
            force: 强制重新处理（删除已有记录）

        Returns:
            int: 保存的题目数量
        """
        # 检查PDF是否已经处理过
        pdf_source = self.session.query(PDFSource).filter_by(file_hash=pdf_hash).first()

        if pdf_source:
            if force:
                print(f"强制模式: 删除已有记录并重新处理...")
                self.session.delete(pdf_source)
                self.session.commit()
                pdf_source = None
            else:
                print(f"PDF文件已处理过: {pdf_path}")
                print(f"使用 --force 参数强制重新处理")
                return 0

        # 创建PDF源记录
        pdf_source = PDFSource(
            file_name=pdf_path.split('/')[-1],
            file_path=pdf_path,
            file_hash=pdf_hash,
            process_status='processing',
            total_questions=len(questions)
        )
        self.session.add(pdf_source)
        self.session.flush()  # 获取pdf_source.id

        saved_count = 0

        # 保存每道题目
        for q_data in questions:
            try:
                question = self._create_question(q_data, pdf_source.id)
                self.session.add(question)
                self.session.flush()  # 获取question.id

                # 保存选项
                if 'options' in q_data:
                    for opt in q_data['options']:
                        option = self._create_option(opt, question.id)
                        self.session.add(option)

                # 保存标签
                if 'tags' in q_data:
                    self._save_tags(q_data['tags'], question.id)

                saved_count += 1

            except Exception as e:
                print(f"保存题目失败: {e}")
                self.session.rollback()
                continue

        # 更新PDF源状态
        pdf_source.process_status = 'completed'
        self.session.commit()

        print(f"成功保存 {saved_count}/{len(questions)} 道题目")
        return saved_count

    def _create_question(self, q_data: Dict, pdf_source_id: int) -> Question:
        """创建题目对象"""
        # 检查是否有图片
        has_image = bool(q_data.get('has_figure', False) and q_data.get('question_image_path'))

        # 处理 correct_answer - 可能是字符串或列表
        correct_answer = q_data.get('correct_answer')
        if isinstance(correct_answer, list):
            correct_answer = ''.join(correct_answer)  # ['A', 'B'] -> 'AB'

        return Question(
            pdf_source_id=pdf_source_id,
            question_text=q_data.get('question_text'),
            question_type=q_data.get('question_type'),
            difficulty=q_data.get('difficulty'),
            correct_answer=correct_answer,
            explanation=q_data.get('explanation'),
            has_image=has_image,
            question_image_path=q_data.get('question_image_path'),
            page_number=q_data.get('page_number'),
            extra_metadata=q_data
        )

    def _create_option(self, opt_data: Dict, question_id: int) -> QuestionOption:
        """创建选项对象"""
        # 检查是否有图片
        has_image = bool(opt_data.get('has_figure', False) and opt_data.get('option_image_path'))

        return QuestionOption(
            question_id=question_id,
            option_key=opt_data.get('key'),
            option_text=opt_data.get('text'),
            is_correct=opt_data.get('is_correct'),
            has_image=has_image,
            option_image_path=opt_data.get('option_image_path')
        )

    def _save_tags(self, tags_data: Dict, question_id: int):
        """保存标签"""
        for category_name, tag_names in tags_data.items():
            if not tag_names:
                continue

            # 获取或创建标签类别
            category = self.session.query(TagCategory).filter_by(name=category_name).first()
            if not category:
                category = TagCategory(
                    name=category_name,
                    display_name=category_name
                )
                self.session.add(category)
                self.session.flush()

            # 为每个标签创建关联
            for tag_name in tag_names:
                # 获取或创建标签
                tag = self.session.query(Tag).filter_by(
                    category_id=category.id,
                    name=tag_name
                ).first()

                if not tag:
                    tag = Tag(
                        category_id=category.id,
                        name=tag_name,
                        slug=tag_name.lower().replace(' ', '_')
                    )
                    self.session.add(tag)
                    self.session.flush()

                # 创建题目-标签关联
                question_tag = QuestionTag(
                    question_id=question_id,
                    tag_id=tag.id,
                    confidence=1.0
                )
                self.session.add(question_tag)
