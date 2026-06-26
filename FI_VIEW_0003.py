import sqlite3
import os
import sys
import tkinter as tk
from tkinter import messagebox, ttk


class FIViewApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FI.db 데이터 조회 시스템 (전체 컬럼)")
        self.root.geometry("1200x700")  # 화면을 조금 더 넓게 설정

        self.db_name = "FI.db"
        self.table_name = "daily_total_info"

        if not os.path.exists(self.db_name):
            messagebox.showerror("오류", f"'{self.db_name}' 파일을 찾을 수 없습니다.")
            self.root.destroy()
            return

        # 사용자가 제공한 14개 전체 컬럼 정의
        self.columns = (
            "ticker", "name", "date", "usd_price", "krw_price", "close",
            "PER", "PBR", "PSR", "PCR", "ROE", "EPS", "PEG", "DIVIDEND_YIELD"
        )
        self.setup_ui()

    def setup_ui(self):
        # 상단 입력 프레임
        input_frame = tk.Frame(self.root, pady=10)
        input_frame.pack(side=tk.TOP, fill=tk.X)

        tk.Label(input_frame, text="종목코드:").grid(row=0, column=0, padx=5)
        self.ent_ticker = tk.Entry(input_frame, width=10)
        self.ent_ticker.grid(row=0, column=1, padx=5)

        tk.Label(input_frame, text="시작일:").grid(row=0, column=2, padx=5)
        self.ent_start = tk.Entry(input_frame, width=12)
        self.ent_start.grid(row=0, column=3, padx=5)

        tk.Label(input_frame, text="종료일:").grid(row=0, column=4, padx=5)
        self.ent_end = tk.Entry(input_frame, width=12)
        self.ent_end.grid(row=0, column=5, padx=5)

        btn_search = tk.Button(input_frame, text="조회하기", command=self.load_data, bg="#4CAF50", fg="white", width=10)
        btn_search.grid(row=0, column=6, padx=10)

        # 중앙 트리뷰 프레임 (세로/가로 스크롤바 포함)
        tree_container = tk.Frame(self.root)
        tree_container.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)

        vsb = ttk.Scrollbar(tree_container, orient="vertical")  # 세로 스크롤
        hsb = ttk.Scrollbar(tree_container, orient="horizontal")  # 가로 스크롤

        self.tree = ttk.Treeview(
            tree_container,
            columns=self.columns,
            show='headings',
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )

        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)

        # 스크롤바 배치
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        # 모든 컬럼 헤더 및 너비 설정
        for col in self.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="center")  # 기본 너비 100

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        ticker = self.ent_ticker.get().strip()
        start = self.ent_start.get().strip()
        end = self.ent_end.get().strip()

        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            # 모든 컬럼(*)을 조회
            query = f"SELECT * FROM {self.table_name} WHERE 1=1"
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
                messagebox.showinfo("결과", "데이터가 없습니다.")
            else:
                for row in rows:
                    self.tree.insert("", tk.END, values=row)

        except sqlite3.Error as e:
            messagebox.showerror("DB 에러", f"오류 발생: {e}")
        finally:
            if conn:
                conn.close()


if __name__ == "__main__":
    root = tk.Tk()
    app = FIViewApp(root)
    root.mainloop()