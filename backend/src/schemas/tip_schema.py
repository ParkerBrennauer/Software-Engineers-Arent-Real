from pydantic import BaseModel
from typing import Optional

class TipRequest(BaseModel):
    tip_percent: Optional[float] = None
    tip_amount: Optional[float] = None
