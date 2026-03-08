# ============================================================================
# 실행화일 만들기
# pyinstaller 가 인식되지않을때
# pip show pyinstaller 명령후 위치를 찾이못한다면   pip install pyinstaller
# pyinstaller --onefile FI_0002.py
# ============================================================================
# 실행파일 실행 =======>   테이블 daily_prices2 생성


import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3
from datetime import datetime
import urllib3
import os

# SSL 인증 오류 방지
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_complete_data_and_save(ticker):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }

    # 1. Finviz에서 현재 시점 재무 지표 추출
    fv_url = f"https://finviz.com/quote.ashx?t={ticker.upper()}"
    res_fv = requests.get(fv_url, headers=headers, verify=False)
    soup = BeautifulSoup(res_fv.text, 'html.parser')

    def get_fv_val(label):
        tds = soup.find_all('td')
        for i, td in enumerate(tds):
            if td.text.strip() == label:
                val = tds[i + 1].text.strip().replace('%', '')
                return val if val != '-' else '0'
        return '0'

    # 재무 데이터 파싱
    eps = float(get_fv_val("EPS (ttm)"))
    roe = float(get_fv_val("ROE")) / 100
    peg = float(get_fv_val("PEG"))
    div = float(get_fv_val("Dividend %")) / 100
    p_b = float(get_fv_val("P/B"))
    p_s = float(get_fv_val("P/S"))
    p_c = float(get_fv_val("P/C"))  # PCR 대용
    curr_price = float(get_fv_val("Price"))

    # 역산을 통해 주당 가치 고정값 도출
    bps = curr_price / p_b if p_b > 0 else 0
    sps = curr_price / p_s if p_s > 0 else 0
    cps = curr_price / p_c if p_c > 0 else 0

    # 2. Yahoo Finance에서 1년치 일별 주가 수집
    hist_url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker.upper()}?range=1y&interval=1d"
    res_hist = requests.get(hist_url, headers=headers, verify=False)
    hist_json = res_hist.json()
    result = hist_json['chart']['result'][0]

    df = pd.DataFrame({
        'Ticker': ticker.upper(),
        'Date': [datetime.fromtimestamp(ts).strftime('%Y-%m-%d') for ts in result['timestamp']],
        'Close': result['indicators']['quote'][0]['close']
    }).dropna()

    # 3. 일별 시계열 지표 계산
    df['PER'] = df['Close'] / eps if eps != 0 else 0
    df['PBR'] = df['Close'] / bps if bps != 0 else 0
    df['PSR'] = df['Close'] / sps if sps != 0 else 0
    df['PCR'] = df['Close'] / cps if cps != 0 else 0
    df['ROE'] = roe
    df['EPS'] = eps
    df['PEG'] = peg
    # df['Dividend_Yield'] = div
    df['DIVIDEND_YIELD'] = div

    # 4. SQLite 저장
    # 이 파일(FI-WEB1.py)이 있는 절대 경로를 구함
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # DB 파일의 전체 경로를 만
    db_path = os.path.join(BASE_DIR, 'FI.db')

    conn = sqlite3.connect(db_path)

    try:
        # 주식 가치정보 테이블 (daily_prices2)
        df.to_sql('daily_prices2', conn, if_exists='append', index=False)

        # 기존 컬럼을 Primary Key(Index)로 설정
        df.set_index('Ticker', inplace=True)
        df.set_index('Date', inplace=True)

        print(f"✅ {ticker} 1년치 가치정보 데이터({len(df)}건) 저장 완료.")
    finally:

        conn.close()

#====================================================================================================================
# 테스트 실행
#====================================================================================================================
stocks = ["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "BRK-B", "TSLA", "AVGO", "LLY", "V", "TSM",
            "UNH", "JPM", "MA", "XOM", "JNJ", "PG", "COST", "HD", "ORCL", "ADBE", "ASML", "CVX",
            "TM", "MRK", "ABBV", "BAC", "KO", "PEP", "NFLX", "LIN", "CRM", "AMD", "DIS", "TMO",
            "WMT", "WFC", "ACN", "INTC", "CSCO", "PFE", "VZ", "ADI", "QCOM", "CAT", "TXN", "DHR", "AMGN", "IBM"]

for s in stocks:
    get_complete_data_and_save(s)
#====================================================================================================================

#====================================================================================================================
# 테이블 컬럼 이름변경
#====================================================================================================================
# 이 파일(FI-WEB1.py)이 있는 절대 경로를 구함
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# DB 파일의 전체 경로를 만
db_path = os.path.join(BASE_DIR, 'FI.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

table_name = "daily_prices2"
old_col = "Date"
new_col = "date"
query = f"ALTER TABLE {table_name} RENAME COLUMN {old_col} TO {new_col};"

try:
    cursor.execute(query)
    conn.commit()
    print(f"컬럼 '{old_col}'이 '{new_col}'로 변경되었습니다.")
except sqlite3.Error as e:
    print(f"에러 발생: {e}")

old_col = "Ticker"
new_col = "ticker"
query = f"ALTER TABLE {table_name} RENAME COLUMN {old_col} TO {new_col};"

try:
    cursor.execute(query)
    conn.commit()
    print(f"컬럼 '{old_col}'이 '{new_col}'로 변경되었습니다.")
except sqlite3.Error as e:
    print(f"에러 발생: {e}")

old_col = "Close"
new_col = "close"
query = f"ALTER TABLE {table_name} RENAME COLUMN {old_col} TO {new_col};"

try:
    cursor.execute(query)
    conn.commit()
    print(f"컬럼 '{old_col}'이 '{new_col}'로 변경되었습니다.")
except sqlite3.Error as e:
    print(f"에러 발생: {e}")

conn.close()
#====================================================================================================================
