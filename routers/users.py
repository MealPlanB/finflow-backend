from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import mysql.connector

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
    cursor.execute("UPDATE users SET money = %s", (request.money,))
    db.commit()
    cursor.close()
    return {"message": "Season started successfully"}


@router.post("/end")
async def end_season(db: mysql.connector.connection.MySQLConnection = Depends(get_db)):
    cursor = db.cursor()
    # start_date와 end_date를 2000-00-00으로 업데이트
    cursor.execute("UPDATE seasons SET start_date = '2000-01-01', end_date = '2000-01-01'")
    db.commit()
    cursor.close()
    return {"message": "Season ended successfully"}


@router.post("/reset")
async def reset_db(db: mysql.connector.connection.MySQLConnection = Depends(get_db)):
    cursor = db.cursor()

    # Clear data from tables except seasons
    cursor.execute("DELETE FROM trade")
    cursor.execute("DELETE FROM users")

    # Reset seasons data
    cursor.execute("UPDATE seasons SET start_date = '2000-01-01', end_date = '2000-01-01'")

    db.commit()
    cursor.close()

    return {"message": "Database reset successful"}
