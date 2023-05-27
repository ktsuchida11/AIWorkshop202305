# AIWorkshop202305

個人のM1 MacではChatGPTのモジュールがうまく動かなかったのでコンテナにして動作を確認した

## コンテナの内容

- Chat GPT API接続するRESTAPIを作成
- 金融に関するデータを取得するためのRESTAPIを作成
- Newsを取得するためのRESTAPIを作成

## 初期設定

### ChatGPTに問い合わせる
#### ChatGPT API接続　:https://platform.openai.com/
ChatGPTに問い合わせるためのAPI
.envファイルをDataSourceAPI直下に作成してAPI_KEYを登録する

### 金融に関するデータを取得
データソースによってはAPI_KEYの取得が必要なものがあるので適宜追加する

#### ALPHA API接続:https://www.alphavantage.co/documentation/
マーケットの過去レートなどを取得するためのAPI

#### News API 接続　：https://newsapi.org/
ニュースのヘッドラインなどを取得するためのAPI
.envファイルをDataSourceAPI直下に作成してAPI_KEYを登録する

ファイル例
``` txt
OPENAI_API_KEY="xxxxxxxxxxxxx"
ALPHA_VANTAGE_API_KEY="xxxxxxxxxxxxx"
NEWSAPI_API_KET="xxxxxxxxxxxxx"
````

## 使い方

Dockerが起動していることが前提条件

```
# コンテナの起動
DataSourceAPI $docker-compose build
DataSourceAPI $docker-compose up -d 

# sample request
DataSourceAPI $ curl -X POST localhost:8002/chatGPT -H "Content-Type: application/json" -d '{"role": "user", "content": "Hello!"}'

````

## 自動取引システムへの応用実装

### 1.実際のニュースを外部サービスから取得 
- News APIを利用して情報ベンダーの情報から為替の取引に関係ありそうな情報を取得する処理を確認
- FastAPIでNewAPIからデータを取得するためのAPIを作成
- カテゴリやニュースの抽出方法をか確認する
`get_externalinfo.py`

### 2.テキストマイニングを実施
- 全体取り上げ単語の重要度をベクトル化するTFIDFを１で取得した情報をもとに出力する処理を確認
- 単語に分割
- センテンスごとの単語の重要度をベクトルで表現
- 特に特徴があった単語を抽出
`sentment_trader.py`

### 3.ChatGPTによるセンチメント判定
- 2の結果をもとにChatGPTを利用してセンチメントを判定する処理を確認
- プロンプトエンジニアリングで役割や前提条件を記載する
- ２で抽出した単語を使ってChatGPTに問い合わせる
- 単語ごとの判断結果を集計する
`sentment_trader.py`

### 4.センチメントの結果をもとに自動で取引
- 3の結果をもとに自動で取引する処理を確認
- OandaAPIを利用して成行注文を行う
`sentment_trader.py`
