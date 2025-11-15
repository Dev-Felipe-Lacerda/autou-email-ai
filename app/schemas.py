from pydantic import BaseModel
from typing import Optional


class EmailTextRequest(BaseModel):
    text: str


class EmailAnalysisResponse(BaseModel):
    category: str
    sub_category: Optional[str] = None
    reason: Optional[str] = None
    auto_reply: str
