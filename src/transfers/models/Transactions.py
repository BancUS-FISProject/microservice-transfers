from pydantic import BaseModel, Field

from typing import Optional

class TransactionBase(BaseModel):
    sender: str
    receiver: str
    quantity: int
    status: str = "pending"
    currency: str = "USD"
    sender_balance: Optional[float] = None
    receiver_balance: Optional[float] = None
    gmt_time: Optional[str] = None

class TransactionCreate(BaseModel):
    sender: str
    receiver: str
    quantity: int

class TransactionView(TransactionBase):
    id: Optional[str] = None

class ErrorResponse(BaseModel):
    error: str
    status: str

class StatusUpdateRequest(BaseModel):
    status: str
