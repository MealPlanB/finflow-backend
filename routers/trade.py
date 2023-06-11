from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import mysql.connector
import requests
import json
from datetime import datetime

url = 'https://openapivts.koreainvestment.com:29443/'
getStock = 'uapi/domestic-stock/v1/quotations/inquire-price'
APP_KEY = 'PSIZExuxlSzK50wmyUIeI1VWQvvqepe9FeJW'
APP_SECRET = 'IuAtB6vXKnChmNsUkVG5bVqZ13kN/3j1gVYQwn57ruNTvOegy5tKGlaYlInAJYv4Ysb6yuSF64VQJV9b8NOatzZOtLeGuWjgI9UIx4WWceFokBsTFdQ220SVB9gYeEUjPA7qov6uhTcJQay4bqV7xNfWPaf6WMYgGQzWxLFCpeDWd3gDg0c='

headers = {
    'content-type': 'application/json; charset=utf-8',
    'authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6ImMxYjA1YWIyLWQzNjctNGIxYS04YWU4LWNiNzVlNGZjNDhlOSIsImlzcyI6InVub2d3IiwiZXhwIjoxNjg2NTQ4Mzg5LCJpYXQiOjE2ODY0NjE5ODksImp0aSI6IlBTSVpFeHV4bFN6SzUwd215VUllSTFWV1F2dnFlcGU5RmVKVyJ9.6OyMiR5_FPoF3nwjRe-FIr-ySzVbS91UuQmgQ_t-mznv_7VUn8vgjteV6d7V7op9vdGzHyio4RLlFDkMVQc75A',
    'appkey': APP_KEY,
    'appsecret': APP_SECRET,
    'tr_id': 'FHKST01010100'
}


def get_db():
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="0000",
        database="finflow"
    )
    return db


router = APIRouter()


class TradeRequest(BaseModel):
    name: str
    stock_name: str
    quantity: int


class TradeHistory(BaseModel):
    user_name: str
    stock_name: str
    quantity: int
    price: int


# 종목 이름을 입력하면 현재 가격을 반환하는 함수
def get_current_stock_price(stock_name):
    endpoint = url + getStock

    f = open('stock_code.txt', 'r', encoding='euc-kr')
    reader = f.read()

    stock_data = eval(reader)
    stock_keys = stock_data.keys()

    f.close()

    input_code = ""
    for key in stock_keys:
        if stock_data[key] == stock_name:
            input_code = key
            break

    # 종목 코드를 찾은 경우
    if input_code != "":
        params = {
            "fid_cond_mrkt_div_code": "J",
            "fid_input_iscd": input_code
        }
        response = requests.get(endpoint, params=params, headers=headers)
        result = json.loads(response.text)

        current_price = result['output']['stck_prpr']  # 현재 가격

        if current_price is not None:
            print(f"The current price of {stock_name} is {current_price}.")
            return int(current_price)
        else:
            print(f"Failed to retrieve the current price of {stock_name}.")
            return None

    else:
        print(f"Failed to find the stock {stock_name}.")
        return None


@router.post("/buy")
async def buy_stock(request: TradeRequest, db: mysql.connector.connection.MySQLConnection = Depends(get_db)):
    cursor = db.cursor()
    # 주식 가격 조회 로직을 추가하여 현재가를 얻어옴
    # stock_price = 1000  # 임시로 가격을 설정
    stock_price = get_current_stock_price(request.stock_name)  # 외부 주식 API와 연동된 값

    # 시즌 도중 여부 확인
    cursor.execute("SELECT start_date, end_date FROM seasons")
    season_dates = cursor.fetchone()
    if season_dates:
        start_date, end_date = season_dates

        # 현재 날짜와 시즌 비교
        now = datetime.now().date()
        if not (start_date <= now <= end_date):
            cursor.close()
            return {"message": "Cannot buy stock outside the season"}

    # 사용자 정보 가져오기
    cursor.execute("SELECT * FROM users WHERE name = %s", (request.name,))
    user_data = cursor.fetchone()
    if user_data:
        # 현재 자금 확인
        money = user_data[2]
        print("Current money:", money)  # 디버깅을 위해 현재 money 값 출력
        if money is not None and money >= stock_price * request.quantity:
            # 주식 매수
            cursor.execute("INSERT INTO trade (user_id, stock_name, quantity, price) VALUES (%s, %s, %s, %s)",
                           (user_data[0], request.stock_name, request.quantity, stock_price))
            # 자금 차감
            remaining_money = money - stock_price * request.quantity
            cursor.execute("UPDATE users SET money = %s WHERE name = %s", (remaining_money, request.name))
            db.commit()
            cursor.close()
            return {"message": "Stock bought successfully"}
        else:
            cursor.close()
            return {"message": "Not enough money to buy the stock"}
    else:
        cursor.close()
        return {"message": "User not found"}


