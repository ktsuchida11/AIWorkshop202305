import os
import json
import requests

# chatGPT
import openai

# dataroeader
import pandas_datareader.fred as fred
import pandas_datareader.eurostat as eurostat
import pandas_datareader.av.forex as avfx
import pandas_datareader.av.time_series as avtimeseries
import pandas_datareader.av.sector as avsector
import pandas_datareader.av.quotes as avquote


# fast api
from fastapi import (FastAPI, status)
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()
openai.api_key = os.getenv("OPENAI_API_KEY")
av_api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
newsapi_key =  os.getenv("NEWSAPI_API_KET")

class request_body(BaseModel):
    role: str
    content: str

# sample request
# curl -X POST localhost:8002/chatGPT -H "Content-Type: application/json" -d '{"role": "user", "content": "Hello!"}'
# https://chatgpt-lab.com/n/nda0de0be1774 
# ここを参考にする

@app.post("/chatGPT")
async def chatGPT(body: request_body):

    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[body.dict()]
        )

        return JSONResponse(content=completion, status_code=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return JSONResponse(content={"error": "internal server error"}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@app.post("/fitrader")
async def chatGPT(body: request_body):

    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "あなたはベテラン債権トレーダーです。過去の経験をもとに話します"},
                body.dict(),
            ],
        )

        return JSONResponse(content=completion, status_code=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return JSONResponse(content={"error": "internal server error"}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@app.post("/fxtrader")
async def chatGPT(body: request_body):

    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "あなたはFXトレーダーです。マーケットの動きを確認しながら話します"},
                body.dict(),
            ],
        )

        return JSONResponse(content=completion, status_code=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return JSONResponse(content={"error": "internal server error"}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


# sample request
# curl -X POST localhost:8002/chatGPT -H "Content-Type: application/json" -d '{"role": "user", "content": "Hello!"}'
@app.post("/sentiment")
async def chatGPT(body: request_body):

    try:

        completion = openai.Completion.create(
        model="text-davinci-003",
        prompt=body.content,
        temperature=0,
        max_tokens=60,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
        )

        print(completion)

        return JSONResponse(content=completion, status_code=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return JSONResponse(content={"error": "internal server error"}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)



# sample request
# curl localhost:8002/fred

# FRED
# 「株価」
# ダウ平均:DJIA
# S&P500:SP500
# ナスダック:NASDAQ100
# 日経225:NIKKEI225
# 「金利」
# 米10年債利回り日足:DGS10
# 米10年債利回り月足:GS10
# 米10年債利回と米3ヶ月債利回の差:T10Y3M
# 米10年債利回と米2年債利回の差:T10Y2Y
# 米政策金利目標上限値:DFEDTARU
# 米政策金利目標下限値:DFEDTARL
# フェデラルファンド実効金利:DFF
# 日本10年債利回り月足:IRLTLT01JPM156N
# 日本10年債利回り月足:IRLTLT01JPM156N
# 「経済指標」
# 米非農業部門雇用者数:PAYEMS
# 米失業率:UNRATE
# 米GDP成長率:A191RL1Q225SBEA
# 米名目GDP:GDP
# 米実質GDP:GDPC1
# 米消費者物価指数:CPALTT01USM659N
# 米新規失業保険申請件数:ICSA
# 日本実質GDP:JPNNGDP
# 「貿易」
# 米国対日輸出額:EXPJP
# 米国対日輸入額:IMPJP
# 日本向輸出:XTEXVA01JPM667S
# 日本向輸入:XTIMVA01JPM667S
# 「その他」
# 米M2マネーストック:M2REAL
# Default start date for reader. Defaults to 5 years before current date
# return json
@app.get("/fred")
async def load_fred( symbol: str ):

    try:
        fred_data = fred.FredReader(symbol)

        df = fred_data.read()

        print(type(df))
        print(df)
        print(fred_data.url)

        fred_data.close()
        return JSONResponse(content=df.to_json(), status_code=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return JSONResponse(content={"error": "internal server error"}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

# eurostat
# Default start date for reader. Defaults to 5 years before current date
# return json
@app.get("/eurostat")
async def load_eurostat( symbol: str ):

    try:
        eurostat_data = eurostat.EurostatReader(symbol)

        df = eurostat_data.read()

        print(type(df))
        print(df)
        print(eurostat_data.url)

        eurostat_data.close()
        return JSONResponse(content=df.to_json(), status_code=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return JSONResponse(content={"error": "internal server error"}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Alpha Vantage Forex
# http://127.0.0.1:8002/avquote?symbol=USD/JPY
# Default start date for reader. Defaults to 5 years before current date
# return json
@app.get("/avfx")
async def load_avfx( symbol: str ):

    try:
        avfx_data = avfx.AVForexReader(symbols=symbol, api_key=av_api_key)

        df = avfx_data.read()

        print(type(df))
        print(df)
        print(avfx_data.url)

        avfx_data.close()
        return JSONResponse(content=df.to_json(), status_code=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return JSONResponse(content={"error": "internal server error"}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Alpha Vantage Quote
# http://127.0.0.1:8002/avquote?symbol=USD/JPY
# Default start date for reader. Defaults to 5 years before current date
# return json
@app.get("/avquote")
async def load_avquote( symbol: str ):

    try:
        avquote_data = avfx.AVForexReader(symbols=symbol, api_key=av_api_key)

        df = avquote_data.read()

        print(type(df))
        print(df)
        print(avquote_data.url)

        avquote_data.close()
        return JSONResponse(content=df.to_json(), status_code=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return JSONResponse(content={"error": "internal server error"}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Alpha Vantage Time series
# http://127.0.0.1:8002/avtimeseries?symbol=USD/JPY&start=JAN-01-2010&end=JAN-01-2023’
# Default start date for reader. Defaults to 5 years before current date
# return json
@app.get("/avtimeseries")
async def load_avquote( symbol: str , start: str , end: str ):

    try:
        avtimeseries_data = avtimeseries.AVTimeSeriesReader(symbols=symbol, start=start, end=end, api_key=av_api_key)

        df = avtimeseries_data.read()

        print(type(df))
        print(df)
        print(avtimeseries_data.url)

        avtimeseries_data.close()
        return JSONResponse(content=df.to_json(), status_code=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return JSONResponse(content={"error": "internal server error"}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

# news
@app.get("/news")
async def newsapi(query : str, pagesize: int, category: str, country: str) :

    try :
        headers = {'X-Api-Key': newsapi_key }

        # parameter はこちらを確認
        # https://newsapi.org/docs/endpoints/sources
        url = 'https://newsapi.org/v2/everything'
        params = {
            'q':  query,
            'sortBy': 'publishedAt',
            'language': 'en',
            'pageSize': pagesize
        }

        #動作確認
        response = requests.get(url, headers=headers, params=params)
        print(response)
        print(f"HTTP Status Code: {response.status_code}")

        data = response.json()

    except Exception as e:
        print(e)

    return data