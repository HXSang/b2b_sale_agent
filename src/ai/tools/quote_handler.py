import json
import os
from openai import OpenAI
from pydantic import ValidationError
from dotenv import load_dotenv

from src.extraction.schemas.quote import QuoteRequestSchema
from src.database.persistent_memory import PersistentMemory

load_dotenv()

class QuoteHandler:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("OPENAI_MODEL")
        self.db = PersistentMemory()
        self.max_retries = 3

    def handle(self, llm_arguments: str, chat_history: list) -> str:
        last_error = None

        for attempt in range(self.max_retries):
            try:
                if attempt == 0:
                    raw_data = json.loads(llm_arguments)
                else:
                    print(f"[QuoteHandler] Retry lần {attempt} — lỗi: {last_error}")
                    raw_data = self._retry_fill_missing(llm_arguments, chat_history, str(last_error))

                quote = QuoteRequestSchema.model_validate(raw_data)
                self._save(quote)
                self._notify(quote)

                return (
                    f"Đã tạo báo giá {quote.quote_id} thành công. "
                    f"Sales sẽ liên hệ khách trong 24 giờ."
                )

            except (json.JSONDecodeError, ValidationError) as e:
                last_error = e
                continue
            except Exception as e:
                print(f"🚨 [DEBUG QUOTEHANDLER] Lỗi tạo báo giá: {e}")
                import traceback
                traceback.print_exc()
                return f"Lỗi hệ thống khi tạo báo giá: {e}"
        return (
            "Không thể tạo báo giá do thiếu thông tin. "
            "Hãy hỏi khách thêm: tên công ty, số lượng, mục đích sử dụng."
        )

    def _save(self, quote: QuoteRequestSchema):
        contact = quote.customer.phone_zalo or quote.customer.email or "N/A"
        json_data = json.dumps(quote.model_dump(), ensure_ascii=False)
        self.db.save_quote(
            quote_id=quote.quote_id,
            status=quote.status,
            priority=quote.priority,
            customer_name=quote.customer.contact_name,
            customer_company=quote.customer.company or "N/A",
            customer_contact=contact,
            data = json_data
        )

    def _notify(self, quote: QuoteRequestSchema):
        products = ", ".join([i.product_name for i in quote.items])
        print(f"""
[SALES ALERT] {'='*40}
Quote ID : {quote.quote_id}
Priority : {quote.priority.upper()}
Khách    : {quote.customer.contact_name} — {quote.customer.company}
Liên hệ  : {quote.customer.phone_zalo or quote.customer.email}
Sản phẩm : {products}
Notes    : {quote.sales_notes}
{'='*50}
        """)

    def _retry_fill_missing(self, original_args: str, chat_history: list, error: str) -> dict:
        prompt = f"""
JSON báo giá bị lỗi validation: {error}

JSON bị lỗi:
{original_args}

Dựa vào hội thoại, điền đầy đủ các trường còn thiếu.
Chỉ trả về JSON hoàn chỉnh.

Schema:
{json.dumps(QuoteRequestSchema.model_json_schema(), ensure_ascii=False, indent=2)}
"""
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0.0,
            messages=[*chat_history, {"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)