@router.post("/sell")
async def sell_stock(request: TradeRequest, db: mysql.connector.connection.MySQLConnection = Depends(get_db)):
    cursor = db.cursor()
    # 주식 가격 조회 로직을 추가하여 현재가를 얻어옴
    # current_price = 3000  # 더미 값으로 처리, 외부 주식 API와 연동하여 실제 값으로 수정되어야 함
    current_price = get_current_stock_price(request.stock_name)  # 외부 주식 API와 연동된 값

    # 시즌 도중 여부 확인
    cursor.execute("SELECT start_date, end_date FROM seasons")
    season_dates = cursor.fetchone()
    if season_dates:
        start_date, end_date = season_dates

        # 현재 날짜와 시즌 비교
        now = datetime.now().date()
        if not (start_date <= now <= end_date):
            cursor.close()
            return {"message": "Cannot sell stock outside the season"}

    # 사용자 정보 가져오기
    cursor.execute("SELECT * FROM users WHERE name = %s", (request.name,))
    user_data = cursor.fetchone()
    if user_data:
        # 보유한 주식 조회
        cursor.execute("SELECT id, quantity, price FROM trade WHERE user_id = %s "
                       "AND stock_name = %s AND quantity > 0", (user_data[0], request.stock_name))
        stock_holdings = cursor.fetchall()

        if stock_holdings:
            _quantity = request.quantity
            remaining_quantity = _quantity
            sold_quantity = 0
            total_profit = 0

            for stock_id, quantity, stock_price in stock_holdings:
                if remaining_quantity <= 0:
                    break

                if quantity >= remaining_quantity:
                    # 주식 판매
                    # 시즌 도중 여부 확인
                    cursor.execute("SELECT start_date, end_date FROM seasons")
                    season_dates = cursor.fetchone()
                    if season_dates:
                        start_date, end_date = season_dates

                        # 현재 날짜와 시즌 비교
                        now = datetime.now().date()
                        if not (start_date <= now <= end_date):
                            cursor.close()
                            return {"message": "Cannot sell stock outside the season"}

                    # profit = (current_price - stock_price) * remaining_quantity
                    profit = current_price * remaining_quantity
                    cursor.execute("UPDATE trade SET quantity = quantity - %s, sold_quantity = sold_quantity + %s "
                                   "WHERE id = %s", (remaining_quantity, remaining_quantity, stock_id))
                    cursor.execute("INSERT INTO trade (user_id, stock_name, quantity, price) VALUES (%s, %s, %s, %s)",
                                   (user_data[0], request.stock_name, -request.quantity, current_price))

                    total_profit += profit
                    remaining_quantity = 0
                else:
                    # 주식 일부 판매
                    # 시즌 도중 여부 확인
                    cursor.execute("SELECT start_date, end_date FROM seasons")
                    season_dates = cursor.fetchone()
                    if season_dates:
                        start_date, end_date = season_dates

                        # 현재 날짜와 시즌 비교
                        now = datetime.now().date()
                        if not (start_date <= now <= end_date):
                            cursor.close()
                            return {"message": "Cannot sell stock outside the season"}

                    # profit = (current_price - stock_price) * quantity
                    profit = current_price * quantity
                    cursor.execute("UPDATE trade SET quantity = quantity - %s, sold_quantity = sold_quantity + %s "
                                   "WHERE id = %s", (quantity, quantity, stock_id))
                    cursor.execute("INSERT INTO trade (user_id, stock_name, quantity, price) VALUES (%s, %s, %s, %s)",
                                   (user_data[0], request.stock_name, -quantity, current_price))

                    total_profit += profit
                    remaining_quantity -= quantity

            # 자금 증가
            # print("total_profit",total_profit)
            new_money = user_data[2] + total_profit
            cursor.execute("UPDATE users SET money = %s WHERE name = %s", (new_money, request.name))
            db.commit()
            cursor.close()
            return {"message": "Stock sold successfully"}
        else:
            cursor.close()
            return {"message": "Not enough stocks to sell"}
    else:
        cursor.close()
        return {"message": "User not found"}


