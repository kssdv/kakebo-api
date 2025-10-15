# models.py
from sqlalchemy import Column, Integer, String, Float, Date
from database import Base
import datetime

# テーブルの構造をクラスで定義する
class Ledger(Base):
    __tablename__ = "ledger" # テーブル名
    # コラムの正義
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, default=datetime.date.today)
    category = Column(String, index=True)
    description = Column(String)
    amount = Column(Float)
    type = Column(String) # "income" or "expense"