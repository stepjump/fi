# ============================================================================
# 실행화일 만들기
# pyinstaller 가 인식되지않을때
# pip show pyinstaller 명령후 위치를 찾이못한다면   pip install pyinstaller
# pyinstaller --onefile FI_0001.py
# ============================================================================
# 실행파일 실행 =======>   테이블 daily_prices 생성


import requests
import pandas as pd
import urllib3
import matplotlib.pyplot as plt
import sqlite3
from datetime import datetime
import os

# 환경 설정
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False


# 주식 거래정보 테이블 (daily_prices)
def init_db():

    # 이 파일(FI-WEB1.py)이 있는 절대 경로를 구함
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # DB 파일의 전체 경로를 만
    db_path = os.path.join(BASE_DIR, 'FI.db')

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

      # 1. 기존 테이블이 있다면 삭제 (초기화 시)
    cursor.execute("DROP TABLE IF EXISTS daily_prices")

    cursor.execute('''    
                   CREATE TABLE IF NOT EXISTS daily_prices  
                   (
                       ticker                       TEXT,
                       name                       TEXT,
                       date                       TEXT,
                       usd_price                       REAL,
                       krw_price                       REAL,                      
                       PRIMARY
                       KEY
                   (
                       ticker,
                       date
                   )
                       )
                   ''')
    conn.commit()
    return conn




def get_exchange_rate():
    url = "https://query1.finance.yahoo.com/v8/finance/chart/USDKRW=X?interval=1d&range=1d"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, verify=False, timeout=10)
        return response.json()['chart']['result'][0]['meta']['regularMarketPrice']
    except:
        return 1450.0





def get_top_50_tickers():
    return {
        "AAPL": "애플", "MSFT": "마이크로소프트", "NVDA": "엔비디아", "GOOGL": "알파벳",
        "AMZN": "아마존", "META": "메타", "BRK-B": "버크셔", "TSLA": "테슬라",
        "AVGO": "브로드컴", "LLY": "일라이릴리", "V": "비자", "TSM": "TSMC",
        "UNH": "유나이티드헬스", "JPM": "JP모건", "MA": "마스터카드", "XOM": "엑슨모빌",
        "JNJ": "존슨앤존슨", "PG": "P&G", "COST": "코스트코", "HD": "홈디포",
        "ORCL": "오라클", "ADBE": "어도비", "ASML": "ASML", "CVX": "셰브론",
        "TM": "토요타", "MRK": "머크", "ABBV": "애브비", "BAC": "뱅크오브아메리카",
        "KO": "코카콜라", "PEP": "펩시", "NFLX": "넷플릭스", "LIN": "린데",
        "CRM": "세일즈포스", "AMD": "AMD", "DIS": "디즈니", "TMO": "써모피셔",
        "WMT": "월마트", "WFC": "웰스파고", "ACN": "액센츄어", "INTC": "인텔",
        "CSCO": "시스코", "PFE": "화이자", "VZ": "버라이즌", "ADI": "아날로그디바이스",
        "QCOM": "퀄컴", "CAT": "캐터필러", "TXN": "텍사스인스트루먼트", "DHR": "다나허",
        "AMGN": "암젠", "IBM": "IBM"
    }








def update_all_stocks_to_db(conn, rate):
    tickers_dict = get_top_50_tickers()
    total = len(tickers_dict)
    print(f"\n🔄 [DB 업데이트] 총 {total}개 종목의 '1년치' 데이터를 동기화합니다...")

    for i, (ticker, name) in enumerate(tickers_dict.items(), 1):
        try:
            # 기간을 1y(1년)로 설정
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=1y"
            headers = {'User-Agent': 'Mozilla/5.0'}
            res = requests.get(url, headers=headers, verify=False, timeout=10)
            data = res.json()['chart']['result'][0]

            df = pd.DataFrame({
                'Date': pd.to_datetime(data['timestamp'], unit='s').strftime('%Y-%m-%d'),
                'USD': data['indicators']['quote'][0]['close'],
                'Ticker': ticker,
                'Name': name
            }).dropna()
            df['KRW'] = df['USD'] * rate

            cursor = conn.cursor()
            for _, row in df.iterrows():
                cursor.execute('''
                INSERT OR REPLACE INTO daily_prices (ticker, name, date, usd_price, krw_price)
                VALUES (?, ?, ?, ?, ?)
            ''', (row['Ticker'], row['Name'], row['Date'], row['USD'], row['KRW']))
            conn.commit()

            print(f"\r진행률: {i}/{total} ({int(i / total * 100)}%) - {name} 동기화 완료", end='')
        except Exception as e:
            print(f"\n❌ {ticker} 수집 실패: {e}")

        print("\n✨ 1년치 데이터가 DB에 최신화되었습니다.")




