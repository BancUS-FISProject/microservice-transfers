from pydantic import BaseModel, Field
from datetime import datetime

from typing import Optional

class TransactionBase(BaseModel):
    sender: str
    receiver: str
    quantity: float
    status: str = "pending"
    currency: str = "USD"
    date: Optional[datetime] = None
    sender_balance: Optional[float] = None
    receiver_balance: Optional[float] = None
    gmt_time: Optional[str] = None

class TransactionCreate(BaseModel):
    sender: str
    receiver: str
    quantity: float

class TransactionView(TransactionBase):
    id: Optional[str] = None

class ErrorResponse(BaseModel):
    error: str
    status: str

class StatusUpdateRequest(BaseModel):
    status: str
