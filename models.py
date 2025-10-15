# models.py
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship # relationship import
from database import Base
import datetime

# 새로운 Category 모델
class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True) # 카테고리 이름은 중복되면 안 됨

# 기존 Ledger 모델 수정
class Ledger(Base):
    __tablename__ = "ledger"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, default=datetime.date.today)
    # 'category' 컬럼은 삭제됩니다.
    description = Column(String)
    amount = Column(Float)
    type = Column(String)

    # Category 테이블을 가리키는 외래 키(Foreign Key) 추가
    category_id = Column(Integer, ForeignKey("categories.id"))

    # Ledger 모델에서 Category 모델의 데이터에 쉽게 접근할 수 있도록 관계 설정
    category = relationship("Category")