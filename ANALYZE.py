import os
import streamlit as st
import pandas as pd
from sqlalchemy import URL, create_engine

def run_analysis():


    # 데이터베이스 연결
    # 객체를 사용하여 안전하게 생성
    db_url = URL.create(
        drivername="sqlite",
        database="FI.db"  # 여기에 실제 파일명을 입력하세요
    )
    engine = create_engine(db_url)


    query = "SELECT * FROM daily_total_info"
    df = pd.read_sql(query, engine)

    # 1. 이상치 및 결측치 처리 (None 처리)
    df = df.fillna(0)

    # 2. 급등 예상 점수 계산 (알고리즘)
    # PEG가 1 미만(성장성), ROE가 15% 이상(수익성), PBR이 2 이하(가치)인 종목에 가점
    df['score'] = 0
    df.loc[(df['PEG'] > 0) & (df['PEG'] < 1.0), 'score'] += 40
    df.loc[df['ROE'] > 15, 'score'] += 30
    df.loc[df['PBR'] < 2.0, 'score'] += 30

    # 점수순으로 정렬
    top_stocks = df.sort_values(by='score', ascending=False).head(10)

    # 3. Streamlit 화면 출력
    st.subheader("🎯 재무 지표 기반 급등 예상 종목 TOP 10")
    st.write("재무 건전성이 우수하여 수급이 몰릴 경우 단기 급등 가능성이 높은 종목입니다.")

    # 결과 표 출력 (가독성을 위한 스타일링)
    st.dataframe(
        top_stocks[['ticker', 'name', 'krw_price', 'ROE', 'PEG', 'score']]
        .style.highlight_max(axis=0, subset=['score'], color='#FF4B4B')
    )

if __name__ == "__main__":
    run_analysis()