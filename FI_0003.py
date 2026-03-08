# ============================================================================
# 실행화일 만들기
# pyinstaller 가 인식되지않을때
# pip show pyinstaller 명령후 위치를 찾이못한다면   pip install pyinstaller
# pyinstaller --onefile FI_0003.py
# ============================================================================
# 실행파일 실행 =======>   테이블 daily_total_info 생성

import sqlite3
import os

def create_total_info_table():
    # 이 파일(FI-WEB1.py)이 있는 절대 경로를 구함
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # DB 파일의 전체 경로를 만
    db_path = os.path.join(BASE_DIR, 'FI.db')

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. 기존 테이블이 있다면 삭제 (초기화 시)
    cursor.execute("DROP TABLE IF EXISTS daily_total_info")

    # 2. 조인된 결과를 바탕으로 새 테이블 생성 및 데이터 삽입
    # 특정 날짜('2026-02-23') 데이터만 합쳐서 새 테이블로 저장
    # target_date = '2026-02-23'

    query = f"""
    CREATE TABLE daily_total_info AS
    SELECT 
        A.ticker, A.name, A.date, A.usd_price, A.krw_price,
        B.close, B.PER, B.PBR, B.PSR, B.PCR, B.ROE, B.EPS, B.PEG, B.DIVIDEND_YIELD
    FROM daily_prices A
    INNER JOIN daily_prices2 B ON A.ticker = B.ticker AND A.date = B.date
    
    """

    # WHERE
    # A.date = '{target_date}'

    try:
        cursor.execute(query)
        conn.commit()
        print(f"기준 daily_total_info 테이블이 성공적으로 생성되었습니다.")
    except Exception as e:
        print(f"오류 발생: {e}")
    finally:
        conn.close()


# 실행
create_total_info_table()