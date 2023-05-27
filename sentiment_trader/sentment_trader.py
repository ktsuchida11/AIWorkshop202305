import matplotlib as mpl
from pylab import plt
import tpqoa
import numpy as np
import pandas as pd
import json
import threading
import warnings
import time
import pickle
import MeCab
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import collections
import math

from sklearn.feature_extraction.text import TfidfVectorizer

from get_externalinfo import get_externalinfo

# ------------------------
# oanda api class
# ------------------------
class oanda_api(tpqoa.tpqoa):

    # changeable variables
    instrument = 'USD_JPY'
    units = 5000
    thread = ""
    strategy = ""
    # un changeable variables
    raw_data = pd.DataFrame()
    position = 0
    tick_cnt = 0
    signal = 0

    def get_setting(self):
        return self.instrument, self.units

    def get_positions(self):
        return self.position

    def set_instrument(self, instrument):
        self.instrument = instrument

    def set_units(self, units):
        self.units = units

    def set_strategy(self, strategy):
        self.strategy = strategy

    def set_thread(self, thread):
        self.thread = thread

    def __set_strategy_signal(self):
        if self.strategy == "fixed":
            self.signal  = self.__get_news_sentiment_signal("あなたは債権者ストラテジストです。過去の債権相場の出来事を思い出しながら以下の言葉を債権価格に対して肯定は否定か評価してください", 0.4 )
            print("fixed income signal:" + str(self.signal))
        elif self.strategy == "equity":
            self.signal  = self.__get_news_sentiment_signal("あなたは日本株のストラテジストです。過去の日本相場の出来事を思い出しながら以下の言葉を株価に対して肯定は否定か評価してください", 0.4 )
            print("equity signal:" + str(self.signal))
        elif self.strategy == "fx":
            self.signal  = self.__get_news_sentiment_signal("あなたは為替のストラテジストです。過去の為替相場の出来事を思い出しながら以下の言葉を株価に対して肯定は否定か評価してください", 0.4 )
            print("equity signal:" + str(self.signal))
        else :
            self.signal = 0

    def __get_news_sentiment_signal(self,prompt,check_param):

        result = 0
        positive = 0
        negative = 0
        queries =[]

        queries = [
                ['an',"business OR fx market OR bond market OR stock market OR invest OR politics OR industry"],
                ['jp',"nikkei AND( business OR fx market OR bond market OR stock market OR invest OR politics OR industry )"],
                ['gb',"business OR fx market OR bond market OR stock market OR invest OR politics OR industry"],
                ['us',"cnbc AND ( business OR fx market OR bond market OR stock market OR invest OR politics OR industry )"],
                ['us',"bloomberg AND ( business OR fx market OR bond market OR stock market OR invest OR politics OR industry)"]
            ]

        info_api = get_externalinfo()
        info_api.set_news_pagesize(10)

        # 検索条件に合わせたニュースの取得
        for query in queries:

            print("-- start get news title --")
            print("news country:" + query[0] + " news query" + query[1] )
            data = info_api.get_news_data(query[1], "business", query[0])

            lines = []
            i = 1
            for article in data["articles"] :
                print(article["title"])
                lines.append(article["title"])
            print("-- end  get news title --")

            print("-- start news words Feature --")
            # 単語の重要度分析 TfidfVectorizer
            check_words = calc_tfidf(lines,check_param)
            print("-- End  news words Feature --")

            print("-- Start ask sentiment to ChatGPT --")
            # create chatGPT Query String
            question =  prompt + ":\n\n" + check_words + "\n\n言葉の評価:"
            print("question:" + question)
            # chatGPTに質問する
            answer = info_api.ask_chatGPTSentiment(question)
            print("answer:" + answer)
            print("-- End ask sentiment to ChatGPT --")

            positive += answer.count("肯定")
            negative += answer.count("否定")
            print("positive:" + str(answer) + "negative:" + str(negative))

        if positive >0 and negative > 0:
            if positive > negative :
                result = 1
            elif positive < negative :
                result = -1

        return result

    def __handle_spot_order(self,pl):

        trade_amount = 0
        print("unit:"+ str(self.units))
        self.__set_strategy_signal()
        # signal on
        if self.signal != 0:
            if self.position == 0:
                print("neutral position signal:" + str(self.signal))
                # positive
                if self.signal == 1:
                    self.position = self.units
                    trade_amount = self.units
                    print(self.thread + "|" + "Buy Position Opened | instrument:" + str(self.instrument) + "units:" + str(self.units) )
                # negative
                elif self.signal == -1:
                    self.position = -1 * self.units
                    trade_amount = (-1 * self.units)
                    print(self.thread + "|" + "Sell Position Opened | instrument:" + str(self.instrument) + "units:" + str(self.units) )
            else :
                print("position:" + str(self.position) + " signal:" + str(self.signal))
                # positive
                if self.signal == 1:
                    self.position = self.position + self.units
                    trade_amount = self.units
                    print(self.thread + "|" + "Buy Position Close | instrument:" + str(self.instrument) + "units:" + str(self.units) )
                # negative
                elif self.signal == -1:
                    self.position = self.position + (-1 * self.units)
                    trade_amount = (-1 * self.units)
                    print(self.thread + "|" + "Sell Position Close | instrument:" + str(self.instrument) + "units:" + str(self.units) )
            result = self.create_order(self.instrument, trade_amount, suppress=True, ret=True)
            print(result)
        # profit loss cut
        else :
            # profit cut
            if pl > 2000:
                print("Get Profit")
                print(self.thread + "|" + "Position Close | instrument:" + str(self.instrument) + "units:" + str(self.units) )
                if self.position != 0:
                    result = self.create_order(self.instrument, (-1 * self.position), suppress=True, ret=True)
                    print(result)
                    self.position = 0
            # loss cut
            elif pl < -3000 :
                print("Get Loss")
                print(self.thread + "|" + "Position Close | instrument:" + str(self.instrument) + "units:" + str(self.units) )
                if self.position != 0:
                    result = self.create_order(self.instrument, (-1 * self.position), suppress=True, ret=True)
                    print(result)
                    self.position = 0

    def on_success(self, time, bid, ask):
        #''' Method called when new data is retrieved. '''
        summary = self.get_account_summary()
        dict_account = {
            'id': summary['id'],
            'unrealizedPL': summary['unrealizedPL'],
            'balance': summary['balance'],
            'pl': summary['pl'],
            'margenRate': summary['marginRate'],
        }

        pl = int(float(dict_account['unrealizedPL']))

        if self.tick_cnt > 20 :
            self.__handle_spot_order(pl)
            self.tick_cnt = 0

        self.tick_cnt += 1
        print('BID: {:.5f} | ASK: {:.5f}'.format(bid, ask))

