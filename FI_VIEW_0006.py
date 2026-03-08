# ============================================================================
# 실행화일 만들기
# pyinstaller 가 인식되지않을때
# pip show pyinstaller 명령후 위치를 찾이못한다면   pip install pyinstaller
# pyinstaller --onefile FI_VIEW_0006.py
# ============================================================================

import sqlite3
import os
import sys
import csv
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from tkcalendar import DateEntry
import subprocess
import webbrowser

class FIViewApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FI.db 금융 데이터 조회 및 엑셀 저장 시스템")
        self.root.geometry("1400x800")

        self.db_name = "FI.db"
        self.table_name = "daily_total_info"

        if not os.path.exists(self.db_name):
            messagebox.showerror("오류", f"'{self.db_name}' 파일을 찾을 수 없습니다.")
            self.root.destroy()
            return

        self.columns = (
            "ticker", "name", "date", "usd_price", "krw_price", "close",
            "PER", "PBR", "PSR", "PCR", "ROE", "EPS", "PEG", "DIVIDEND_YIELD"
        )

        self.ticker_list = self.get_ticker_list()
        self.setup_ui()

    def get_ticker_list(self):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute(f"SELECT DISTINCT ticker FROM {self.table_name} ORDER BY ticker ASC")
            tickers = [row[0] for row in cursor.fetchall()]
            conn.close()
            return ["전체 조회"] + tickers
        except Exception:
            return ["전체 조회"]

    def setup_ui(self):
        control_frame = tk.LabelFrame(self.root, text="조회 및 관리", padx=15, pady=15)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        tk.Label(control_frame, text="종목코드:").grid(row=0, column=0, padx=5)
        self.combo_ticker = ttk.Combobox(control_frame, values=self.ticker_list, width=15, state="readonly")
        self.combo_ticker.current(0)
        self.combo_ticker.grid(row=0, column=1, padx=5)

        # 2. 시작일/종료일 달력
        tk.Label(control_frame, text="시작일:").grid(row=0, column=2, padx=5)
        self.cal_start = DateEntry(control_frame, width=12, background='darkblue', date_pattern='yyyy-mm-dd')
        self.cal_start.grid(row=0, column=3, padx=5)

        tk.Label(control_frame, text="종료일:").grid(row=0, column=4, padx=5)
        self.cal_end = DateEntry(control_frame, width=12, background='darkblue', date_pattern='yyyy-mm-dd')
        self.cal_end.grid(row=0, column=5, padx=5)


        btn_search = tk.Button(control_frame, text="데이터 검색", command=self.load_data,
                               bg="#C0C0C0", fg="black", font=('맑은 고딕', 10, 'bold'), width=12)
        btn_search.grid(row=0, column=6, padx=10)

        btn_excel = tk.Button(control_frame, text="엑셀로 내보내기", command=self.export_to_excel,
                              bg="#C0C0C0", fg="black", font=('맑은 고딕', 10, 'bold'), width=15)
        btn_excel.grid(row=0, column=7, padx=10)

        btn_exe_backend = tk.Button(control_frame, text="BACKEND 실행", command=self.exe_backend,
                              bg="#C0C0C0", fg="black", font=('맑은 고딕', 10, 'bold'), width=15)
        btn_exe_backend.grid(row=0, column=8, padx=10)

        tree_container = tk.Frame(self.root)
        tree_container.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)

        vsb = ttk.Scrollbar(tree_container, orient="vertical")
        hsb = ttk.Scrollbar(tree_container, orient="horizontal")

        self.tree = ttk.Treeview(tree_container, columns=self.columns, show='headings',
                                 yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        for col in self.columns:
            self.tree.heading(col, text=col.upper())
            self.tree.column(col, width=100, anchor="center")

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        selected_ticker = self.combo_ticker.get()
        start = self.cal_start.get_date().strftime('%Y-%m-%d')
        end = self.cal_end.get_date().strftime('%Y-%m-%d')

        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            query = f"SELECT * FROM {self.table_name} WHERE date BETWEEN ? AND ?"
            params = [start, end]

            if selected_ticker != "전체 조회":
                query += " AND ticker = ?"
                params.append(selected_ticker)

            query += " ORDER BY date DESC"
            cursor.execute(query, params)
            rows = cursor.fetchall()

            for row in rows:
                self.tree.insert("", tk.END, values=row)
            conn.close()
        except Exception as e:
            messagebox.showerror("에러", f"조회 중 오류 발생: {e}")

    def export_to_excel(self):
        """이 함수가 위 load_data 함수와 똑같은 위치에서 시작해야 합니다."""
        rows = self.tree.get_children()
        if not rows:
            messagebox.showwarning("경고", "내보낼 데이터가 없습니다.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="stock_data.csv"
        )

        if file_path:
            try:
                with open(file_path, mode="w", newline="", encoding="utf-8-sig") as f:
                    writer = csv.writer(f)
                    writer.writerow(self.columns)
                    for row_id in rows:
                        writer.writerow(self.tree.item(row_id)["values"])
                messagebox.showinfo("완료", "저장되었습니다.")
            except Exception as e:
                messagebox.showerror("에러", f"저장 실패: {e}")

    def exe_backend(self):
        # 1. 같은 폴더에 있는 파일 실행
        # subprocess.run(["server.exe"])
        # 백그라운드로 실행 (파이썬은 기다리지 않음)
        process = subprocess.Popen(["server.exe"])
        print("서버가 백그라운드에서 시작되었습니다. PID:", process.pid)
        # 이후 다른 작업(GUI 실행 등)을 계속할 수 있습니다.


        url = "http://127.0.0.1:8000/docs#"

        # 방법 A: 시스템 기본 브라우저로 열기
        webbrowser.open(url)

        # 방법 B: 크롬으로 지정해서 열기 (윈도우 기준 경로)
        # 크롬 설치 경로가 다른 경우 해당 경로로 수정하세요.
        chrome_path = 'C:/Program Files/Google/Chrome/Application/chrome.exe %s'
        webbrowser.get(chrome_path).open(url)



if __name__ == "__main__":
    root = tk.Tk()
    app = FIViewApp(root)
    root.mainloop()