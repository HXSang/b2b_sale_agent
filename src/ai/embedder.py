import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class OpenAIEmbedding:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.ai_model = os.getenv("MODEL_EMBEDDING")
        
    def get_embedding(self, text: str) -> list[float]:
        try:
            response = self.client.embeddings.create(
                input=[text],
                model=self.ai_model,
            )
            return response.data[0].embedding
            
        except Exception as e:
            print(f"[Embedding Error]: Lỗi {e}")
            return []