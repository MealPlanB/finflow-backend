from fastapi import APIRouter, Depends, HTTPException
import requests
import json
from pydantic import BaseModel


class CurrentChartInfo(BaseModel):
    high_price: str
    low_price: str
    current_price: str
    start_price: str
    current_rate: str


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
endpoint = url + getStock
router = APIRouter()


@router.get("/show/{stock}")
async def show_stock_info(stock: str):
    with open('stock_code.txt', 'r', encoding='euc-kr') as f:
        stock_data = eval(f.read())

    stock_code = next((code for code, name in stock_data.items() if name == stock), None)

    if stock_code:
        params = {
            "fid_cond_mrkt_div_code": "J",
            "fid_input_iscd": stock_code
        }
        response = requests.get(endpoint, params=params, headers=headers)
        result = json.loads(response.text)

        chart_info = CurrentChartInfo(
            high_price=result['output']['stck_hgpr'],
            low_price=result['output']['stck_lwpr'],
            current_price=result['output']['stck_prpr'],
            start_price=result['output']['stck_oprc'],
            current_rate=result['output']['prdy_ctrt']
        )

        return chart_info
    else:
        return {"message": "Stock not found"}
