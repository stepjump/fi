import sqlite3
import os
import sys


def main():
    db_name = "FI.db"
    table_name = "daily_total_info"

    # 1. DB 파일 존재 여부 체크
    if not os.path.exists(db_name):
        print(f"❌ 오류: '{db_name}' 파일을 찾을 수 없습니다.")
        print("프로그램을 종료합니다.")
        sys.exit()

    # 2. 사용자로부터 조회 조건 입력 받기
    print("\n--- [ 데이터 조회 조건 입력 ] ---")
    search_ticker = input("1. 종목코드(ticker) 입력 (전체 조회는 엔터): ").strip()
    start_date = input("2. 조회 시작일자 (YYYY-MM-DD, 예: 2024-01-01): ").strip()
    end_date = input("3. 조회 종료일자 (YYYY-MM-DD, 예: 2024-12-31): ").strip()

    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # 3. 동적 쿼리 생성 (WHERE 절 구성)
        # 기본 쿼리: 전체 조회
        query = f"SELECT * FROM {table_name} WHERE 1=1"
        params = []

        # 종목코드 조건 추가
        if search_ticker:
            query += " AND ticker = ?"
            params.append(search_ticker)

        # 날짜 범위 조건 추가 (date 컬럼 기준)
        if start_date and end_date:
            query += " AND date BETWEEN ? AND ?"
            params.extend([start_date, end_date])

        # 최신순 정렬 (선택 사항)
        query += " ORDER BY date DESC"

        # 4. 쿼리 실행
        cursor.execute(query, params)
        column_names = [description[0] for description in cursor.description]
        rows = cursor.fetchall()

        # 5. 결과 출력
        print("\n" + "=" * 130)
        if not rows:
            print(f"🔍 검색 조건에 맞는 데이터가 없습니다. (입력값: {search_ticker}, {start_date} ~ {end_date})")
        else:
            print(f"✅ 총 {len(rows)}건의 데이터를 발견했습니다.")
            print("-" * 130)
            print(" | ".join(f"{name:^10}" for name in column_names))
            print("-" * 130)

            for row in rows:
                print(row)
        print("=" * 130)

    except sqlite3.Error as e:
        print(f"❌ 데이터베이스 에러: {e}")
    finally:
        if 'conn' in locals():
            conn.close()


if __name__ == "__main__":
    main()