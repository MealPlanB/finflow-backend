import websockets
import requests
import json
from datetime import datetime
import math
import time
from fastapi import FastAPI
import yfinance as yf
import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd






url = 'https://openapivts.koreainvestment.com:29443/'
getStock = 'uapi/domestic-stock/v1/quotations/inquire-price'
APP_KEY = 'PSIZExuxlSzK50wmyUIeI1VWQvvqepe9FeJW'
APP_SECRET = 'IuAtB6vXKnChmNsUkVG5bVqZ13kN/3j1gVYQwn57ruNTvOegy5tKGlaYlInAJYv4Ysb6yuSF64VQJV9b8NOatzZOtLeGuWjgI9UIx4WWceFokBsTFdQ220SVB9gYeEUjPA7qov6uhTcJQay4bqV7xNfWPaf6WMYgGQzWxLFCpeDWd3gDg0c='

now = datetime.today()


headers = {
    'content-type' : 'application/json; charset=utf-8',
    'authorization' : 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6ImUwYmVjMWUxLWY0MTctNDIyYy1hYTJjLTIxYTJhMDFhNGY3ZCIsImlzcyI6InVub2d3IiwiZXhwIjoxNjg1Mjg2NjkxLCJpYXQiOjE2ODUyMDAyOTEsImp0aSI6IlBTSVpFeHV4bFN6SzUwd215VUllSTFWV1F2dnFlcGU5RmVKVyJ9.Zjiqz81vnouTKDLcTF3iOaVAPvtXw29vU9tri_wQHkCoX5e3PhOZ1X8Bcu5sMsoPhSpx68GaojbpUfh-tiiWLw',
    'appkey' : APP_KEY,
    'appsecret' : APP_SECRET,
    'tr_id' : 'FHKST01010100'
}


getURL = url + getStock


f = open('stock_code.txt', 'r', encoding = 'utf-8')
reader = f.read()

stockData = eval(reader)
stockKey = stockData.keys()

f.close()


'''
#장 마감시간 체크. 장 마감 이후는 종가 이용하기!
def checkDay():
    if(now.weekday() == 5 or now.weekday() == 6 or now.hour > 17 or now.hour < 8):
        return False
    else:
        return True
'''
print("함수시작")

#사용자가 입력한 이름을 바탕으로 주식을 찾아서 고가/저가...등을 반환함
def findStock(inputedStockName):
    inputedIscd = ""
    for key in stockKey:
        if stockData[key] == inputedStockName:
            inputedIscd = key
            break
    #찾은 경우
    if inputedIscd != "":
        params = {
            "fid_cond_mrkt_div_code": "J",
            #이곳에 종목코드 입력
            "fid_input_iscd": inputedIscd
        }
        ress = requests.get(getURL, params = params, headers=headers)
        
        result = json.loads(ress.text)
        money_info = []
        high_price = result['output']['stck_hgpr'] #최고가
        low_price = result['output']['stck_lwpr'] #최저가
        sd_price = result['output']['stck_prpr'] #현재가
        prdy_vrss = result['output']['prdy_ctrt'] #등락율
        stck_oprc = result['output']['stck_oprc'] #시가
        money_info.append(inputedStockName)
        money_info.append(high_price)
        money_info.append(low_price)
        money_info.append(sd_price)
        money_info.append(prdy_vrss)
        money_info.append(stck_oprc)
        money_info.append(inputedIscd)
        return money_info
            
    else:
        strs = inputedStockName + "을 찾을수 없습니다.\n"
        return strs


start = time.time()
print(findStock("LG전자"))
end = time.time()

print(end - start)

def sellStock(inputedStockName):
    return False


#종목이름을 받아 1월 1일부터 입력한 날까지 그래프 그려주기
#{종목이름}.png로 저장한다.

def makeStockGraph(inputedStockName, end_date):
    stock_info = findStock(inputedStockName)
    if type(stock_info) == list:
        stockCode = stock_info[6]
        start_date = datetime(2023,1,1)
        stockCode += '.ks'
        stock = yf.download(stockCode, start = start_date, end = end_date)

        mpf.plot(stock, type = "candle", style = "yahoo", title =  "graph", ylabel = "Price", show_nontrading = False, returnfig = True)
        plt.savefig(inputedStockName + '.png')
    else:
        print("존재하지 않는 주식입니다.")

end_date = datetime(2023,5,27)
makeStockGraph("삼성전자", end_date)
makeStockGraph("LG전자", end_date)

def makeTodayStockGraph(stockCode):
    
    
    open_price = 3000
    high_price = 5000
    low_price = 2000
    current_price = 3500

    data = {
        'date': ['2023-01-01'],
        'open': [open_price],
        'high': [high_price],
        'low': [low_price],
        'close': [current_price]
    }

    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)

    mpf.plot(df, type='candle', style='yahoo', title='Candlestick Chart', ylabel='Price')

    plt.show()

makeTodayStockGraph("005930")



    
