"""PDF解析器"""

import fitz  # PyMuPDF
import hashlib
from pathlib import Path
from typing import List, Dict


class PDFParser:
    """PDF解析器 - 提取文本和图片"""

    def __init__(self, image_output_dir: str = "data/images/questions"):
        """
        初始化PDF解析器

        Args:
            image_output_dir: 图片输出目录
        """
        self.image_output_dir = Path(image_output_dir)
        self.image_output_dir.mkdir(parents=True, exist_ok=True)

    def extract_text(self, pdf_path: str) -> str:
        """
        提取PDF中的所有文本

        Args:
            pdf_path: PDF文件路径

        Returns:
            str: 提取的文本内容
        """
        doc = fitz.open(pdf_path)
        text_content = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            if text.strip():
                text_content.append(f"--- 第{page_num + 1}页 ---\n{text}")

        doc.close()
        return "\n\n".join(text_content)

    def extract_images(self, pdf_path: str) -> List[Dict]:
        """
        提取PDF中的所有图片

        Args:
            pdf_path: PDF文件路径

        Returns:
            List[Dict]: 图片信息列表
        """
        doc = fitz.open(pdf_path)
        images = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            image_list = page.get_images()

            for img_index, img in enumerate(image_list):
                try:
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]

                    # 计算图片哈希（避免重复存储）
                    image_hash = hashlib.md5(image_bytes).hexdigest()
                    image_filename = f"{image_hash}.{image_ext}"
                    image_path = self.image_output_dir / image_filename

                    # 保存图片（如果不存在）
                    if not image_path.exists():
                        with open(image_path, "wb") as img_file:
                            img_file.write(image_bytes)

                    images.append({
                        "path": str(image_path),
                        "page": page_num + 1,
                        "hash": image_hash,
                        "filename": image_filename
                    })
                except Exception as e:
                    print(f"提取图片失败 (页{page_num + 1}, 图{img_index}): {e}")
                    continue

        doc.close()
        return images

    def get_file_hash(self, pdf_path: str) -> str:
        """
        计算PDF文件的MD5哈希

        Args:
            pdf_path: PDF文件路径

        Returns:
            str: 文件MD5哈希值
        """
        with open(pdf_path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()

    def get_page_count(self, pdf_path: str) -> int:
        """
        获取PDF页数

        Args:
            pdf_path: PDF文件路径

        Returns:
            int: 页数
        """
        doc = fitz.open(pdf_path)
        page_count = len(doc)
        doc.close()
        return page_count
