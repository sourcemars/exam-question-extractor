"""图片裁剪工具"""

import hashlib
from pathlib import Path
from typing import List, Optional, Tuple
from PIL import Image


class ImageCropper:
    """图片裁剪工具 - 从页面图片中裁剪题目/选项图片"""

    def __init__(self, output_dir: str = "src/web/static/images/questions"):
        """
        初始化裁剪工具

        Args:
            output_dir: 裁剪图片的输出目录
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def crop_region(
        self,
        source_image: str,
        bbox: List[int],
        padding: int = 10,
        prefix: str = "fig"
    ) -> Optional[str]:
        """
        裁剪图片区域

        Args:
            source_image: 源图片路径
            bbox: 边界框 [x1, y1, x2, y2]
            padding: 边距（像素）
            prefix: 文件名前缀

        Returns:
            str: 保存的图片路径，失败返回None
        """
        try:
            img = Image.open(source_image)
            width, height = img.size

            # 应用边距并确保不超出图片边界
            x1 = max(0, bbox[0] - padding)
            y1 = max(0, bbox[1] - padding)
            x2 = min(width, bbox[2] + padding)
            y2 = min(height, bbox[3] + padding)

            # 裁剪图片
            cropped = img.crop((x1, y1, x2, y2))

            # 使用裁剪内容的MD5哈希作为文件名
            img_bytes = cropped.tobytes()
            content_hash = hashlib.md5(img_bytes).hexdigest()[:12]
            filename = f"{prefix}_{content_hash}.png"
            output_path = self.output_dir / filename

            # 保存图片
            cropped.save(str(output_path), "PNG")
            img.close()

            return str(output_path)

        except Exception as e:
            print(f"裁剪图片失败: {e}")
            return None

    def get_web_path(self, file_path: str) -> str:
        """
        将文件系统路径转换为Web路径

        Args:
            file_path: 文件系统路径

        Returns:
            str: Web访问路径（如 /static/images/questions/fig_xxx.png）
        """
        path = Path(file_path)

        # 查找 static 目录的位置
        parts = path.parts
        try:
            static_index = parts.index("static")
            # 从 static 开始构建Web路径
            web_path = "/" + "/".join(parts[static_index:])
            return web_path
        except ValueError:
            # 如果路径中没有 static，返回文件名
            return f"/static/images/questions/{path.name}"

    def process_question_figures(
        self,
        source_image: str,
        question_data: dict,
        padding: int = 10
    ) -> dict:
        """
        处理题目中的所有图片区域

        Args:
            source_image: 页面图片路径
            question_data: 题目数据（包含figure_bbox等字段）
            padding: 裁剪边距

        Returns:
            dict: 更新后的题目数据（添加了图片路径）
        """
        # 处理题干图片
        if question_data.get('has_figure') and question_data.get('figure_bbox'):
            bbox = question_data['figure_bbox']
            cropped_path = self.crop_region(source_image, bbox, padding, "q")
            if cropped_path:
                question_data['question_image_path'] = self.get_web_path(cropped_path)

        # 处理选项图片
        if 'options' in question_data:
            for option in question_data['options']:
                if option.get('has_figure') and option.get('figure_bbox'):
                    bbox = option['figure_bbox']
                    cropped_path = self.crop_region(source_image, bbox, padding, f"opt_{option.get('key', 'x')}")
                    if cropped_path:
                        option['option_image_path'] = self.get_web_path(cropped_path)

        return question_data
