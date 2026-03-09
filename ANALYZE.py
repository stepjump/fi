import yfinance as yf
import pandas as pd
import streamlit as st

def run_analysis():

    # 1. 분석할 종목 리스트 (50개 예시)
    tickers = [ 
                # 기술/성장주
                "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "AMD", "INTC", "ADBE",            
                "CRM", "ORCL", "CSCO", "QCOM", "AVGO", "TXN", "IBM", "NFLX", "PYPL", "SNOW",
                # 금융/소비재
                "JPM", "BAC", "WFC", "GS", "MS", "V", "MA", "AXP", "KO", "PEP",
                "MCD", "WMT", "COST", "PG", "DIS", "NKE", "HD", "LOW", "TGT", "SBUX",
                # 에너지/산업/기타
                "XOM", "CVX", "BA", "CAT", "MMM", "GE", "HON", "UPS", "LMT", "PFE"]


    def analyze_stocks(tickers):
        results = []
        
        for ticker in tickers:
            try:
                # 2. 최근 10일간의 데이터 수집
                df = yf.download(ticker, period="10d", interval="1d", progress=False)
                
                # 3. 데이터가 부족하면 건너뜀
                if len(df) < 2: continue
                
                # 4. 기술적 지표 계산: 거래량 급증 확인
                recent_volume = df['Volume'].iloc[-1]
                avg_volume = df['Volume'].iloc[-5:-1].mean()
                
                # 5. 종가 기준 상승률 확인
                price_change = ((df['Close'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
                
                # 6. 필터링 조건: 거래량이 평균의 2배 이상 AND 가격이 상승 중
                if recent_volume > avg_volume * 2 and price_change > 0:
                    results.append({
                        "종목": ticker,
                        "현재가격": round(df['Close'].iloc[-1], 2),
                        "상승률(%)": round(price_change, 2),
                        "거래량급증비율": round(recent_volume / avg_volume, 2)
                    })


                # Streamlit 화면 출력
                st.title("📊 실시간 종목 분석 자동화")
                if st.button("분석 시작"):
                    with st.spinner("50개 종목 데이터 분석 중..."):
                        df_result = analyze_stocks(tickers)
                        if not df_result.empty:
                            st.dataframe(df_result.sort_values(by="상승률(%)", ascending=False))
                        else:
                            st.write("현재 조건에 맞는 종목이 없습니다.")
                            
                    st.dataframe(df) # 팝업 창 안에서 표가 출력됩니다.

            except Exception as e:
                continue
                
            return pd.DataFrame(results)



# 단독 실행을 위한 코드
if __name__ == "__main__":
    run_analysis()


