from datetime import datetime

from pydantic import BaseModel, Field
from typing import Optional, List

# Base account data
class AccountBase(BaseModel):
    name: str
    iban: str
    cards: List[str] = Field(default_factory=list)
    creation_date: datetime = Field(default_factory=datetime.now)
    email: str
    subscription: str
    balance: int = 0
    isBlocked: bool = False

# Account update data needed
class AccountCreate(BaseModel):
    name: str
    email: str
    subscription: str = "Free"

# Account update balance data needed
class AccountUpdatebalance(BaseModel):
    balance: int

class AccountUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    subscription: Optional[str] = None
    
class AccountView(BaseModel):
    name: str
    iban: str
    cards: List[str]
    creation_date: datetime
    email: str
    subscription: str
    balance: int
    isBlocked: bool
    pass