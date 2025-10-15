# schemas.py
from pydantic import BaseModel
import datetime

# 家計簿項目の基本フィールドの定義
class LedgerBase(BaseModel):
    category: str
    description: str | None = None
    amount: float
    type: str # "income" or "expense"
    date: datetime.date | None = datetime.date.today()

# 生成するとき(POST要請)使用するモデル
class LedgerCreate(LedgerBase):
    pass

# データベースで検索した後、クライアントに応答するとき使うモデル
class Ledger(LedgerBase):
    id: int
    
    class Config:
        orm_mode = True # SQLAlchemy モデル客体をPydanticモデルに自動変換の出来るよにしてくれる設定