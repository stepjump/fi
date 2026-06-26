import sqlite3
import os
import sys
import tkinter as tk
from tkinter import messagebox, ttk
from tkcalendar import DateEntry


class FIViewApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FI.db 금융 데이터 조회 시스템 (리스트 선택형)")
        self.root.geometry("1350x800")

        self.db_name = "FI.db"
        self.table_name = "daily_total_info"

        # 1. 파일 확인 및 초기화
        if not os.path.exists(self.db_name):
            messagebox.showerror("오류", f"'{self.db_name}' 파일을 찾을 수 없습니다.")
            self.root.destroy()
            return

        self.columns = (
            "ticker", "name", "date", "usd_price", "krw_price", "close",
            "PER", "PBR", "PSR", "PCR", "ROE", "EPS", "PEG", "DIVIDEND_YIELD"
        )

        # DB에서 종목 리스트 가져오기
        self.ticker_list = self.get_ticker_list()

        self.setup_ui()

    def get_ticker_list(self):
        """DB에서 현재 존재하는 모든 종목코드를 가져와 리스트로 반환"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute(f"SELECT DISTINCT ticker FROM {self.table_name} ORDER BY ticker ASC")
            tickers = [row[0] for row in cursor.fetchall()]
            conn.close()
            return ["전체 조회"] + tickers  # 기본값 추가
        except Exception as e:
            print(f"종목 리스트 로딩 실패: {e}")
            return ["전체 조회"]

    def setup_ui(self):
        # 상단 제어 프레임
        control_frame = tk.LabelFrame(self.root, text="조회 필터", padx=15, pady=15)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        # 1. 종목코드 선택 (Combobox)
        tk.Label(control_frame, text="종목코드 선택:").grid(row=0, column=0, padx=5)
        self.combo_ticker = ttk.Combobox(control_frame, values=self.ticker_list, width=15, state="readonly")
        self.combo_ticker.current(0)  # '전체 조회' 선택
        self.combo_ticker.grid(row=0, column=1, padx=5)

        # 2. 시작일/종료일 달력
        tk.Label(control_frame, text="시작일:").grid(row=0, column=2, padx=5)
        self.cal_start = DateEntry(control_frame, width=12, background='darkblue', date_pattern='yyyy-mm-dd')
        self.cal_start.grid(row=0, column=3, padx=5)

        tk.Label(control_frame, text="종료일:").grid(row=0, column=4, padx=5)
        self.cal_end = DateEntry(control_frame, width=12, background='darkblue', date_pattern='yyyy-mm-dd')
        self.cal_end.grid(row=0, column=5, padx=5)

        # 3. 버튼
        btn_search = tk.Button(control_frame, text="데이터 검색", command=self.load_data,
                               bg="#28a745", fg="white", font=('맑은 고딕', 10, 'bold'), width=12)
        btn_search.grid(row=0, column=6, padx=20)

        # 트리뷰(표) 설정 및 스크롤바
        tree_container = tk.Frame(self.root)
        tree_container.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)

        vsb = ttk.Scrollbar(tree_container, orient="vertical")
        hsb = ttk.Scrollbar(tree_container, orient="horizontal")

        self.tree = ttk.Treeview(
            tree_container,
            columns=self.columns,
            show='headings',
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )

        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        for col in self.columns:
            self.tree.heading(col, text=col.upper())
            self.tree.column(col, width=100, anchor="center")

    def load_data(self):
        # 기존 표 내용 지우기
        for item in self.tree.get_children():
            self.tree.delete(item)

        selected_ticker = self.combo_ticker.get()
        start = self.cal_start.get_date().strftime('%Y-%m-%d')
        end = self.cal_end.get_date().strftime('%Y-%m-%d')

        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            # 기본 쿼리 (날짜 범위 우선)
            query = f"SELECT * FROM {self.table_name} WHERE date BETWEEN ? AND ?"
            params = [start, end]

            # 종목 선택이 '전체 조회'가 아닐 때만 ticker 조건 추가
            if selected_ticker != "전체 조회":
                query += " AND ticker = ?"
                params.append(selected_ticker)

            query += " ORDER BY date DESC"

            cursor.execute(query, params)
            rows = cursor.fetchall()

            if not rows:
                messagebox.showinfo("검색 결과", "해당 조건의 데이터가 없습니다.")
            else:
                for row in rows:
                    self.tree.insert("", tk.END, values=row)

        except sqlite3.Error as e:
            messagebox.showerror("에러", f"DB 에러: {e}")
        finally:
            if conn:
                conn.close()


if __name__ == "__main__":
    root = tk.Tk()
    app = FIViewApp(root)
    root.mainloop()