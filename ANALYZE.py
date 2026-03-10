import os
import streamlit as st
import pandas as pd
from sqlalchemy import URL, create_engine

def run_analysis():

    # 1. 파일의 현재 위치를 기준으로 절대 경로 계산
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 2. 로컬(Codespaces)과 배포 환경 모두에서 동작하도록 경로 설정
    # 파일이 같은 폴더에 있다고 가정합니다.
    db_path = os.path.join(base_dir, 'FI.db')
    
    # 3. SQLAlchemy 연결 문자열 생성 (슬래시 3개 사용)
    # Windows/Linux 상관없이 호환되는 sqlite:/// 경로 방식
    db_url = f"sqlite:///{db_path}"
    
    try:
        engine = create_engine(db_url)
        # 데이터 가져오기
        query = "SELECT * FROM daily_total_info"
        df = pd.read_sql(query, engine)
        
        st.write("데이터 로드 성공!", df.head())
        
    except Exception as e:
        st.error(f"데이터베이스 연결 오류: {e}")
        st.write(f"시도한 경로: {db_url}") # 로그 확인용



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