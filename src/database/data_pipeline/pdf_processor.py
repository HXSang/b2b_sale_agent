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

# Map section type → metadata
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
    """
    Xử lý catalog nhiều trang thành chunks có metadata.
    Mỗi chunk = 1 semantic unit (không phải cắt theo số ký tự).
    """
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.doc_converter = DocumentConverter()
        self.model = "gpt-4o-mini"

    # ──────────────────────────────────────────
    # BƯỚC 1: PDF → Markdown
    # ──────────────────────────────────────────
    def extract_markdown(self, pdf_path: str) -> str:
        path = Path(pdf_path)
        logger.info(f"Docling đang bóc tách {path.name}...")
        result = self.doc_converter.convert(path)
        markdown = result.document.export_to_markdown()
        logger.info(f"Bóc được {len(markdown)} ký tự.")
        return markdown

    # ──────────────────────────────────────────
    # BƯỚC 2: Markdown → Chunks theo header
    # ──────────────────────────────────────────
    def split_by_headers(self, markdown: str) -> list[dict]:
        """
        Tách markdown thành chunks dựa theo heading (#, ##, ###).
        Mỗi chunk giữ nguyên nội dung gốc không cắt xén.
        """
        # Split theo heading nhưng giữ heading trong chunk
        pattern = r'(?=^#{1,3} )'
        raw_sections = re.split(pattern, markdown, flags=re.MULTILINE)

        chunks = []
        for section in raw_sections:
            section = section.strip()
            if len(section) < 50:  # Bỏ qua section quá ngắn
                continue

            # Lấy title từ dòng đầu
            lines = section.split('\n')
            title = lines[0].replace('#', '').strip()

            chunks.append({
                "title": title,
                "content": section,
                "char_count": len(section)
            })

        logger.info(f"Tách được {len(chunks)} sections từ headers.")
        return chunks

    # ──────────────────────────────────────────
    # BƯỚC 3: Classify từng chunk bằng LLM
    # ──────────────────────────────────────────
    def classify_chunk(self, title: str, content_preview: str) -> dict:
        """
        Dùng LLM classify section type + extract metadata.
        Chỉ gửi 500 ký tự đầu để tiết kiệm token.
        """
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
            logger.warning(f"Classify thất bại: {e}")
            return {
                "section_type": "other",
                "product_type": None,
                "belt_pitch": None,
                "contains_table": False,
                "contains_formula": False,
                "summary": title
            }

    # ──────────────────────────────────────────
    # BƯỚC 4: Build vector payload
    # ──────────────────────────────────────────
    def build_search_text(self, chunk: dict, metadata: dict) -> str:
        """
        Convert chunk thành text để embedding.
        Ưu tiên metadata + summary + content.
        """
        parts = []

        if metadata.get("product_type"):
            parts.append(f"Sản phẩm: {metadata['product_type']}")
        if metadata.get("belt_pitch"):
            parts.append(f"Pitch: {metadata['belt_pitch']}")
        if metadata.get("section_type"):
            parts.append(f"Loại thông tin: {SECTION_TYPES.get(metadata['section_type'], '')}")
        if metadata.get("summary"):
            parts.append(metadata["summary"])

        # Thêm content nhưng giới hạn độ dài
        parts.append(chunk["content"][:2000])

        return "\n".join(parts)

    # ──────────────────────────────────────────
    # MAIN: Chạy toàn bộ pipeline
    # ──────────────────────────────────────────
    def process(self, pdf_path: str) -> list[dict]:
        """
        Trả về list các points sẵn sàng upsert vào Qdrant.
        """
        # 1. Extract
        markdown = self.extract_markdown(pdf_path)

        # 2. Split
        chunks = self.split_by_headers(markdown)
        logger.info(f"Tổng {len(chunks)} chunks cần xử lý.")

        points = []
        for i, chunk in enumerate(chunks):
            logger.info(f"Xử lý chunk {i+1}/{len(chunks)}: {chunk['title'][:50]}")

            # 3. Classify
            metadata = self.classify_chunk(
                title=chunk["title"],
                content_preview=chunk["content"]
            )

            # 4. Build payload
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

        logger.info(f"Hoàn tất chunking: {len(points)} points.")
        return points