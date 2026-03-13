# test_api 테이블 CRUD API
# 서버실행 uvicorn TEST_API:app --reload
# http://127.0.0.1:8000/docs#
from fastapi import FastAPI
import sqlite3
from pydantic import BaseModel

app = FastAPI()
DB_FILE = "test_api.db"

# 데이터를 주고받기 위한 규격(Schema) 정의
class Item(BaseModel):
    name: str
    desc: str | None = None

# API 시작 시 DB 테이블이 없으면 생성
@app.on_event("startup")
def startup():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS test_api (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            desc TEXT
        )
    """)
    conn.commit()
    conn.close()

# 1. 모든 데이터 가져오기 (GET)
@app.get("/items")
def get_items():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM test_api")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1], "desc": r[2]} for r in rows]

# 2. 새로운 데이터 추가하기 (POST)
@app.post("/items")
def create_item(item: Item):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO test_api (name, desc) VALUES (?, ?)", (item.name, item.desc))
    conn.commit()
    conn.close()
    return {"message": "데이터가 성공적으로 저장되었습니다."}


# 3. 데이터 수정하기 (PUT)
@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # 해당 ID가 존재하는지 먼저 확인
    cursor.execute("SELECT id FROM test_api WHERE id = ?", (item_id,))
    if not cursor.fetchone():
        conn.close()
        return {"message": "아이템을 찾을 수 없습니다."}

    # 데이터 업데이트
    cursor.execute(
        "UPDATE test_api SET name = ?, desc = ? WHERE id = ?",
        (item.name, item.desc, item_id)
    )
    conn.commit()
    conn.close()
    return {"message": f"ID {item_id} 데이터가 수정되었습니다."}


# 4. 데이터 삭제하기 (DELETE)
@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM test_api WHERE id = ?", (item_id,))

    if cursor.rowcount == 0:
        conn.close()
        return {"message": "삭제할 아이템이 없습니다."}

    conn.commit()
    conn.close()
    return {"message": f"ID {item_id} 데이터가 삭제되었습니다."}


# 5. 특정 ID의 데이터 하나만 조회하기 (GET)
@app.get("/items/{item_id}")
def get_item(item_id: int):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # 해당 ID로 데이터 조회
    cursor.execute("SELECT * FROM test_api WHERE id = ?", (item_id,))
    row = cursor.fetchone()
    conn.close()

    # 데이터가 없을 경우 404 에러 반환
    if row is None:
        return {"해당 ID의 데이터를 찾을 수 없습니다."}

    return {"id": row[0], "name": row[1], "desc": row[2]}
