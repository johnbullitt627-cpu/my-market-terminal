import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd

# --- STYLING ---
st.set_page_config(layout="wide", page_title="Wealth Management Terminal")

st.markdown("""
    <style>
    .stApp { background-color: #0c0c0c; color: #ffffff; }
    [data-testid="stMetricValue"] { color: #00FF00 !important; font-family: 'Courier New'; }
    .stButton>button { border: 1px solid #444; background-color: #111; color: #00FF00; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIG ---
WATCHLIST = ['SPY', 'QQQ', 'DIA', 'IWM', 'TSLA', 'AAPL', 'NVDA', '^TNX', 'DX-Y.NYB']

@st.cache_data(ttl=60)
def get_market_data(ticker):
    try:
        # Fetching 5 days to ensure we have enough data points even after weekends
        df = yf.download(ticker, period="5d", interval="1m", progress=False)
        if df.empty:
            return None, None, None
        
        # Pulling the last available price and the previous close
        current_price = float(df['Close'].iloc[-1])
        open_price = float(df['Close'].iloc[0])
        change = current_price - open_price
        pct_change = (change / open_price) * 100
        return current_price, change, pct_change
    except Exception:
        return None, None, None

st.title("📊 INSTITUTIONAL MARKET DASHBOARD")

if 'active_ticker' not in st.session_state:
    st.session_state.active_ticker = 'SPY'

# --- THE GRID ---
cols = st.columns(3)
for i, ticker in enumerate(WATCHLIST):
    with cols[i % 3]:
        p, c, pct = get_market_data(ticker)
        
        # Bulletproof formatting: only show numbers if they exist
        val_display = f"{p:,.2f}" if p is not None else "Data N/A"
        delta_display = f"{pct:.2f}%" if pct is not None else "N/A"
        
        st.metric(label=ticker, value=val_display, delta=delta_display)
        
        if st.button(f"CHART {ticker}", key=f"btn_{ticker}"):
            st.session_state.active_ticker = ticker

# --- THE CHART ---
st.divider()
active = st.session_state.active_ticker
try:
    chart_df = yf.download(active, period="1mo", interval="1h", progress=False)
    fig = go.Figure(data=[go.Candlestick(
        x=chart_df.index,
        open=chart_df['Open'], high=chart_df['High'],
        low=chart_df['Low'], close=chart_df['Close'])])
    fig.update_layout(title=f"Technical View: {active}", template="plotly_dark", height=600)
    st.plotly_chart(fig, use_container_width=True)
except:
    st.error(f"Could not load chart for {active}")
