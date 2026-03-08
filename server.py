# ============================================================================
# 실행화일 만들기
# pip show pyinstaller 명령후 위치를 찾이못한다면   pip install pyinstaller
# pyinstaller 가 인식되지않을때
# pyinstaller --onefile server.py
# ============================================================================
# ============================================================================
# 서버실행
# uvicorn server:app --reload
# http://127.0.0.1:8000/stocks/AAPL?start_date=2026-01-01&end_date=2026-02-28
# ============================================================================



from typing import Optional

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, String, Float, desc, false
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase, Query
from starlette.middleware.cors import CORSMiddleware
import random
# =========================================================
# 실행화일로 만들었을때 정상 백엔드서버 작동을 위해
# 실행파일 만들기
# pyinstaller --onefile --collect-all uvicorn main.py
# =========================================================
import uvicorn
import multiprocessing
# =========================================================


# DB 설정
SQLALCHEMY_DATABASE_URL = "sqlite:///./FI.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase): pass

class DailyPrice(Base):
    __tablename__ = "daily_total_info"
    # ticker = Column(String, primary_key=True, index=True)
    ticker = Column(String, primary_key=True, index=False)
    name = Column(String)
    date = Column(String, primary_key=True, index=True)
    usd_price = Column(Float)
    krw_price = Column(Float)
    close = Column(Float)
    per = Column(Float)
    pbr = Column(Float)
    psr = Column(Float)
    pcr = Column(Float)
    roe = Column(Float)
    eps = Column(Float)
    peg = Column(Float)
    dividend_yield = Column(Float)

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@app.get("/stocks")
def get_all_stocks(db: Session = Depends(get_db)):
    stocks = db.query(DailyPrice.ticker, DailyPrice.date, DailyPrice.name, DailyPrice.usd_price, DailyPrice.krw_price).distinct().all()

    return [{"ticker": s.ticker, "date": s.date, "name": s.name, "usd_price": s.usd_price, "krw_price": s.krw_price} for s in stocks]



# http://127.0.0.1:8000/stocks/AAPL?start_date=2026-01-01&end_date=2026-02-28
@app.get("/stocks/{ticker}")
def read_stock(ticker: str,
               start_date: str,
               end_date: str,
               db: Session = Depends(get_db)):

    # 1. 기존 기능: 거래 이력 가져오기
    #prices = db.query(DailyPrice).filter(DailyPrice.ticker == ticker).order_by(desc(DailyPrice.date)).all()
    prices = db.query(DailyPrice).filter(DailyPrice.ticker == ticker).filter(DailyPrice.date >= start_date).filter(DailyPrice.date <= end_date).order_by(desc(DailyPrice.date)).all()

    if not prices:
        raise HTTPException(status_code=404, detail="Data not found")

    return {
        # "metrics": metrics, # 신규 가치 정보
        "history": prices   # 기존 가격 이력
    }


# =========================================================
# 실행화일로 만들었을때 정상 백엔드서버 작동을 위해
# =========================================================
if __name__ == "__main__":
    # Windows에서 멀티프로세싱 관련 오류를 방지하기 위해 필수
    multiprocessing.freeze_support()

    # uvicorn.run을 통해 소스 코드 내부에서 서버 실행
    uvicorn.run(app, host="127.0.0.1", port=8000)
# =========================================================