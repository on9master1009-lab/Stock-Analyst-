import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="📊 股票分析", layout="centered")
st.title("📊 美股分析工具")

# Alpha Vantage API Key
API_KEY = st.sidebar.text_input("🔑 Alpha Vantage API Key", type="password")
ticker = st.sidebar.text_input("📈 美股代號", value="AAPL").upper()
days = st.sidebar.slider("📅 顯示天數", 30, 365, 180)

# 按鈕放在側邊欄
analyze_clicked = st.sidebar.button("🚀 分析", use_container_width=True)

@st.cache_data(ttl=3600)
def get_stock_data(symbol, api_key):
    """抓取股票資料"""
    try:
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}"
        r = requests.get(url, timeout=30)
        data = r.json()
        
        if "Time Series (Daily)" not in data:
            return None
        
        df = pd.DataFrame.from_dict(data["Time Series (Daily)"], orient='index')
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        df = df[['4. close']]
        df.columns = ['close']
        df['close'] = pd.to_numeric(df['close'])
        return df
    except:
        return None

# 主要邏輯
if analyze_clicked:
    if not API_KEY:
        st.warning("⚠️ 請輸入 Alpha Vantage API Key")
        st.info("🔑 免費取得：https://www.alphavantage.co/support/#api-key")
    else:
        with st.spinner("載入資料中..."):
            df = get_stock_data(ticker, API_KEY)
            
            if df is None or df.empty:
                st.error(f"❌ 無法取得 {ticker} 的資料")
                st.info("請檢查：\n1. API Key 是否正確\n2. 代號是否為美股（如 AAPL, TSLA）")
            else:
                # 顯示最新股價
                latest = df['close'].iloc[-1]
                prev = df['close'].iloc[-2]
                change = ((latest / prev) - 1) * 100
                
                col1, col2, col3 = st.columns(3)
                col1.metric("💰 最新股價", f"${latest:.2f}")
                col2.metric("📈 日變動", f"{change:.2f}%")
                col3.metric("📊 資料天數", f"{len(df)} 天")
                
                # 計算簡單指標
                df['MA20'] = df['close'].rolling(20).mean()
                df['MA50'] = df['close'].rolling(50).mean()
                
                # 顯示最近 20 天動量
                if len(df) >= 20:
                    mom = ((df['close'].iloc[-1] / df['close'].iloc[-20]) - 1) * 100
                    st.metric("🚀 20日動量", f"{mom:.2f}%")
                
                # 價格走勢圖
                st.subheader("📉 價格走勢")
                df_show = df.tail(days)
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df_show.index, y=df_show['close'], 
                                         name=ticker, line=dict(color='blue', width=2)))
                fig.add_trace(go.Scatter(x=df_show.index, y=df_show['MA20'], 
                                         name='20日均線', line=dict(color='orange', width=1, dash='dash')))
                
                fig.update_layout(height=400, margin=dict(l=10, r=10, t=20, b=20))
                st.plotly_chart(fig, use_container_width=True)
                
                st.caption("📌 資料來源：Alpha Vantage API")
else:
    # 初始畫面（尚未點擊按鈕時顯示）
    st.info("👈 請輸入 API Key 和股票代號，然後點擊「分析」")
    st.markdown("""
    ### 📌 支援的美股代號
    AAPL, TSLA, NVDA, AMD, MSFT, GOOGL, AMZN, META
    
    ### 🔑 免費取得 API Key
    1. 前往 https://www.alphavantage.co/support/#api-key
    2. 輸入 Email 和姓名
    3. 點擊「GET FREE API KEY」
    4. 複製 Key 貼到左側欄位
    """)
