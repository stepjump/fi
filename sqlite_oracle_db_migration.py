# =======================================================================
# SQLite DB파일 FI.db 중 daily_total_info 테이블안의 값들을
# 오라클DB daily_total_info 테이블로 넣어주는 파이썬 코드
# [오라클 DB 접속정보]
# DB_USER = "STEPJUMP"
# DB_PASSWORD = "7312"
# DB_HOST = "localhost"
# DB_PORT = "1521"
# DB_SID = "orcl"   
# =======================================================================
# pip install oracledb
# pip install cryptography  #암호화 라이브러리
# python -m pip install cryptography
# =======================================================================
# pyinstaller -F --hidden-import=secrets --hidden-import=getpass --hidden-import=ssl --hidden-import=uuid --collect-all cryptography --copy-metadata cryptography sqlite_oracle_db_migration.py

import sqlite3
import oracledb

# ==========================================
# 1. 접속 정보 설정
# ==========================================
DB_USER = "STEPJUMP"
DB_PASSWORD = "7312"
DB_HOST = "localhost"
DB_PORT = "1521"
DB_SID = "orcl"

SQLITE_DB_FILE = "FI.db"  # 파이썬 스크립트와 같은 경로에 있다고 가정

def migrate_sqlite_to_oracle():
    sqlite_conn = None
    oracle_conn = None
    
    try:
        # ==========================================
        # 2. SQLite에서 데이터 읽기
        # ==========================================
        print("1. SQLite DB 파일 연결 중...")
        sqlite_conn = sqlite3.connect(SQLITE_DB_FILE)
        sqlite_cursor = sqlite_conn.cursor()
        
        # 생성 데이터 구조 순서대로 정확하게 Select 수행
        sqlite_select_query = """
            SELECT "ticker", "name", "date", "usd_price", "krw_price", "Close", 
                   "PER", "PBR", "PSR", "PCR", "ROE", "EPS", "PEG", "DIVIDEND_YIELD" 
            FROM daily_total_info
        """
        sqlite_cursor.execute(sqlite_select_query)
        rows = sqlite_cursor.fetchall() # 모든 데이터를 튜플 리스트로 가져옴
        
        total_rows = len(rows)
        print(f"-> SQLite 테이블에서 총 {total_rows}개의 행을 성공적으로 읽었습니다.")
        
        if total_rows == 0:
            print("이전할 데이터가 존재하지 않아 작업을 종료합니다.")
            return

        # ==========================================
        # 3. 오라클 DB 연결 (Thin 모드)
        # ==========================================
        print("\n2. 오라클 DB 연결 중...")

        # ⭐ 이 한 줄을 추가하면 오라클 구버전(11g 등) 호환 모드로 작동합니다.
        oracledb.init_oracle_client()

        # SID 형식을 위한 DSN 구조 생성
        dsn_string = oracledb.makedsn(DB_HOST, DB_PORT, sid=DB_SID)
        oracle_conn = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=dsn_string)
        oracle_cursor = oracle_conn.cursor()
        print("-> 오라클 데이터베이스 연결 성공.")


        # ==========================================
        # 1. 기존 데이터 전체 삭제 (TRUNCATE)
        # ==========================================
        print("\n[작업] 기존 오라클 테이블의 데이터를 모두 삭제합니다...")
        truncate_query = "TRUNCATE TABLE daily_total_info"
        oracle_cursor.execute(truncate_query)
        print("-> 기존 데이터 삭제 완료.")

        # 2. 대량 데이터 삽입 수행 (기존 코드)
        print("\n3. 오라클 DB로 데이터 전송 및 삽입 중...")        
        oracle_conn.commit()




        # ==========================================
        # 4. 오라클 Insert 쿼리 준비 (생성한 테이블에 맞춰 선택)
        # ==========================================
        
        # [선택 A] 예약어를 피해 컬럼명을 수정한 '추천 버전' 테이블인 경우 (기본값)
        oracle_insert_query = """
            INSERT INTO daily_total_info (
                ticker, name, info_date, usd_price, krw_price, close_price, 
                per, pbr, psr, pcr, roe, eps, peg, dividend_yield
            ) VALUES (
                :1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14
            )
        """
        
        # [선택 B] 만약 모든 컬럼명을 쌍따옴표로 대소문자 구분하여 똑같이 만든 경우
        # (만약 선택 B 유형으로 테이블을 만드셨다면 아래 11줄의 주석샵(#)을 해제하고 위 선택 A를 주석처리 하세요)
        # oracle_insert_query = """
        #     INSERT INTO "daily_total_info" (
        #         "ticker", "name", "date", "usd_price", "krw_price", "Close", 
        #         "PER", "PBR", "PSR", "PCR", "ROE", "EPS", "PEG", "DIVIDEND_YIELD"
        #     ) VALUES (
        #         :1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14
        #     )
        # """

        # ==========================================
        # 5. 대량 데이터 삽입 수행 및 커밋
        # ==========================================
        print("\n3. 오라클 DB로 데이터 전송 및 삽입 중...")
        
        # executemany는 고속 대량 삽입 처리를 지원하여 성능을 극대화합니다.
        oracle_cursor.executemany(oracle_insert_query, rows)
        
        # 오라클은 데이터 영구 반영을 위해 commit이 필수입니다.
        oracle_conn.commit()
        print(f"-> 완료: 총 {oracle_cursor.rowcount}개의 데이터가 오라클 DB로 안전하게 이관되었습니다.")
        
    except sqlite3.Error as se:
        print(f"\n[SQLite 오류] {se}")
    except oracledb.DatabaseError as oe:
        print(f"\n[오라클 DB 오류] {oe}")
    except Exception as e:
        print(f"\n[기타 오류] {e}")
        
    finally:
        # ==========================================
        # 6. 사용한 DB 자원 해제
        # ==========================================
        if sqlite_conn:
            sqlite_conn.close()
            print("\nSQLite 연결 해제 완료.")
        if oracle_conn:
            oracle_conn.close()
            print("오라클 연결 해제 완료.")

if __name__ == "__main__":
    migrate_sqlite_to_oracle()

    