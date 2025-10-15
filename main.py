# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import extract
from typing import List
from datetime import date, timedelta # datetime 관련 모듈 import

from fastapi.middleware.cors import CORSMiddleware
import models, schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS ミドルウェア追加
origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://127.0.0.1:5500", # Live Server 같은 확장 프로그램 포트
    "null" # 로컬 파일을 직접 열 때 (file://) Origin 헤더가 "null"이 될 수 있음
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # 위에서 정의한 origins 목록을 허용
    allow_credentials=True,      # 쿠키를 포함한 요청을 허용
    allow_methods=["*"],         # 모든 HTTP 메소드(GET, POST 등)를 허용
    allow_headers=["*"],         # 모든 HTTP 헤더를 허용
)

# データベース・セッション依存症注入
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 카테고리 관리를 위한 API 엔드포인트 추가 ---
@app.post("/categories/", response_model=schemas.Category)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    db_category = models.Category(name=category.name)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@app.get("/categories/", response_model=List[schemas.Category])
def read_categories(db: Session = Depends(get_db)):
    return db.query(models.Category).all()

@app.delete("/categories/{category_id}", status_code=status.HTTP_200_OK)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    # 1. 삭제할 카테고리가 존재하는지 확인
    db_category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    # 2. 해당 카테고리를 사용하고 있는 가계부 내역이 있는지 확인
    is_used = db.query(models.Ledger).filter(models.Ledger.category_id == category_id).first()
    if is_used:
        # 사용 중이라면 에러를 발생시켜 삭제를 막음
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This category is in use and cannot be deleted."
        )

    # 3. 사용 중이지 않다면 삭제 진행
    db.delete(db_category)
    db.commit()
    return {"message": "Category deleted successfully"}

# --- 가계부 API 수정 ---
@app.post("/ledger/", response_model=schemas.Ledger)
def create_ledger_entry(entry: schemas.LedgerCreate, db: Session = Depends(get_db)):
    db_entry = models.Ledger(**entry.dict())
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry

# 기간별 조회를 위해 GET 엔드포인트 대폭 수정
@app.get("/ledger/", response_model=List[schemas.Ledger])
def read_ledger_entries(period: str | None = "all", db: Session = Depends(get_db)):
    today = date.today()
    query = db.query(models.Ledger)

    if period == "day":
        query = query.filter(models.Ledger.date == today)
    elif period == "week":
        start_of_week = today - timedelta(days=today.weekday())
        query = query.filter(models.Ledger.date >= start_of_week)
    elif period == "month":
        query = query.filter(extract('year', models.Ledger.date) == today.year,
                             extract('month', models.Ledger.date) == today.month)
    
    # "all" 또는 다른 값이 들어오면 모든 데이터를 조회
    return query.order_by(models.Ledger.date.desc()).all()

@app.put("/ledger/{ledger_id}", response_model=schemas.Ledger)
def update_ledger_entry(ledger_id: int, entry: schemas.LedgerCreate, db: Session = Depends(get_db)):
    # 1. 수정할 내역을 데이터베이스에서 찾습니다.
    db_ledger = db.query(models.Ledger).filter(models.Ledger.id == ledger_id).first()
    if db_ledger is None:
        raise HTTPException(status_code=404, detail="Ledger entry not found")

    # 2. 받은 데이터(entry)로 기존 데이터(db_ledger)의 값을 갱신합니다.
    for key, value in entry.dict().items():
        setattr(db_ledger, key, value)

    # 3. 변경사항을 커밋하고 갱신된 객체를 반환합니다.
    db.commit()
    db.refresh(db_ledger)
    return db_ledger

@app.delete("/ledger/{ledger_id}", status_code=status.HTTP_200_OK)
def delete_ledger_entry(ledger_id: int, db: Session = Depends(get_db)):
    # 1. 삭제할 내역을 데이터베이스에서 찾습니다.
    db_ledger = db.query(models.Ledger).filter(models.Ledger.id == ledger_id).first()
    if db_ledger is None:
        raise HTTPException(status_code=404, detail="Ledger entry not found")

    # 2. 데이터를 삭제하고 커밋합니다.
    db.delete(db_ledger)
    db.commit()
    return {"message": "Ledger entry deleted successfully"}