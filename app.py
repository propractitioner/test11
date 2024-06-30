import streamlit as st
import requests
from datetime import datetime, timedelta
from googletrans import Translator

# finnhub API 키 설정
FINNHUB_API_KEY = st.secrets["finnhub"]["api_key"]

# 번역기 초기화
translator = Translator()

def get_news(ticker, days):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    url = f"https://finnhub.io/api/v1/company-news"
    params = {
        'symbol': ticker,
        'from': start_date.strftime('%Y-%m-%d'),
        'to': end_date.strftime('%Y-%m-%d'),
        'token': FINNHUB_API_KEY
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        news = response.json()
        
        # 最大5つのニュース項目のみを返す
        return news[:5]
    except requests.RequestException as e:
        st.error(f"ニュースの取得中にエラーが発生しました: {str(e)}")
        return []

def summarize_news(articles):
    summaries = []
    for article in articles:
        title = article['headline']
        summary = article['summary']
        full_summary = f"{title}\n{summary}"
        summaries.append(full_summary)
    return "\n\n".join(summaries)

def translate_to_japanese(text):
    try:
        return translator.translate(text, dest='ja').text
    except Exception as e:
        st.error(f"翻訳中にエラーが発生しました: {str(e)}")
        return text

# Streamlitアプリ
st.title('株式ニュース要約アプリ')

ticker = st.text_input('株式ティッカーを入力してください（例：AAPL）')
period = st.selectbox('期間を選択してください', ['1日', '1週間', '1ヶ月'])

if st.button('ニュースを取得'):
    if ticker:
        days = {'1日': 1, '1週間': 7, '1ヶ月': 30}[period]
        with st.spinner('ニュースを取得中...'):
            news = get_news(ticker, days)
        if news:
            summary = summarize_news(news)
            with st.spinner('ニュースを翻訳中...'):
                translated_summary = translate_to_japanese(summary)
            st.write(translated_summary)
        else:
            st.warning('選択した期間中にニュースが見つかりませんでした。別の期間を選択するか、別のティッカーを入力してください。')
    else:
        st.warning('ティッカーを入力してください。')
