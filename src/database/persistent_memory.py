import os
import json
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

class Conversation(Base):
    __tablename__ = "conversations"
    id          = Column(Integer, primary_key=True, autoincrement=True)
    session_id  = Column(String(255), nullable=False, index=True)
    role        = Column(String(50), nullable=False)
    content     = Column(Text, nullable=False)
    created_at  = Column(DateTime, default=datetime.utcnow)

class QuoteRecord(Base):
    __tablename__ = "quotes"
    id               = Column(Integer, primary_key=True, autoincrement=True)
    quote_id         = Column(String(50), unique=True, nullable=False)
    status           = Column(String(20), default="pending")
    priority         = Column(String(10), nullable=False)
    customer_name    = Column(String(255))
    customer_company = Column(String(255))
    customer_contact = Column(String(255))
    data             = Column(Text, nullable=False)  
    created_at       = Column(DateTime, default=datetime.utcnow)

class PersistentMemory:
    def __init__(self):
        db_url = os.getenv("DATABASE_URL")
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def save_message(self, session_id: str, role: str, content: str):
        with self.Session() as db:
            msg = Conversation(
                session_id=session_id,
                role=role,
                content=content if isinstance(content, str) else json.dumps(content, ensure_ascii=False)
            )
            db.add(msg)
            db.commit()

    def load_history(self, session_id: str, limit: int = 40) -> list:
        with self.Session() as db:
            rows = (
                db.query(Conversation)
                .filter(Conversation.session_id == session_id)
                .order_by(Conversation.created_at.desc())
                .limit(limit)
                .all()
            )
            rows = list(reversed(rows))
            return [{"role": r.role, "content": r.content} for r in rows]

    def save_quote(self, quote_id: str, status: str, priority: str,
                   customer_name: str, customer_company: str,
                   customer_contact: str, data: str):
        with self.Session() as db:
            record = QuoteRecord(
                quote_id=quote_id,
                status=status,
                priority=priority,
                customer_name=customer_name,
                customer_company=customer_company,
                customer_contact=customer_contact,
                data=data
            )
            db.add(record)
            db.commit()

    def delete_session(self, session_id: str):
        with self.Session() as db:
            db.query(Conversation).filter(
                Conversation.session_id == session_id
            ).delete()
            db.commit()