#
# def show_menu(tickers):
#     now = datetime.now().strftime('%Y-%m-%d %H:%M')
#     print("\n" + "=" * 75)
#     print(f"   📅 조회 시각: {now} | 미국 주식 상위 50개 [1년 데이터] 분석 시스템")
#     print("=" * 75)
#
#     ticker_keys = list(tickers.keys())
#     for i in range(0, len(ticker_keys), 4):
#         row = ""
#         for j in range(4):
#             if i + j < len(ticker_keys):
#                 t = ticker_keys[i + j]
#                 n = tickers[t]
#                 row += f"{i + j + 1:2d}. {n[:6]:<6}({t:<5}) "
#         print(row)
#     print("=" * 75)
#
#
#
#
#     while True:
#         choice = input("\n분석할 번호 입력 (종료: 0): ")
#         if choice == '0': return None, None
#         try:
#             idx = int(choice)
#             if 1 <= idx <= len(ticker_keys):
#                 selected_ticker = ticker_keys[idx - 1]
#                 return selected_ticker, tickers[selected_ticker]
#             print("❗ 1~50번 사이의 숫자를 입력하세요.")
#         except ValueError:
#             print("❗ 숫자만 입력 가능합니다.")




def run_analysis():
    conn = init_db()
    rate = get_exchange_rate()

    # 시작 시 1년치 데이터 업데이트
    update_all_stocks_to_db(conn, rate)

    conn.close()

    # tickers_dict = get_top_50_tickers()
    #
    # while True:
    #     ticker, name = show_menu(tickers_dict)
    #     if not ticker: break
    #
    #     try:
    #         query = f"SELECT date, usd_price as USD, krw_price as KRW FROM daily_prices WHERE ticker = '{ticker}' ORDER BY date ASC"
    #         df = pd.read_sql(query, conn)
    #
    #         # 그래프 시각화 (365일치)
    #         fig, ax = plt.subplots(figsize=(14, 12))
    #         plt.subplots_adjust(bottom=0.4)
    #
    #         # 데이터가 많으므로 점(marker)을 작게 하거나 선(line)만 강조
    #         ax.plot(df['date'], df['KRW'], color='#1f77b4', lw=1.5, label='원화(KRW)')
    #         ax.set_title(f"{name} ({ticker}) 최근 1년 추이", fontsize=18, pad=30, fontweight='bold')
    #
    #         # x축 날짜 표시 최적화 (데이터가 많으므로 일부만 표시)
    #         xticks = ax.get_xticks()
    #         ax.set_xticks(xticks[::max(1, len(xticks) // 15)])
    #
    #
    #
    #         ax.grid(True, linestyle=':', alpha=0.6)
    #         plt.xticks(rotation=45)
    #
    #         # 하단 표 (최근 10일치 요약)
    #         table_df = df.tail(10)
    #         table_data = [[r['date'], f"${r['USD']:,.2f}", f"{r['KRW']:,.0f}원"] for _, r in table_df.iterrows()]
    #         the_table = ax.table(cellText=table_data, colLabels=["날짜", "USD", "KRW"],
    #                              loc='bottom', cellLoc='center', bbox=[0, -0.6, 1, 0.45])
    #         the_table.auto_set_font_size(False)
    #         the_table.set_fontsize(13)
    #         the_table.scale(1, 2.0)
    #
    #         for k in range(3):
    #             the_table[(0, k)].set_facecolor("#333333")
    #             the_table[(0, k)].set_text_props(color='white', fontweight='bold')
    #
    #         plt.show()
    #
    #     except Exception as e:
    #         print(f"❌ 조회 오류: {e}")
    #
    #         conn.close()

if __name__ == "__main__":
    run_analysis()



