import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(
    page_title="US Stock Dashboard 200+ (BMNR)",
    page_icon="📈",
    layout="wide"
)


# 2. 실시간 데이터 수집 및 변동성 분석 함수
# 캐시를 사용하되, 버튼 클릭 시 clear_cache()를 통해 초기화 가능하게 설정
@st.cache_data(ttl=3600)
def get_market_data():
    # 비트마인(BMNR) + 주요 200개 종목 리스트
    tickers = [
        'BMNR', 'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'BRK.B', 'TSLA', 'V',
        'UNH', 'LLY', 'MA', 'JPM', 'JNJ', 'XOM', 'AVGO', 'PG', 'HD', 'ORCL', 'ADBE',
        'ASML', 'COST', 'CVX', 'ABBV', 'MRK', 'KO', 'PEP', 'BAC', 'TMO', 'AZN',
        'CRM', 'FMX', 'LIN', 'NVO', 'AMD', 'MCD', 'ACN', 'CSCO', 'ABT', 'TMUS',
        'DHR', 'INTU', 'GE', 'WMT', 'VZ', 'DIS', 'TXN', 'NEE', 'PM', 'AMAT',
        'RTX', 'PFE', 'IBM', 'LOW', 'HON', 'UNP', 'GS', 'CAT', 'INTC', 'CMCSA',
        'QCOM', 'ISRG', 'BKNG', 'NOW', 'AXP', 'SPGI', 'AMGN', 'SYK', 'MDLZ', 'VRTX',
        'PLD', 'MU', 'GILD', 'ADP', 'ADI', 'LMT', 'TJX', 'ETN', 'BLK', 'CVS',
        'BSX', 'MMC', 'AMT', 'REGN', 'LRCX', 'PANW', 'DE', 'EQIX', 'CB', 'PGR',
        'ZTS', 'SCHW', 'FI', 'CI', 'CDNS', 'SNPS', 'KLAC', 'C', 'BDX',
        'ELV', 'WM', 'ITW', 'HCA', 'MAR', 'ICE', 'APH', 'EOG', 'MCK',
        'MCO', 'GD', 'ADSK', 'PH', 'CTAS', 'T', 'FTNT', 'TDG', 'ORLY', 'AON',
        'NXPI', 'SLB', 'ECL', 'PCAR', 'MSI', 'EMR', 'ROP', 'AJG', 'CRWD', 'MNST',
        'HUM', 'DASH', 'MARA', 'COIN', 'MSTR', 'ABNB', 'UBER', 'SNOW', 'TEAM', 'WDAY',
        'PYPL', 'SQ', 'SHOP', 'NET', 'DDOG', 'OKTA', 'ZS', 'MDB', 'PLTR', 'U',
        'RIVN', 'LCID', 'DKNG', 'PINS', 'SNAP', 'TTD', 'ROKU', 'AFRM', 'UPST', 'HOOD',
        'SOFI', 'F', 'GM', 'X', 'NUE', 'FCX', 'AAL', 'DAL', 'UAL', 'LUV',
        'O', 'STAG', 'VICI', 'MPW', 'NEM', 'GOLD', 'TSM', 'SE', 'CPNG', 'MELI',
        'PDD', 'BABA', 'JD', 'BIDU', 'LI', 'NIO', 'XPEV', 'TME', 'NTES', 'BEKE'
    ]
    unique_tickers = []
    for t in tickers:
        if t not in unique_tickers: unique_tickers.append(t)

    # 현재 시간 기록 (년-월-일 시:분:초)
    update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        # 실시간 환율 및 주가 데이터 수집
        ex_df = yf.download("USDKRW=X", period="1d", interval="1m")
        current_rate = float(ex_df['Close'].iloc[-1])
        raw_data = yf.download(unique_tickers, period="10d", interval="1d")['Close'].ffill()
        current_prices = raw_data.iloc[-1]
        volatility = raw_data.pct_change().dropna().std()
    except Exception:
        current_rate = 1350.0
        current_prices = pd.Series([0.0] * len(unique_tickers), index=unique_tickers)
        volatility = pd.Series([0.0] * len(unique_tickers), index=unique_tickers)

    stock_list = []
    for i, ticker in enumerate(unique_tickers, 1):
        price_usd = float(current_prices.get(ticker, 0.0))
        est_move = (volatility.get(ticker, 0.0) * 1.732 * 100)

        status = "🔴 높음 (3%↑)" if est_move >= 3.0 else ("🟡 보통 (1%↑)" if est_move >= 1.0 else "🟢 낮음")

        stock_list.append({
            'No.': i,
            'Ticker': ticker,
            'Price (USD)': f"$ {price_usd:,.2f}",
            'Price (KRW)': f"₩ {int(price_usd * current_rate):,}" if price_usd > 0 else "N/A",
            'Volatility_3D': status,
            'Est_Move_%': round(est_move, 2)
        })

    full_df = pd.DataFrame(stock_list)
    full_df['Sort_Key'] = full_df['Ticker'].apply(lambda x: 0 if x == 'BMNR' else 1)
    full_df = full_df.sort_values(by=['Sort_Key', 'No.']).drop(columns=['Sort_Key'])
    full_df['No.'] = range(1, len(full_df) + 1)

    return full_df, current_rate, update_time


