import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class CatalogSearchTool:
    def __init__(self, db_manager, embedder):
        self.db = db_manager
        self.embedder = embedder
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.rewriter_model = os.getenv("OPENAI_MODEL") 

    def _rewrite_query(self, raw_query: str) -> str:
        prompt = f"""
        Nhiệm vụ: Dịch yêu cầu khách hàng thành từ khóa kỹ thuật Tiếng Anh để tìm trong database cảm biến công nghiệp.

        Ví dụ:
        - "cảm biến đo xa ngoài trời cho drone" -> "LiDAR long range outdoor UAV lightweight"
        - "đo góc nghiêng chống rung" -> "IMU tilt angle vibration resistant"
        - "đo dầu nhớt độ nhớt" -> "oil sensor viscosity measurement industrial"
        - "chịu được nước mưa" -> "IP67 IP68 waterproof outdoor"
        - "chuẩn giao tiếp công nghiệp" -> "RS485 CAN bus industrial interface"

        Yêu cầu của khách: "{raw_query}"

        Chỉ trả về từ khóa, không giải thích.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.rewriter_model,
                temperature=0.0,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"-> [Rewriter] Lỗi: {e}. Fallback về câu gốc.")
            return raw_query

    def _reranking(self, query: str, results: list) -> list:
        if not results:
            return results

        candidates = []
        for i, res in enumerate(results):
            name = res.payload.get('product_name') or 'N/A'
            desc_raw = res.payload.get('general_description_raw') or ''
            desc = str(desc_raw)[:300]
            
            specs = {k: v for k, v in res.payload.items()
                        if k not in {'product_name', 'general_description_raw', 'source_file'}
                        and v is not None}
            candidates.append(f"[{i}] {name}\nMô tả: {desc}\nSpecs: {specs}")

        prompt = f"""
            Yêu cầu của khách: "{query}"

            Dưới đây là {len(results)} sản phẩm tìm được. Hãy sắp xếp lại theo mức độ PHÙ HỢP THỰC SỰ với yêu cầu.

            {chr(10).join(candidates)}

            Chỉ trả về danh sách index theo thứ tự ưu tiên, cách nhau bằng dấu phẩy.
            Ví dụ: 2,0,4,1,3
            Không giải thích gì thêm.
            """
        try:
            response = self.client.chat.completions.create(
                model=self.rewriter_model,
                temperature=0.0,
                messages=[{"role": "user", "content": prompt}]
            )
            result_text = response.choices[0].message.content.strip()
            order = [int(x.strip()) for x in result_text.split(',')]
            
            return [results[i] for i in order if i < len(results)]
        except Exception as e:
            print(f"-> [Reranker] Lỗi: {e}. Giữ nguyên thứ tự cũ.")
            return results

    def execute(self, query_text: str) -> str:
        print(f"\n[SearchTool] Nhận lệnh: '{query_text}'")

        optimized_query = self._rewrite_query(query_text)
        print(f"-> [Rewriter] Đã dịch: '{optimized_query}'")

        query_vector = self.embedder.get_embedding(optimized_query)
        if not query_vector:
            return "Lỗi hệ thống: Không thể tạo vector tìm kiếm."

        results = self.db.search(
            collection_name="b2b_sensors",
            query_vector=query_vector,
            limit=10,
            score_threshold=0.2
        )
        if not results:
            return "Không tìm thấy sản phẩm nào phù hợp trong catalog."

        reranked = self._reranking(query_text, results)[:3]
        print(f"-> [Reranker] Xong. Giữ lại {len(reranked)}/{len(results)} sản phẩm.")

        SKIP_KEYS = {'product_name', 'general_description_raw', 'source_file', '_source_collection'}

        lines = ["--- KẾT QUẢ TỪ KHO ---"]
        for i, res in enumerate(reranked, 1):
            payload = res.payload
            name = payload.get('product_name') or 'N/A'
            desc_raw = payload.get('general_description_raw') or ''
            desc = str(desc_raw)[:200]
            score = round(res.score, 3)

            specs = [
                f"  - {k}: {v}"
                for k, v in payload.items()
                if k not in SKIP_KEYS and v is not None and v != [] and v != ""
            ]

            lines.append(f"\n[{i}] {name} (score: {score})")
            lines.append(f"Mô tả: {desc}...")
            lines.extend(specs)

        return "\n".join(lines)