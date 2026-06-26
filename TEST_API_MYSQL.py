# 호스팅업체에서 mysql 접속불가
import pymysql
from fastapi import FastAPI

app = FastAPI()

# 닷홈에서 받은 정보 입력
DB_CONFIG = {
    'host': 'stepjump7312.dothome.co.kr/',
    'user': 'stepjump7312',
    'password': 'gu7312!!',
    'database': 'stepjump7312',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

# 공통 커넥션 함수
def get_db():
    return pymysql.connect(**DB_CONFIG)

# 1. CREATE: 데이터 추가
@app.post("/items")
def create_item(name: str, desc: str):
    conn = get_db()
    with conn.cursor() as cursor:
        sql = "INSERT INTO test_api (name, `desc`) VALUES (%s, %s)"
        cursor.execute(sql, (name, desc))
    conn.commit()
    conn.close()
    return {"message": "데이터가 추가되었습니다."}

# 2. READ: 전체 또는 특정 데이터 조회
@app.get("/items")
def get_items(item_id: int = None):
    conn = get_db()
    with conn.cursor() as cursor:
        if item_id:
            cursor.execute("SELECT * FROM test_api WHERE id = %s", (item_id,))
        else:
            cursor.execute("SELECT * FROM test_api")
        result = cursor.fetchall()
    conn.close()
    return result

# 3. UPDATE: 데이터 수정
@app.put("/items/{item_id}")
def update_item(item_id: int, name: str, desc: str):
    conn = get_db()
    with conn.cursor() as cursor:
        sql = "UPDATE test_api SET name = %s, `desc` = %s WHERE id = %s"
        affected = cursor.execute(sql, (name, desc, item_id))
    conn.commit()
    conn.close()
    if affected == 0:
        return {"message": "수정할 데이터를 찾을 수 없습니다."}
    return {"message": f"ID {item_id} 수정 완료"}

# 4. DELETE: 데이터 삭제
@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    conn = get_db()
    with conn.cursor() as cursor:
        affected = cursor.execute("DELETE FROM test_api WHERE id = %s", (item_id,))
    conn.commit()
    conn.close()
    if affected == 0:
        return {"message": "삭제할 데이터를 찾을 수 없습니다."}
    return {"message": f"ID {item_id} 삭제 완료"}