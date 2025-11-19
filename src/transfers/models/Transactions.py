from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class TransactionBase(BaseModel):
    date: datetime = Field(default_factory=datetime.utcnow)
    sender: str
    receiver: str
    quantity: int
    status: str = "pending"


class TransactionCreate(BaseModel):
    sender: str
    receiver: str
    quantity: int


class TransactionView(TransactionBase):
    id: Optional[str] = None