# 3. 사이드바 구성 및 데이터 로딩
st.sidebar.header("🔍 FI-WEB 분석 설정")

# --- [추가] 새로고침 버튼 ---
if st.sidebar.button("🔄 실시간 데이터 새로고침", use_container_width=True):
    st.cache_data.clear()  # 캐시 데이터 전체 삭제
    st.rerun()  # 앱 재실행을 통해 데이터 다시 호출

view_option = st.sidebar.selectbox("조회 모드", ["전체 종목 보기", "변동성 종목만 보기 (1%↑)"])
search_q = st.sidebar.text_input("종목 코드 직접 검색", "").upper()

with st.spinner('최신 데이터를 불러오는 중...'):
    df, exchange_rate, last_update = get_market_data()

# 필터링 로직
filtered_df = df[df['Ticker'].str.contains(search_q)]
if view_option == "변동성 종목만 보기 (1%↑)":
    filtered_df = filtered_df[(filtered_df['Est_Move_%'] >= 1.0) | (filtered_df['Ticker'] == 'BMNR')]

# 4. 메인 화면 구성
st.title("📊 US Market Real-time FI Dashboard")

c1, c2 = st.columns(2)
with c1:
    st.metric(label="현재 원/달러 환율", value=f"{exchange_rate:,.2f} 원")
with c2:
    st.write(f"⏱️ **최종 업데이트 시각:** `{last_update}`")
    st.info(f"조회된 종목: **{len(filtered_df)}**개")


# 스타일링 함수: BMNR 행 하이라이트
def highlight_bmnr(row):
    return ['background-color: #fff9c4; font-weight: bold;' if row.Ticker == 'BMNR' else '' for _ in row]


# 5. 테이블 출력
st.dataframe(
    filtered_df.style.apply(highlight_bmnr, axis=1),
    use_container_width=True,
    hide_index=True,
    height=2000 if len(filtered_df) < 50 else 6000,
    column_config={
        "No.": st.column_config.TextColumn("No.", width=50),
        "Ticker": st.column_config.TextColumn("Ticker", width=100),
        "Price (USD)": st.column_config.TextColumn("현재가($)"),
        "Price (KRW)": st.column_config.TextColumn("현재가(₩)"),
        "Volatility_3D": st.column_config.TextColumn("3일 변동성"),
        "Est_Move_%": st.column_config.NumberColumn("예상변동(%)", format="%.2f%%")
    }
)

st.divider()
st.caption("비트마인(BMNR)은 사용자 설정에 의해 항상 최상단에 고정 표시됩니다.")