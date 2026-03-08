# ========================================================================
# [FI.db sqlite 파일 만들기]
# FI_0001.py, FI_0002.py, FI_0001.py 사용하여 실행파일 만들기
# pyinstaller --onefile FI_0001.py
# ------------------------------------------------------------------------
# FI_0001.exe 실행    ===> daily_prices 테이블 생성
# FI_0002.exe 실행    ===> daily_prices2 테이블 생성
# FI_0003.exe 실행    ===> daily_total_info 테이블 생성
# 3파일을 실행하면 daily_total_info 주테이블이 만들어진다.
# ========================================================================
# ========================================================================
# [실행]
# streamlit run FI-WEB-0001.py
# ========================================================================
# ========================================================================
# [배포]
# 사이트 https://share.streamlit.io/
# [Github] stepjump@naver.com
# Repository ==> stock_info
# https://stockinfo-o4ubhhwjex3cxshshbzgei.streamlit.app/
#
# ========================================================================
# # git commit, push
# git add .
# git commit -m "update app"
# git push origin main

# # 초기화
# git pull origin main --rebase
# git push origin main
# ========================================================================


import streamlit as st
import sqlite3
import pandas as pd
import os
import time

# 페이지 설정
st.set_page_config(layout="wide", page_title="가치투자 주식 대시보드")

# DB 연결 함수
def get_data():
    # 이 파일(FI-WEB1.py)이 있는 절대 경로를 구함
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, 'FI.db')


    # conn = sqlite3.connect('FI.db')  # 본인의 db 파일명으로 수정하세요\
    conn = sqlite3.connect(db_path)  # 본인의 db 파일명으로 수정하세요
    query = "SELECT * FROM daily_total_info"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# 데이터 로드
df = get_data()

# --- 사이드바 (왼쪽 화면) ---
st.sidebar.title("🔍 종목 선택 및 필터")

# 데이터가 비어있는지 먼저 확인
if df.empty:
    st.error("DB에 데이터가 없습니다. 데이터 수집을 먼저 진행해 주세요.")
else:
    # 가치투자 필터 기능
    if st.sidebar.checkbox("가치투자 우량주만 보기"):
        filtered_df = df[(df['PER'] > 0) & (df['PBR'] < 30) & (df['ROE'] > 5)]
    else:
        filtered_df = df

    if filtered_df.empty:
        st.sidebar.warning("조건에 맞는 종목이 없습니다.")
        target_stock = None
    else:
        # 종목 리스트 생성
        filtered_df['display_name'] = filtered_df['ticker'] + " (" + filtered_df['name'] + ")"
        # selectbox에서 아무것도 선택되지 않았을 때를 대비해 index=0 설정
        target_stock = st.sidebar.selectbox("종목을 선택하세요", filtered_df['display_name'].unique())

    # --- 메인 화면 (오른쪽 화면) ---
    if target_stock:  # target_stock이 None이 아닐 때만 실행
        selected_ticker = target_stock.split(" (")[0]

        # 데이터 추출
        stock_info = df[df['ticker'] == selected_ticker].iloc[0]
        history_info = df[df['ticker'] == selected_ticker].sort_values(by='date', ascending=False)

        st.title(f"📈 {target_stock} 분석 리포트")

        # 상단: 가치투자 주요 지표
        st.subheader("📌 주요 가치 지표")
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("현재가 [" + time.strftime('%Y.%m.%d - %H:%M') + "]", f"{stock_info['close']:,}")
        with col2:
            st.metric("PER", f"{stock_info['PER']:.2f}")
        with col3:
            st.metric("PBR", f"{stock_info['PBR']:.2f}")
        with col4:
            st.metric("ROE", f"{stock_info['ROE']:.2f}%")
        with col5:
            st.metric("PEG", f"{stock_info['PEG']:.2f}")

        st.divider()

        # 하단: 전체 데이터 테이블
        st.subheader("📋 전체 데이터 내역")
        st.dataframe(history_info, use_container_width=True)

        # 시각화 추가 (옵션: 주가 흐름)
        st.subheader("📊 주가 추이")
        st.line_chart(history_info.set_index('date')['close'])

    else:
        st.info("왼쪽 사이드바에서 종목을 선택해 주세요.")