# ----------------------------------------------
# word cloud function
# ----------------------------------------------
def calc_tfidf(lines,check_param):

    # 単語の重要度分析 TfidfVectorizer
    vec_tfidf = TfidfVectorizer()

    X = vec_tfidf.fit_transform(lines)
    print('feature_names:', vec_tfidf.get_feature_names())
    print("feature_value:" + str(check_param) )

    words = vec_tfidf.get_feature_names()

    check_words = ""
    i = 1
    for doc_id, vec in zip(range(len(lines)), X.toarray()):
        print('doc_id:', doc_id)
        for w_id, tfidf in sorted(enumerate(vec), key=lambda x: x[1], reverse=True):
            lemma = words[w_id]
            if tfidf > check_param :
                print(str(i) + '.\t{0:s}: {1:f}'.format(lemma, tfidf))
                check_words = check_words + str(i) + ". " + lemma + "\n"
                i = i + 1

    return check_words

# -------------------------------------------------
# main function
# -------------------------------------------------
def run_sentiment(instrument, units, stop, strategy):

    trade_api = oanda_api('pyalgo.cfg')

    print(threading.current_thread().name + "default instrument: " + str(instrument) + " units: " + str(units))

    trade_api.set_instrument(instrument)
    trade_api.set_units(units)
    trade_api.set_strategy(strategy)
    trade_api.set_thread(strategy)

    if threading.current_thread().name != 'MainThread':
        trade_api.set_thread(threading.current_thread().name)

    trade_api.stream_data(instrument, stop=stop)
    # create_order(instrument, units=-trade_api.position * trade_api.units)
    trade_api.create_order(instrument, units=-trade_api.position)


# -------------------
# start program
# -------------------
if __name__ == '__main__':

    warnings.simplefilter('ignore')
    # initialize api

    # create thread
    t1 = threading.Thread(target=run_sentiment, args=("USD_JPY", 1000, 500, "fx"), name='Thread fixed Income')
    #t2 = threading.Thread(target=run_sentiment, args=("USD_JPY", 1000, 500, "equity"), name='Thread equity')
    #t3 = threading.Thread(target=run_sentiment, args=("USD_JPY", 1000, 500, "fx"), name='Thread politics')
    # start()
    t1.start()
    #t2.start()
    #t3.start()
    # join()
    t1.join()
    #t2.join()
    #t3.join()

