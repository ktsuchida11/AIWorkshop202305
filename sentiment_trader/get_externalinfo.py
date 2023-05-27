import requests
import json

class get_externalinfo():

    base_url = "http://127.0.0.1:8002"

    fred_url =  "/fred"
    quote_url = "/avquote"
    timeserise_url = "/avtimeseries"

    #POST先URL
    chatGPT_url = "/chatGPT"

    chatGPT_sentiment_url= "/sentiment"
    newsapi_url= "/news"

    news_pagesize = 10

    def set_news_pagesize(self, news_pagesize) :
        self.news_pagesize = news_pagesize

    def get_dict_data(self, symbol) :
        result = ""

        try :
            payload = {
                "symbol": symbol
            }

            #GET送信
            response = requests.get(
                self.base_url + self.fred_url,
                params = payload    #dataを指定する
                )

            res_data = response.json()
            print(type(res_data))
            result = json.dumps(res_data)
            #print(result)
        except Exception as e:
            print(e)

        return result

    def get_str_data(self, symbol) :

        result = ""

        try :
            payload = {
                "symbol": symbol
            }

            #GET送信
            response = requests.get(
                self.base_url + self.quote_url,
                params = payload    #dataを指定する
                )

            res_data = response.json()
            print(type(res_data))
            result = res_data
            #print(result)
        except Exception as e:
            print(e)

        return result

    def get_news_data(self, query, category, country) :

        result = ""

        try :
            payload = {
                "query": query,
                "pagesize": self.news_pagesize,
                "category": category,
                "country": country
            }

            #GET送信
            response = requests.get(
                self.base_url + self.newsapi_url,
                params = payload    #dataを指定する
                )

            res_data = response.json()
            print(type(res_data))
            result = res_data
            print(result)
        except Exception as e:
            print(e)

        return result


    def get_historical_data(self, symbol, start, end) :
        result = ""

        try :
            payload = {
                "symbol": symbol,
                "start": start,
                "end": end
            }

            #GET送信
            response = requests.get(
                self.base_url + self.timeserise_url,
                params = payload    #dataを指定する
                )

            res_data = response.json()
            print(type(res_data))
            result = json.dumps(res_data)
            print(result)
        except Exception as e:
            print(e)

        return result

    def ask_chatGPT(self, question) :

        answer = ""
        try :

            #JSON形式のデータ
            json_data = {
                "role": "user",
                "content": question
            }

            #POST送信
            response = requests.post(
                self.base_url + self.chatGPT_url,
                data = json.dumps(json_data)    #dataを指定する
                )

            res_data = response.json()

            choices = res_data.get('choices')
            answer = choices[0].get('message').get('content')

        except Exception as e:
            print(e)
        return answer

    def ask_chatGPTSentiment(self, question) :

        try :
            #JSON形式のデータ
            json_data = {
                "role": "user",
                "content": question
            }
            #POST送信
            response = requests.post(
                self.base_url + self.chatGPT_sentiment_url,
                data =json.dumps(json_data)   #dataを指定する
                )

            res_data = response.json()

            choices = res_data.get('choices')
            answer = choices[0].get('text')

        except Exception as e:
            print(e)

        return answer