# ========================================================================
# [FI.db sqlite 파일 만들기]
# FI_0001.py, FI_0002.py, FI_0001.py 사용하여 실행파일 만들기
# pyinstaller --onefile FI_0001.py
#
# [requirements.txt 파일 만들기]
# pip freeze > requirements.txt
# ------------------------------------------------------------------------
# DB방법1 : [로컬 pc에서 파이썬 3.12.10 개발환경에서 빌드후 실행화일 실행하여 FI.db 업데이트됨
# DB방법2: python FI_0001.py 실행
#          python FI_0002.py 실행
#          python FI_0003.py 실행
# ==>FI.db 업데이트됨
# ==> GitHub 에 Push 작업필요]
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
# [배포정보]
# 사이트 https://share.streamlit.io/
# [Github] stepjump@naver.com
# Repository ==> stock_info
# https://stockinfo-o4ubhhwjex3cxshshbzgei.streamlit.app/
# ========================================================================
# ★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★
# [배포 하는법]
# git pull
# git add .
# git commit -m "update app"
# git push origin main
# ★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★
# # 초기화
# git pull origin main --rebase
# git push origin main
# ★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★
# [배포 시도시 충돌났을때 처리]
# git stash
# git pull origin main
# git stash pop
# git push -f origin main
# ★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★
# ========================================================================
# streamlit 터미널에서 실행
# streamlit run FI-WEB1.py --server.enableCORS false --server.enableXsrfProtection false
# ========================================================================


import base64
import subprocess
import sys
import requests
import streamlit as st
import sqlite3
import pandas as pd
import os
import pytz
from datetime import datetime
import streamlit as st
import yfinance as yf


# 현재 파일이 있는 폴더를 파이썬 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from ANALYZE import run_analysis # 분석 로직이 담긴 함수를 import
 


# ==================================================================================
# 서비스 접속시 비밀번호 인증 
# ==================================================================================
# 1. 세션 상태에 인증 여부 저장
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

def check_password():
    # 2. 비밀번호 입력받기
    password = st.text_input("비밀번호를 입력하세요:", type="password")
    if password == "4978": # 여기에 원하시는 비밀번호 설정
        st.session_state.authenticated = True
        st.rerun() # 인증 성공 시 화면 새로고침
    elif password != "":
        st.error("비밀번호가 틀렸습니다.")
        st.stop() # 인증 실패 시 아래 코드 실행 중단

# 3. 인증되지 않았다면 로그인 화면만 보여줌
if not st.session_state.authenticated:
    check_password()
    st.stop() # 이후 내용 표시 중단

# 4. 인증 성공 시 여기에 원래 만드신 웹 앱 코드를 작성하세요
st.title("환영합니다!")
st.write("이제 서비스가 표시됩니다.")
# ==================================================================================

# ==================================================================================
# 분석 페이지로 이동
# ==================================================================================
# 1. 팝업 창 정의
@st.dialog("종목 분석 시스템", width="large")
def show_analysis_modal():
    st.write("### 50개 종목 데이터 분석 중...")
    # 여기서 ANALYZE.py의 로직 실행
    run_analysis()
    
    if st.button("닫기"):
        st.rerun()

# 2. 메인 페이지의 빨간색 버튼
if st.button("분석 페이지로 이동", type="primary"):
    # 스타일을 위한 마크다운 (빨간색 강조)
    st.markdown("""
        <style>
        div.stButton > button:first-child {
            background-color: #FF4B4B;
            color: white;
        }
        </style>
    """, unsafe_allow_html=True)
    show_analysis_modal()
# ==================================================================================   


# ==================================================================================
# 한국 현재시간, 미국 현재시간 표시
# ==================================================================================
# 1. 시간대 설정
kst = pytz.timezone('Asia/Seoul')
est = pytz.timezone('US/Eastern')  # 미국 동부 기준 (뉴욕 등)

# 2. 현재 시간 가져오기
now_kst = datetime.now(kst)
now_est = datetime.now(est)

# 3. 시간 표시 형식 지정 (년-월-일 시:분:초)
time_format = '%Y-%m-%d %H:%M:%S'

# 4. 화면 레이아웃 구성
col1, col2 = st.columns(2)

with col1:
    st.write("### 한국 시간 (KST)")
    st.info(now_kst.strftime(time_format))

with col2:
    st.write("### 미국 시간 (EST)")
    st.info(now_est.strftime(time_format))

st.divider() # 하단 구분선
# ==================================================================================


# ==================================================================================
# 파일 수정한 시간 구하기
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
program_path = os.path.join(BASE_DIR, 'FI-WEB1.py')
timestamp = os.path.getmtime(program_path)
last_modified_date = f"[프로그램 수정시간 : {datetime.fromtimestamp(timestamp, tz=pytz.timezone('Asia/Seoul')).strftime('%Y-%m-%d %H:%M')}]"
# ==================================================================================

# ==================================================================================
# 페이지 설정
st.set_page_config(layout="wide", page_title="가치투자 주식 대시보드")
# ==================================================================================

# ==================================================================================
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
# ==================================================================================


# ==================================================================================
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

        st.title(f"📈 {target_stock} 분석 리포트 " + last_modified_date)

        # 상단: 가치투자 주요 지표
        st.subheader("📌 주요 가치 지표")
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("현재가", f"{stock_info['close']:,}")
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
# ==================================================================================



