import yfinance as yf
import pandas as pd
import os
import ssl
import warnings

# 1. 환경 설정: SSL 및 경고 메시지 무시
ssl._create_default_https_context = ssl._create_unverified_context
os.environ['CURL_CA_BUNDLE'] = "" # curl_cffi 보안 우회
warnings.filterwarnings('ignore')

def get_us_stock_data(ticker_symbol, period="1mo", interval="1d"):
    """
    미국 주식 데이터를 가져와서 출력 및 저장하는 함수
    period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
    """
    print(f"\n[정보] {ticker_symbol} 데이터를 불러오는 중...")

    try:
        # Ticker 객체 생성 (session 설정 없이 최신 yfinance 방식 사용)
        stock = yf.Ticker(ticker_symbol)

        # 주가 히스토리 가져오기
        df = stock.history(period=period, interval=interval)

        if df.empty:
            print(f"[오류] {ticker_symbol} 데이터를 찾을 수 없습니다. 티커를 확인하세요.")
            return None

        # 기업 기본 정보 (종목명, 현재가, 배당수익률 등)
        info = stock.info
        company_name = info.get('longName', ticker_symbol)
        current_price = info.get('currentPrice', 'N/A')

        print(f"--- {company_name} ({ticker_symbol}) ---")
        print(f"현재가: ${current_price}")
        print(df.tail()) # 최근 5일 데이터 출력

        # CSV 파일로 저장
        filename = f"{ticker_symbol}_history.csv"
        df.to_csv(filename)
        print(f"\n[완료] 데이터가 '{filename}'으로 저장되었습니다.")

        return df

    except Exception as e:
        print(f"[예외 발생] 데이터를 가져오는 중 오류가 발생했습니다: {e}")
        return None

if __name__ == "__main__":
    # 테스트용: 애플(AAPL)과 테슬라(TSLA) 데이터 가져오기
    tickers = ["AAPL", "TSLA"]
    for t in tickers:
        get_us_stock_data(t)