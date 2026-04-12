import os
import json
from openai import OpenAI
from dotenv import load_dotenv

from src.database.qdrant_core import QdrantManager
from src.ai.embedder import OpenAIEmbedding
from src.ai.tools.catalog_search import CatalogSearchTool
from src.ai.tools.quote_handler import QuoteHandler
from src.extraction.schemas.quote import QuoteRequestSchema

load_dotenv()

class B2BSalesAgent:
    def __init__(self, session_id: str = "default"):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model_name = os.getenv("OPENAI_MODEL")
        self.session_id = session_id

        self.db = QdrantManager()
        self.embedder = OpenAIEmbedding()
        self.search_tool = CatalogSearchTool(db_manager=self.db, embedder=self.embedder)
        self.quote_handler = QuoteHandler()

        self.system_instruction = """
        Bạn là "Core-Eye Agent" - Kỹ sư Sales B2B chuyên nghiệp, điềm tĩnh trong lĩnh vực THIẾT BỊ TỰ ĐỘNG HÓA VÀ CÔNG NGHIỆP (Cảm biến công nghiệp, LiDAR, Motor...).

        NGUYÊN TẮC:
        0. GIỚI HẠN LĨNH VỰC: Bạn cung cấp thiết bị cho MỤC ĐÍCH CÔNG NGHIỆP. 
        - Nếu khách hỏi sản phẩm 100% ngoài ngành (ô tô, quần áo, giải trí): Từ chối lịch sự.
        - Nếu khách hỏi những ứng dụng chung chung có thể dùng trong công nghiệp (như đo nhiệt độ dầu, nước, áp suất): TUYỆT ĐỐI KHÔNG TỪ CHỐI. Hãy MẶC ĐỊNH ĐÓ LÀ ỨNG DỤNG CÔNG NGHIỆP và tiếp tục tư vấn, hoặc hỏi thêm: "Anh/chị cần đo cho hệ thống máy móc hay dây chuyền nào?" để xác nhận.1. THÔNG SỐ KỸ THUẬT: Luôn dùng tool `search_products`. Không bịa thông số.
        2. GIÁ CẢ: Không bao giờ báo giá cụ thể. Khi khách chốt mua:
        - Thu thập đủ: tên, công ty, số lượng, mục đích dùng, liên hệ.
        - Sau đó → gọi tool `create_quote_request`.
        3. Câu hỏi chung chung → hỏi ngược lại sắc bén về thông số kỹ thuật.
        4. Ngắn gọn, đi thẳng vào vấn đề.
        """

        self.chat_history = [
            {"role": "system", "content": self.system_instruction}
        ]

        self.tools_schema = [
            {
                "type": "function",
                "function": {
                    "name": "search_products",
                    "description": "Tìm kiếm thông số kỹ thuật sản phẩm trong database.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Từ khóa kỹ thuật cần tìm. BẮT BUỘC phải bao gồm tên loại thiết bị kết hợp với thông số. Ví dụ: 'cảm biến đo dầu 41mA 24V' thay vì chỉ tìm '41mA'."
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_quote_request",
                    "description": """Tạo yêu cầu báo giá khi khách:
                    - Hỏi giá hoặc muốn mua sản phẩm cụ thể
                    - Đã xác nhận sản phẩm và số lượng
                    - Hỏi về delivery, lead time, bảo hành
                    KHÔNG gọi nếu khách chỉ hỏi thông số kỹ thuật.""",
                    "parameters": QuoteRequestSchema.model_json_schema()
                }
            }
        ]

        print("[Agent] Khởi động xong.")

    def chat(self, user_message: str, history: list) -> tuple[str, list]:
        # 1. Thêm tin nhắn của User
        history.append({"role": "user", "content": user_message})

        try:
            # 2. Gọi OpenAI Lần 1
            print("[Agent DEBUG] Gửi lên OpenAI lần 1 số lượng messages:", len(history))
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=history,
                tools=self.tools_schema,
                tool_choice="auto",
                temperature=0.0
            )

            response_message = response.choices[0].message
            
            # CHÚ Ý: Dump cái message của Assistant (có thể chứa tool_calls) vào history
            history.append(response_message.model_dump(exclude_none=True))

            # 3. Xử lý Tool Calling (Nếu có)
            if response_message.tool_calls:
                print(f"[Agent DEBUG] LLM yêu cầu gọi {len(response_message.tool_calls)} tools.")
                
                # Duyệt qua TỪNG tool call
                for tool_call in response_message.tool_calls:
                    name = tool_call.function.name
                    tool_call_id = tool_call.id # Lấy ID để lát trả lời
                    print(f"[Agent DEBUG] Đang xử lý Tool: {name} (ID: {tool_call_id})")
                    
                    try:
                        args = json.loads(tool_call.function.arguments)
                        if name == "search_products":
                            print(f"[Agent] Đang lục kho kiến thức cho: {args.get('query')}...")
                            tool_result = self.search_tool.execute(query_text=args.get("query"))
                        elif name == "create_quote_request":
                            print("[Agent] Đang lập phiếu báo giá...")
                            tool_result = self.quote_handler.handle(
                                llm_arguments=tool_call.function.arguments,
                                chat_history=history
                            )
                        else:
                            tool_result = f"Error: Không tìm thấy tool '{name}'."
                            
                    except Exception as tool_e:
                        print(f"[Cảnh báo] Lỗi khi chạy tool {name}: {tool_e}")
                        tool_result = f"Error: Tool execution failed due to {tool_e}"
                        
                    # QUAN TRỌNG NHẤT: Trả lời LẠI CHO ĐÚNG CÁI ID ĐÓ
                    history.append({
                        "role": "tool",
                        "tool_call_id": tool_call_id, # Phải khớp với ID lúc nãy
                        "name": name,
                        "content": str(tool_result)
                    })

                # 4. Gọi OpenAI Lần 2 (Để nó đọc kết quả Tool và chốt câu trả lời)
                print("[Agent DEBUG] Đã gắn xong kết quả Tool. Gọi OpenAI lần 2...")
                final_response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=history,
                    temperature=0.0
                )
                final_text = final_response.choices[0].message.content
                
                # Lưu câu trả lời cuối cùng
                history.append({"role": "assistant", "content": final_text})
                return final_text, history

            else:
                # Không có Tool, LLM trả lời thẳng
                return response_message.content, history

        except Exception as e:
            # In ra lỗi chi tiết để dễ debug
            import traceback
            traceback.print_exc()
            return f"Lỗi kỹ thuật: {e}", history