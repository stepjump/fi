# ============================================================================
# 파이썬 파일 순차적으로 실행시키기
# FI_0001.py, FI_0002.py, FI_0003.py  ===> SQLite FI.db파일, 테이블 daily_total_info 주식정보 메인 테이블 만들기
# pyinstaller --onefile ALL_RUN.py
# ============================================================================

import subprocess
import sys
import os

def run_scripts():
    # 실행할 파일 이름 목록 (필요에 따라 수정)
    scripts = ["FI_0001.py", "FI_0002.py", "FI_0003.py"] 

    # 현재 main.py 파일이 있는 폴더의 절대 경로
    current_dir = os.path.dirname(os.path.abspath(__file__))

    for script in scripts:
        script_path = os.path.join(current_dir, script)
        
        print(f"========== [ {script} 실행 시작 ] ==========")
        try:
            result = subprocess.run(
                [sys.executable, script_path], 
                check=True,
                text=True,
                capture_output=True,
                encoding='utf-8' # <--- 핵심 해결책: UTF-8 인코딩 방식 지정
            )
            print(result.stdout, end="")
            print(f"========== [ {script} 실행 완료 ] ==========\n")
            
        except subprocess.CalledProcessError as e:
            print(f"[오류 발생] {script} 실행 중 문제가 발생했습니다.")
            print(e.stderr)
            break
        except FileNotFoundError:
            print(f"[파일 찾기 오류] {script_path} 경로에서 파일을 찾을 수 없습니다.")
            break

if __name__ == "__main__":
    run_scripts()