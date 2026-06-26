import sqlite3
import os
import sys
import tkinter as tk
from tkinter import messagebox, ttk


class FIViewApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FI.db 데이터 조회 시스템")
        self.root.geometry("1000x600")

        self.db_name = "FI.db"
        self.table_name = "daily_total_info"

        # 1. 파일 존재 확인 (시작하자마자 체크)
        if not os.path.exists(self.db_name):
            messagebox.showerror("오류", f"'{self.db_name}' 파일을 찾을 수 없습니다.\n프로그램을 종료합니다.")
            self.root.destroy()
            return

        self.setup_ui()

    def setup_ui(self):
        # 상단 입력부 프레임
        input_frame = tk.Frame(self.root, pady=10)
        input_frame.pack(side=tk.TOP, fill=tk.X)

        tk.Label(input_frame, text="종목코드:").grid(row=0, column=0, padx=5)
        self.ent_ticker = tk.Entry(input_frame, width=10)
        self.ent_ticker.grid(row=0, column=1, padx=5)

        tk.Label(input_frame, text="시작일(YYYY-MM-DD):").grid(row=0, column=2, padx=5)
        self.ent_start = tk.Entry(input_frame, width=12)
        self.ent_start.grid(row=0, column=3, padx=5)

        tk.Label(input_frame, text="종료일(YYYY-MM-DD):").grid(row=0, column=4, padx=5)
        self.ent_end = tk.Entry(input_frame, width=12)
        self.ent_end.grid(row=0, column=5, padx=5)

        btn_search = tk.Button(input_frame, text="조회하기", command=self.load_data, bg="#2196F3", fg="white")
        btn_search.grid(row=0, column=6, padx=10)

        # 중앙 데이터 표시부 (Treeview)
        self.tree_frame = tk.Frame(self.root)
        self.tree_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)

        # 스크롤바 추가
        scrollbar = tk.Scrollbar(self.tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 테이블 컬럼 설정 (사용자가 제공한 스키마 기준)
        self.columns = ("ticker", "name", "date", "usd_price", "krw_price", "close", "PER", "PBR", "ROE", "DIV_Y")
        self.tree = ttk.Treeview(self.tree_frame, columns=self.columns, show='headings', yscrollcommand=scrollbar.set)

        for col in self.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=80, anchor="center")

        self.tree.pack(expand=True, fill=tk.BOTH)
        scrollbar.config(command=self.tree.yview)

    def load_data(self):
        # 기존 내용 삭제
        for item in self.tree.get_children():
            self.tree.delete(item)

        ticker = self.ent_ticker.get().strip()
        start = self.ent_start.get().strip()
        end = self.ent_end.get().strip()

        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            query = f"SELECT ticker, name, date, usd_price, krw_price, close, PER, PBR, ROE, DIVIDEND_YIELD FROM {self.table_name} WHERE 1=1"
            params = []

            if ticker:
                query += " AND ticker = ?"
                params.append(ticker)
            if start and end:
                query += " AND date BETWEEN ? AND ?"
                params.extend([start, end])

            query += " ORDER BY date DESC"

            cursor.execute(query, params)
            rows = cursor.fetchall()

            if not rows:
                messagebox.showinfo("결과", "검색 조건에 맞는 데이터가 없습니다.")
            else:
                for row in rows:
                    self.tree.insert("", tk.END, values=row)

        except sqlite3.Error as e:
            messagebox.showerror("DB 에러", f"데이터를 가져오는 중 오류 발생: {e}")
        finally:
            if conn:
                conn.close()


if __name__ == "__main__":
    root = tk.Tk()
    app = FIViewApp(root)
    root.mainloop()