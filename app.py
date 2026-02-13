import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd

# --- TERMINAL STYLING & DYNAMIC COLORING ---
st.set_page_config(layout="wide", page_title="Wealth Management Terminal")

def get_style(color_hex):
    return f"""
    <style>
    .stApp {{ background-color: #0c0c0c; color: #ffffff; }}
    .stButton>button {{ border: 1px solid #444; background-color: #111; color: #ffffff; width: 100%; font-size: 12px; }}
    /* Custom classes for ticker colors */
    .price-up {{ color: #00FF00 !important; font-family: 'Courier New'; font-size: 20px; font-weight: bold; }}
    .price-down {{ color: #FF0000 !important; font-family: 'Courier New'; font-size: 20px; font-weight: bold; }}
    .ticker-label {{ color: #888; font-size: 12px; margin-bottom: -10px; }}
    </style>
    """
st.markdown(get_style("#00FF00"), unsafe_allow_html=True)

# --- SIDEBAR COMMAND CENTER ---
with st.sidebar:
    st.header("⌨️ Command Center")
    st.subheader("Manage Watchlist")
    
    # Default list including your favorites like SPY, QQQ, and the 10Y Yield (^TNX)
    if 'ticker_list' not in st.session_state:
        st.session_state.ticker_list = ['SPY', 'QQQ', 'DIA', 'IWM', 'TSLA', 'AAPL', 'NVDA', '^TNX', 'DX-Y.NYB']
    
    new_ticker = st.text_input("Add Ticker (e.g., MSFT, GOOG, BTC-USD):").upper()
    if st.button("Add to Grid") and new_ticker:
        if new_ticker not in st.session_state.ticker_list:
            st.session_state.ticker_list.append(new_ticker)
            st.rerun()
            
    if st.button("Clear All"):
        st.session_state.ticker_list = []
        st.rerun()

# --- DATA ENGINE ---
@st.cache_data(ttl=60)
def get_market_data(ticker):
    try:
        df = yf.download(ticker, period="2d", interval="1m", progress=False)
        if df.empty: return None, None, None
        current_price = float(df['Close'].iloc[-1])
        open_price = float(df['Close'].iloc[0])
        change_pct = ((current_price - open_price) / open_price) * 100
        return current_price, change_pct, (current_price - open_price)
    except:
        return None, None, None

# --- THE GRID ---
st.title("⚡ VIBE TERMINAL")
if 'active_ticker' not in st.session_state:
    st.session_state.active_ticker = 'SPY'

# Responsive grid (4 columns for smaller text/tighter fit)
cols = st.columns(4)
for i, ticker in enumerate(st.session_state.ticker_list):
    with cols[i % 4]:
        p, pct, raw_change = get_market_data(ticker)
        
        if p is not None:
            color_class = "price-up" if pct >= 0 else "price-down"
            arrow = "▲" if pct >= 0 else "▼"
            
            # Rendering custom HTML for the "Eikon" look
            st.markdown(f"<p class='ticker-label'>{ticker}</p>", unsafe_allow_html=True)
            st.markdown(f"<p class='{color_class}'>{p:,.2f} <span style='font-size:14px;'>{arrow} {abs(pct):.2f}%</span></p>", unsafe_allow_html=True)
            
            if st.button(f"CHART {ticker}", key=f"btn_{ticker}"):
                st.session_state.active_ticker = ticker
        else:
            st.write(f"{ticker}: N/A")

# --- MASTER CHART ---
st.divider()
active = st.session_state.active_ticker
try:
    chart_df = yf.download(active, period="1mo", interval="1h", progress=False)
    fig = go.Figure(data=[go.Candlestick(x=chart_df.index, open=chart_df['Open'], 
                    high=chart_df['High'], low=chart_df['Low'], close=chart_df['Close'])])
    fig.update_layout(title=f"Technical: {active}", template="plotly_dark", height=500, margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(fig, use_container_width=True)
except:
    st.error("Chart unavailable")