@router.get("/mystats")
async def get_my_stats(name: str, db: mysql.connector.connection.MySQLConnection = Depends(get_db)):
    cursor = db.cursor()

    # 사용자 정보 가져오기
    cursor.execute("SELECT id FROM users WHERE name = %s", (name,))
    user_id = cursor.fetchone()
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    user_id = user_id[0]

    # 보유 주식 조회
    cursor.execute("SELECT stock_name, SUM(quantity) FROM trade WHERE user_id = %s AND quantity>0 "
                   "GROUP BY stock_name HAVING SUM(quantity) + SUM(sold_quantity) != 0", (user_id,))
    stock_holdings = cursor.fetchall()

    # 응답 데이터 생성
    response = {
        "총 매입금": 0,
        "총 평가금": 0,
        "보유 주식": []
    }

    for stock in stock_holdings:
        stock_name, quantity = stock
        if quantity == 0:
            continue

        # 총 매입금 계산
        cursor.execute("SELECT SUM(quantity * price) FROM trade WHERE user_id = %s "
                       "AND stock_name = %s AND quantity > 0", (user_id, stock_name))
        purchase_amount = cursor.fetchone()[0] or 0
        response["총 매입금"] += purchase_amount

        # 현재 주식 가격 조회
        current_price = get_current_stock_price(stock_name)

        # 평가손익 계산
        cursor.execute("SELECT SUM((%s - price) * quantity) FROM trade WHERE user_id = %s "
                       "AND stock_name = %s AND quantity > 0", (current_price, user_id, stock_name))
        profit_loss = cursor.fetchone()[0] or 0

        stock_info = {
            "주식명": stock_name,
            "매입금": f"{int(purchase_amount):,}원",
            "평가손익": f"{int(profit_loss):+,}원"
        }
        response["보유 주식"].append(stock_info)

        # 총 평가금 계산
        if quantity > 0:
            response["총 평가금"] += current_price * quantity

    # 현재 수익률 계산
    if response["총 매입금"] > 0:
        profit_rate = int((response["총 평가금"] - response["총 매입금"]) / response["총 매입금"] * 100)
    else:
        profit_rate = 0

    response["현재 수익률"] = f"{profit_rate}%"

    # 현금 보유액 조회
    cursor.execute("SELECT money FROM users WHERE id = %s", (user_id,))
    cash_holdings = cursor.fetchone()[0] or 0
    response["현금 보유액"] = f"{int(cash_holdings):,}원"

    cursor.close()

    return response


@router.get("/history/{name}")
async def get_trade_history(name: str, db: mysql.connector.connection.MySQLConnection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT trade.stock_name, trade.quantity, trade.sold_quantity, trade.price, users.name FROM trade "
                   "JOIN users ON trade.user_id = users.id WHERE users.name = %s", (name,))
    trade_data = cursor.fetchall()
    cursor.close()
    if trade_data:
        trade_history = []
        for row in trade_data:
            stock_name = row[0]
            quantity = row[1] + row[2]  # quantity + sold_quantity
            price = row[3]
            user_name = row[4]

            trade = TradeHistory(stock_name=stock_name, quantity=quantity, price=price, user_name=user_name)
            trade_history.append(trade)

        return trade_history
    else:
        raise HTTPException(status_code=404, detail="Trade history not found")


@router.get("/current-stocks")
async def get_current_stocks(db: mysql.connector.connection.MySQLConnection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT DISTINCT stock_name FROM trade")
    stock_data = cursor.fetchall()
    cursor.close()

    current_stocks = [row[0] for row in stock_data]
    return {"current_stocks": current_stocks}
