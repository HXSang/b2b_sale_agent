import redis
import json
import os
from dotenv import load_dotenv

load_dotenv()

class RedisMemory:
    def __init__(self):
        redis_host = os.getenv("REDIS_HOST", "redis")
        self.client = redis.Redis(host=redis_host, port=6379, decode_responses=True)
    
    def get_history(self, session_id: str, system_instruction: str, window_size: int = 10) -> list:
        key = f"session:{session_id}"
        raw_data = self.client.get(key)
        
        system_msg = {"role": "system", "content": system_instruction}
        
        if raw_data is None:
            return [system_msg]
        else:
            full_history = json.loads(raw_data)
            if full_history and full_history[0].get("role") == "system":
                full_history = full_history[1:]
                
            recent_history = full_history[-window_size:] if len(full_history) > window_size else full_history

            final_history = [system_msg] + recent_history
            
            return final_history
    
    def save_history(self, session_id: str, history: list):
        key = f"session:{session_id}"
        json_history = json.dumps(history, ensure_ascii=False)
        self.client.setex(name=key, time=604800, value=json_history)