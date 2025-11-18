from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class EmptyGet404(BaseModel):
    """
    Account not found
    """
    pass

class EmptyPatch400(BaseModel):
    """
    Bad Request
    """
    pass

class EmptyPatch403(BaseModel):
    """
    Forbidden Operation - Not sufficient funds
    """
    pass

class EmptyPatch404(BaseModel):
    """
    Account not found
    """
    pass