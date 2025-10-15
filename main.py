# main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
# CORSミドルウェア追加
from fastapi.middleware.cors import CORSMiddleware

import models, schemas
from database import SessionLocal, engine

# データベース・テーブルの作成
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS ミドルウェア追加
origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://127.0.0.1:5500", # Live Server 같은 확장 프로그램 포트
    "null" # 로컬 파일을 직접 열 때 (file://) Origin 헤더가 "null"이 될 수 있음
]

# データベース・セッション依存症注入
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/ledger/", response_model=schemas.Ledger)
def create_ledger_entry(entry: schemas.LedgerCreate, db: Session = Depends(get_db)):
    # 新しい家計簿項目追加
    db_entry = models.Ledger(**entry.dict())
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry

@app.get("/ledger/", response_model=List[schemas.Ledger])
def read_ledger_entries(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # 家計簿う項目検索
    entries = db.query(models.Ledger).offset(skip).limit(limit).all()
    return entries

@app.get("/ledger/{entry_id}", response_model=schemas.Ledger)
def read_ledger_entry(entry_id: int, db: Session = Depends(get_db)):
    # 特定家計簿検索
    entry = db.query(models.Ledger).filter(models.Ledger.id == entry_id).first()
    if entry is None:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry