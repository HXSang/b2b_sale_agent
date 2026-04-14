from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from src.ai.agent import B2BSalesAgent
import sys
import os
from src.memory.redis_core import RedisMemory

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

class ChatRequest(BaseModel):
    session_id : str
    message : str

class ChatResponse(BaseModel):
    reply : str
    
app = FastAPI(title="B2B Sale API")
print("[System] Đang khởi động Agent và kết nối Redis...")
agent = B2BSalesAgent()
memory = RedisMemory()

@app.post("/chat", response_model=ChatResponse)
def chat_with_agent(request: ChatRequest):
    try:
        system_rule = agent.system_instruction
        history = memory.get_history(request.session_id, system_instruction=system_rule)
        reply, new_history = agent.chat(request.message, history)
        memory.save_history(request.session_id, new_history)
        test_data = memory.client.get(f"session:{request.session_id}")
        return ChatResponse(reply=reply)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
