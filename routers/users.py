from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import mysql.connector

from routers.trade import get_my_stats

router = APIRouter()


class User(BaseModel):
    id: int
    name: str


class SeasonStartRequest(BaseModel):
    start_date: str
    end_date: str
    money: int


def get_db():
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="0000",
        database="finflow"
    )
    return db


@router.get("/users/{user_id}")
async def get_user(user_id: int, db: mysql.connector.connection.MySQLConnection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()
    cursor.close()
    if user_data:
        user = User(id=user_data[0], name=user_data[1], email=user_data[2])
        return user
    else:
        return JSONResponse(status_code=404, content={"message": "User not found"})


@router.post("/users")
async def create_users(names: List[str], db: mysql.connector.connection.MySQLConnection = Depends(get_db)):
    cursor = db.cursor()
    for name in names:
        cursor.execute("INSERT INTO users (name) VALUES (%s)", (name,))
    db.commit()
    cursor.close()
    return {"message": "Users created successfully"}


@router.post("/start")
async def start_season(request: SeasonStartRequest, db: mysql.connector.connection.MySQLConnection = Depends(get_db)):
    cursor = db.cursor()
    # seasons 테이블의 start_date, end_date 업데이트
    cursor.execute("UPDATE seasons SET start_date = %s, end_date = %s", (request.start_date, request.end_date))
    # 모든 사용자의 money 필드 업데이트
    cursor.execute("UPDATE users SET money = money + %s", (request.money,))
    db.commit()
    cursor.close()
    return {"message": "Season started successfully"}


@router.post("/end")
async def end_season(db: mysql.connector.connection.MySQLConnection = Depends(get_db)):
    cursor = db.cursor()
    # start_date와 end_date를 2000-00-00으로 업데이트
    cursor.execute("UPDATE seasons SET start_date = '2000-01-01', end_date = '2000-01-01'")
    cursor.execute("UPDATE seasons SET host = ''")
    db.commit()

    # 수익률 계산을 위해 필요한 정보 가져오기
    cursor.execute("SELECT name FROM users")
    users = cursor.fetchall()

    # 최고 수익률 초기화
    highest_profit_rate = -1
    highest_profit_user = None

    for user in users:
        name = user[0]
        # 사용자의 통계 정보 가져오기
        stats = await get_my_stats(name, db)
        profit_rate = int(stats["현재 수익률"][:-1])  # '%' 기호 제거하고 정수로 변환

        # 최고 수익률 갱신
        if profit_rate > highest_profit_rate:
            highest_profit_rate = profit_rate
            highest_profit_user = name

    # trade 테이블 초기화
    cursor.execute("TRUNCATE TABLE trade")
    db.commit()

    # users 테이블의 money 칼럼 초기화 및 금액 추가
    cursor.execute("UPDATE users SET money = 0")
    cursor.execute(f"UPDATE users SET money = money + 1500000 WHERE name = '{highest_profit_user}'")
    db.commit()

    cursor.close()

    # 응답 메세지 생성
    message = "모의투자 시즌이 종료되었습니다.\n"
    message += f"전체 수익률 1위: {highest_profit_user} ({highest_profit_rate}%)\n"
    message += f"{highest_profit_user}님, 축하합니다! {highest_profit_user} 님에게는 다음 시즌에 추가 시작금 혜택을 드립니다!"

    return {"message": message}


@router.post("/reset")
async def reset_db(db: mysql.connector.connection.MySQLConnection = Depends(get_db)):
    cursor = db.cursor()

    # Clear data from tables except seasons
    cursor.execute("DELETE FROM trade")
    cursor.execute("DELETE FROM users")

    # Reset seasons data
    cursor.execute("UPDATE seasons SET start_date = '2000-01-01', end_date = '2000-01-01'")
    cursor.execute("UPDATE seasons SET host = ''")
    db.commit()
    cursor.close()

    return {"message": "Database reset successful"}


@router.get("/set-host/{name}")
async def assign_host(name: str, db: mysql.connector.connection.MySQLConnection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("UPDATE seasons SET host = %s", (name,))
    db.commit()
    cursor.close()
    return {"message": "Host set successfully"}


@router.get("/is-host/{name}")
async def check_host(name: str, db: mysql.connector.connection.MySQLConnection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT host FROM seasons")
    result = cursor.fetchone()
    cursor.close()

    if result and result[0] == name:
        return {"message": "You are the host"}
    else:
        return {"message": "You are not the host"}
