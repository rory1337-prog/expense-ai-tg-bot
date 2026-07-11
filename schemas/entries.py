from pydantic import BaseModel, Field


class EntryCreate(BaseModel):
    chat_id: str
    name: str
    amount: float = Field(gt=0)
    category: str
    type: str
    created_at: str


class EntryRead(EntryCreate):
    id: int
