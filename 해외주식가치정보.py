import requests
from bs4 import BeautifulSoup
import pandas as pd
import urllib3

# SSL 경고 무시
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_finviz_metrics(ticker):
    url = f"https://finviz.com/quote.ashx?t={ticker.upper()}"

    # 핀비즈는 봇 차단이 강력하므로 User-Agent 설정이 필수입니다.
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, verify=False, timeout=10)
        if response.status_code != 200:
            return f"Error: 서버 응답 코드 {response.status_code}"

        soup = BeautifulSoup(response.text, 'html.parser')

        # 지표가 담긴 테이블 찾기 (snapshot-table2 클래스)
        table = soup.find('table', {'class': 'snapshot-table2'})
        if not table:
            return "지표 테이블을 찾을 수 없습니다."

        # 모든 셀(td) 데이터 추출
        tds = table.find_all('td')
        data_map = {}
        for i in range(0, len(tds), 2):
            label = tds[i].text.strip()
            value = tds[i + 1].text.strip()
            data_map[label] = value

        # 요청하신 8가지 지표 매핑 (Finviz 용어에 맞춤)
        # PCR과 EV/EBITDA는 상세 페이지에 따라 없을 수 있어 기본 지표 위주 구성
        metrics = {
            "TICKER": ticker.upper(),
            "PER": data_map.get("P/E"),
            "PBR": data_map.get("P/B"),
            "PSR": data_map.get("P/S"),
            "EPS (ttm)": data_map.get("EPS (ttm)"),
            "ROE": data_map.get("ROE"),
            "PEG": data_map.get("PEG"),
            "Dividend %": data_map.get("Dividend %"),  # 배당 수익률
            "Price": data_map.get("Price")
        }

        return metrics

    except Exception as e:
        return f"에러 발생: {e}"


# 실행 테스트 (애플, 테슬라, 엔비디아)
target_stocks = ["AAPL", "MSFT", "NVDA", "GOOGL",
		        "AMZN", "META", "BRK-B", "TSLA",
		        "AVGO", "LLY", "V", "TSM",
                "UNH", "JPM", "MA", "XOM",
                "JNJ", "PG", "COST", "HD",
                "ORCL", "ADBE", "ASML", "CVX",
                "TM", "MRK", "ABBV", "BAC",
                "KO", "PEP", "NFLX", "LIN",
                "CRM", "AMD", "DIS", "TMO",
                "WMT", "WFC", "ACN", "INTC",
                "WMT", "WFC", "ACN", "INTC",
                "CSCO", "PFE", "VZ", "ADI",
                "WMT", "WFC", "ACN", "INTC",
                "QCOM", "CAT", "TXN", "DHR",
                "WMT", "WFC", "ACN", "INTC",
                "AMGN", "IBM"]


for stock in target_stocks:
    print(f"\n[ {stock} 주요 가치평가 지표 ]")
    result = get_finviz_metrics(stock)
    if isinstance(result, dict):
        for k, v in result.items():
            print(f"{k}: {v}")
    else:
        print(result)

