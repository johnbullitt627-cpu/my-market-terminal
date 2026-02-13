import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd

# --- ADVISOR TERMINAL STYLING ---
st.set_page_config(layout="wide", page_title="Wealth Management Terminal")

# Professional "Bloomberg" Dark Theme
st.markdown("""
    <style>
    .stApp { background-color: #0c0c0c; color: #ffffff; }
    [data-testid="stMetricValue"] { color: #00FF00 !important; font-family: 'Courier New'; }
    .stButton>button { border: 1px solid #444; background-color: #111; color: #00FF00; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- WATCHLIST CONFIG ---
# Added sectors and macro indicators for a Senior Director's oversight
WATCHLIST = ['SPY', 'QQQ', 'DIA', 'IWM', 'TSLA', 'AAPL', 'NVDA', '^TNX', 'DX-Y.NYB']

@st.cache_data(ttl=60) # Cache for 1 minute to keep it fast
def get_market_data(ticker):
    try:
        data = yf.download(ticker, period="2d", interval="1m")
        price = data['Close'].iloc[-1]
        change = price - data['Close'].iloc[0]
        pct = (change / data['Close'].iloc[0]) * 100
        return price, change, pct
    except:
        return 0, 0, 0

st.title("📊 INSTITUTIONAL MARKET DASHBOARD")

if 'active_ticker' not in st.session_state:
    st.session_state.active_ticker = 'SPY'

# --- 1. THE GRID (3 Columns) ---
cols = st.columns(3)
for i, ticker in enumerate(WATCHLIST):
    with cols[i % 3]:
        p, c, pct = get_market_data(ticker)
        st.metric(label=ticker, value=f"{p:,.2f}", delta=f"{pct:.2f}%")
        if st.button(f"CHART {ticker}", key=f"btn_{ticker}"):
            st.session_state.active_ticker = ticker

# --- 2. MASTER-DETAIL CHART ---
st.divider()
active = st.session_state.active_ticker
df = yf.download(active, period="1mo", interval="1h")

fig = go.Figure(data=[go.Candlestick(x=df.index,
                open=df['Open'], high=df['High'],
                low=df['Low'], close=df['Close'])])

fig.update_layout(title=f"Technical View: {active}", template="plotly_dark", 
                  height=600, plot_bgcolor='black', paper_bgcolor='black')
st.plotly_chart(fig, use_container_width=True)
