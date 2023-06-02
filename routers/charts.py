from fastapi import APIRouter, Depends, HTTPException
import requests
import json
from pydantic import BaseModel

class current_chartInfo(BaseModel):
    high_price : str
    low_price : str
    current_price : str
    start_price : str
    current_rate : str



url = 'https://openapivts.koreainvestment.com:29443/'
getStock = 'uapi/domestic-stock/v1/quotations/inquire-price'
APP_KEY = 'PSIZExuxlSzK50wmyUIeI1VWQvvqepe9FeJW'
APP_SECRET = 'IuAtB6vXKnChmNsUkVG5bVqZ13kN/3j1gVYQwn57ruNTvOegy5tKGlaYlInAJYv4Ysb6yuSF64VQJV9b8NOatzZOtLeGuWjgI9UIx4WWceFokBsTFdQ220SVB9gYeEUjPA7qov6uhTcJQay4bqV7xNfWPaf6WMYgGQzWxLFCpeDWd3gDg0c='


headers = {
    'content-type' : 'application/json; charset=utf-8',
    'authorization' : 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6ImZlNmVlZGM4LWVhY2QtNDM5Yy1iYmRhLWE0YWU3MTE5Nzg1OCIsImlzcyI6InVub2d3IiwiZXhwIjoxNjg1NzY2NTA2LCJpYXQiOjE2ODU2ODAxMDYsImp0aSI6IlBTSVpFeHV4bFN6SzUwd215VUllSTFWV1F2dnFlcGU5RmVKVyJ9.doCpyeROBQaVSbwpX0J6fLygs8ejTKFXE1YiG-1aMFF1McowYakCTCqozC86wVlIw7iQPV_jGUoJWI47iGgqmA',
    'appkey' : APP_KEY,
    'appsecret' : APP_SECRET,
    'tr_id' : 'FHKST01010100'
}
endpoint = url + getStock
router = APIRouter()


#최고가, 최저가, 현재가, 시가, 등락율(전일대비) 반환해줌
@router.get("/show/{stock}")
async def afaf(stock : str):
    f = open('stock_code.txt', 'r', encoding = 'euc-kr')
    reader = f.read()

    stock_data = eval(reader)
    stock_keys = stock_data.keys()
    f.close()

    stock_name = stock

    input_code = ""
    for key in stock_keys:
        if stock_data[key] == stock_name:
            input_code = key
            print(input_code)
            break

    # 종목 코드를 찾은 경우
    if input_code != "":
        params = {
            "fid_cond_mrkt_div_code": "J",
            "fid_input_iscd": input_code
        }
        response = requests.get(endpoint, params=params, headers=headers)
        result = json.loads(response.text)
        high_P = result['output']['stck_hgpr'] #최고가
        low_P = result['output']['stck_lwpr'] #최저가
        current_P = result['output']['stck_prpr'] #현재가
        start_P = result['output']['stck_oprc'] #시작가
        current_R = result['output']['prdy_ctrt'] #등락율

        chart_info = current_chartInfo(high_price = high_P, low_price = low_P, current_price = current_P, start_price = start_P, current_rate = current_R)
        
        return chart_info
    else:
        return "오류!"



