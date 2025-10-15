# schemas.py
from pydantic import BaseModel
import datetime

# --- Category 스키마 추가 ---
class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int

    class Config:
        orm_mode = True

# --- Ledger 스키마 수정 ---
class LedgerBase(BaseModel):
    description: str | None = None
    amount: float
    type: str
    date: datetime.date | None = datetime.date.today()
    category_id: int # category 이름(str) 대신 category_id(int)를 받도록 변경

class LedgerCreate(LedgerBase):
    pass

class Ledger(LedgerBase):
    id: int
    category: Category # 응답을 보낼 때는 카테고리 전체 정보를 포함하여 보냄

    class Config:
        orm_mode = True