import os
import json
import logging
from pathlib import Path
import time
from openai import OpenAI
from pydantic import BaseModel
from dotenv import load_dotenv

from docling.document_converter import DocumentConverter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CatalogExtractor:
    def __init__(self):
        load_dotenv()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model_name = os.getenv("OPENAI_MODEL") 

        logger.info("Đang khởi động cỗ máy Docling...")
        self.doc_converter = DocumentConverter()

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Nhiệm vụ: Nuốt PDF, bóc tách bảng biểu, nhả ra Markdown.
        """
        path_obj = Path(pdf_path)
        if not path_obj.exists():
            logger.error(f"Không tìm thấy file: {path_obj}")
            return ""
            
        logger.info(f"Docling đang phân tích file {path_obj.name}...")
        try:
            result = self.doc_converter.convert(path_obj)
            markdown_content = result.document.export_to_markdown()
            logger.info(f"Docling đã bóc được {len(markdown_content)} ký tự Markdown.")
            return markdown_content
        except Exception as e:
            logger.error(f"Lỗi khi chạy Docling: {e}")
            return ""

    def extract_to_schema(self, markdown_text: str, schema_class: type[BaseModel]) -> dict:
        if not markdown_text:
            return None

        logger.info(f"Đang ép khuôn JSON bằng OpenAI: {schema_class.__name__}...")
        
        prompt = f"""
        Bạn là một kỹ sư B2B chuyên nghiệp. Hãy đọc tài liệu Markdown (được trích xuất từ PDF) sau.
        Đặc biệt chú ý đến các thông số trong bảng biểu (|---|---|).
        Tuyệt đối không giải thích, không suy diễn, chỉ trả về dữ liệu đúng định dạng JSON được yêu cầu.
        Nếu không có thông số, hãy để null.
        
        Tài liệu Markdown:
        {markdown_text}
        """
        max_retries = 3 
        delay = 5 

        for attempt in range(max_retries):
            try:
                completion = self.client.beta.chat.completions.parse(
                    model=self.model_name,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    response_format=schema_class,
                    temperature=0.0
                )
                
                return completion.choices[0].message.parsed.model_dump()
                
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg or "RateLimitError" in error_msg:
                    if attempt < max_retries - 1:
                        logger.warning(f"OpenAI chạm ngưỡng Rate Limit (Lần {attempt+1}/{max_retries}). Lùi lại {delay}s rồi thử tiếp...")
                        time.sleep(delay)
                        delay *= 2 
                    else:
                        logger.error(f"Đã thử {max_retries} lần nhưng vẫn dính Rate Limit: {e}")
                        return None
                else:
                    logger.error(f"Lỗi hệ thống khi bóc tách: {e}")
                    return None
        return None