import os
import logging
from pathlib import Path
import time
from typing import Optional

from openai import OpenAI
from pydantic import ValidationError
from dotenv import load_dotenv

from docling.document_converter import DocumentConverter

from src.extraction.schemas.oil_sensor import OilSensorSchema

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - [%(name)s] - %(message)s'
)
logger = logging.getLogger(__name__)

class DoclingOpenAIExtractor:
    def __init__(self, api_key: Optional[str] = None):
        load_dotenv()
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.model_name = os.getenv("OPENAI_MODEL")
        self.doc_converter = DocumentConverter()

    def _convert_pdf_to_markdown(self, file_path: Path) -> str:
        """Sử dụng Docling để đọc layout và bảng biểu, chuyển thành Markdown"""
        if not file_path.exists():
            raise FileNotFoundError(f"Không tìm thấy file: {file_path}")
        
        logger.info("Docling đang phân tích layout và bảng biểu. Vui lòng chờ...")
        result = self.doc_converter.convert(file_path)
        return result.document.export_to_markdown()

    def extract(self, pdf_path: str | Path) -> Optional[OilSensorSchema]:
        path_obj = Path(pdf_path)
        logger.info(f"=== Bắt đầu tiến trình với file: {path_obj.name} ===")

        try:
            markdown_content = self._convert_pdf_to_markdown(path_obj)
            logger.info(f"Docling đã bóc được {len(markdown_content)} ký tự Markdown.")
        except Exception as e:
            logger.error(f"Lỗi khi chạy Docling: {e}")
            return None

        prompt = f"""
        Bạn là một chuyên gia kỹ thuật phần cứng, nhiệm vụ là đọc và bóc tách thông số từ datasheet.
        Hãy đặc biệt chú ý đến các khu vực có định dạng bảng biểu (|---|---|).
        Tuyệt đối không giải thích, không suy diễn. Nếu một thông số không có trong văn bản, hãy để null.
        Với các trường số lượng, chỉ lấy giá trị số học, bỏ ký tự đơn vị đi kèm.
        
        Tài liệu Markdown:
        {markdown_content}
        """

        logger.info(f"Đang gửi lên OpenAI ({self.model_name}) và ép khuôn Pydantic...")
        
        max_retries = 3
        delay = 5

        for attempt in range(max_retries):
            try:
                completion = self.client.beta.chat.completions.parse(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    response_format=OilSensorSchema,
                    temperature=0.0
                )
                validated_data = completion.choices[0].message.parsed
                logger.info("Bóc tách & Validate thành công! Data đã sẵn sàng.")
                return validated_data
                
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg or "RateLimitError" in error_msg:
                    if attempt < max_retries - 1:
                        logger.warning(f"OpenAI chạm ngưỡng Rate Limit (Lần {attempt+1}/{max_retries}). Lùi lại {delay}s...")
                        time.sleep(delay)
                        delay *= 2
                    else:
                        logger.error(f"Thử {max_retries} lần vẫn dính Rate Limit: {e}")
                        return None
                else:
                    logger.error(f"Lỗi khi gọi OpenAI API hoặc Validate: {e}")
                    return None
                    
        return None