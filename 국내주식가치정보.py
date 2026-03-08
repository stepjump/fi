#국내주식전용 가치정보 가져오기

import requests
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_korean_stock_metrics(ticker):
    # 네이버 증권 종목분석 페이지
    url = f"https://finance.naver.com/item/main.naver?code={ticker}"
    headers = {'User-Agent': 'Mozilla/5.0'}

    res = requests.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(res.text, 'html.parser')

    # 주요 지표가 포함된 테이블 탐색
    content = soup.find('div', {'class': 'section cop_analysis'})
    if not content: return "데이터를 찾을 수 없습니다."

    # 테이블 내의 텍스트 데이터 추출
    # (네이버는 보통 최근 분기/연도 데이터를 테이블로 제공함)
    metrics = {}
    rows = content.find('table').find_all('tr')

    for row in rows:
        title = row.find('th').get_text(strip=True) if row.find('th') else ""
        data = row.find_all('td')
        if data:
            # 가장 최근 연도 데이터(보통 4번째 칸) 추출
            metrics[title] = data[3].get_text(strip=True)

    return metrics


# 삼성전자(005930) 테스트
print(get_korean_stock_metrics("005930"))