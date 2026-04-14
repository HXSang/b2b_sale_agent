import re
import os
import uuid
import logging
from pathlib import Path
from openai import OpenAI
from docling.document_converter import DocumentConverter
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

SECTION_TYPES = {
    "product_intro":    "Giới thiệu sản phẩm, ứng dụng, ưu điểm",
    "how_to_design":    "Quy trình thiết kế, tính toán chọn belt",
    "selection_table":  "Bảng tra cứu thông số, kích thước chuẩn",
    "formula":          "Công thức tính toán kỹ thuật",
    "terms":            "Thuật ngữ, ký hiệu, định nghĩa",
    "precautions":      "Lưu ý lắp đặt, bảo quản, an toàn",
    "product_list":     "Danh sách sản phẩm, mã hàng",
    "other":            "Nội dung khác",
}

class BandoCatalogChunker:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.doc_converter = DocumentConverter()
        self.model = os.getenv("OPENAI_MODEL")

    def extract_markdown(self, pdf_path: str) -> str:
        path = Path(pdf_path)
        result = self.doc_converter.convert(path)
        markdown = result.document.export_to_markdown()
        return markdown

    def split_by_headers(self, markdown: str) -> list[dict]:
        pattern = r'(?=^#{1,3} )'
        raw_sections = re.split(pattern, markdown, flags=re.MULTILINE)

        chunks = []
        for section in raw_sections:
            section = section.strip()
            if len(section) < 50:  
                continue

            lines = section.split('\n')
            title = lines[0].replace('#', '').strip()

            chunks.append({
                "title": title,
                "content": section,
                "char_count": len(section)
            })

        return chunks

    def classify_chunk(self, title: str, content_preview: str) -> dict:
        section_types_str = "\n".join([f"- {k}: {v}" for k, v in SECTION_TYPES.items()])

        prompt = f"""
        Phân tích đoạn nội dung từ catalog kỹ thuật dây đai Bando Japan.

        Tiêu đề section: {title}
        Nội dung (500 ký tự đầu): {content_preview[:500]}

        Hãy trả về JSON với các trường sau:
        - section_type: một trong {list(SECTION_TYPES.keys())}
        - product_type: loại belt nếu có (KPS II, STS, Ceptor-X, V-Belt, Power Ace...), null nếu không có
        - belt_pitch: pitch nếu có (8M, 14M, S8M, H, L...), null nếu không có
        - contains_table: true/false
        - contains_formula: true/false
        - summary: tóm tắt 1 câu nội dung của section này

        Các loại section:
        {section_types_str}

        Chỉ trả về JSON, không giải thích.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=0.0,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            import json
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return {
                "section_type": "other",
                "product_type": None,
                "belt_pitch": None,
                "contains_table": False,
                "contains_formula": False,
                "summary": title
            }

    def build_search_text(self, chunk: dict, metadata: dict) -> str:
        parts = []

        if metadata.get("product_type"):
            parts.append(f"Sản phẩm: {metadata['product_type']}")
        if metadata.get("belt_pitch"):
            parts.append(f"Pitch: {metadata['belt_pitch']}")
        if metadata.get("section_type"):
            parts.append(f"Loại thông tin: {SECTION_TYPES.get(metadata['section_type'], '')}")
        if metadata.get("summary"):
            parts.append(metadata["summary"])

        parts.append(chunk["content"][:2000])

        return "\n".join(parts)

    def process(self, pdf_path: str) -> list[dict]:

        markdown = self.extract_markdown(pdf_path)

        chunks = self.split_by_headers(markdown)
        logger.info(f"Tổng {len(chunks)} chunks cần xử lý.")

        points = []
        for i, chunk in enumerate(chunks):

            metadata = self.classify_chunk(
                title=chunk["title"],
                content_preview=chunk["content"]
            )

            payload = {
                "source_file":    Path(pdf_path).name,
                "chunk_index":    i,
                "title":          chunk["title"],
                "content":        chunk["content"],
                "char_count":     chunk["char_count"],
                "section_type":   metadata.get("section_type", "other"),
                "product_type":   metadata.get("product_type"),
                "belt_pitch":     metadata.get("belt_pitch"),
                "contains_table": metadata.get("contains_table", False),
                "contains_formula": metadata.get("contains_formula", False),
                "summary":        metadata.get("summary", ""),
                "brand":          "Bando",
                "catalog":        "Power Transmission Belts",
            }

            points.append({
                "chunk": chunk,
                "payload": payload,
                "search_text": self.build_search_text(chunk, metadata)
            })

        return points
