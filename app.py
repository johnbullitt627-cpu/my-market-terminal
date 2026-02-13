import streamlit as st
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# --- TERMINAL STYLING & DYNAMIC COLORING ---
st.set_page_config(layout="wide", page_title="Institutional Market Terminal")

# Custom CSS for the "Eikon" Grid Aesthetic
st.markdown("""
    <style>
    /* Main background */
    .stApp { background-color: #0c0c0c; color: #ffffff; }
    
    /* Price formatting (entire string turns color) */
    .price-up { color: #00FF00 !important; font-family: 'Courier New', monospace; font-size: 18px; font-weight: bold; margin: 0; padding: 0;}
    .price-down { color: #FF0000 !important; font-family: 'Courier New', monospace; font-size: 18px; font-weight: bold; margin: 0; padding: 0;}
    
    /* Section headers and ticker labels */
    .section-header { color: #FFD700; font-size: 18px; font-weight: bold; border-bottom: 1px solid #444; margin-top: 20px; margin-bottom: 15px; padding-bottom: 5px; text-transform: uppercase;}
    .ticker-label { color: #888; font-size: 13px; margin-bottom: 2px; font-weight: 600;}
    
    /* The "Quote Box" effect */
    .metric-container { background-color: #111; padding: 12px; border-radius: 4px; border: 1px solid #333; margin-bottom: 10px;}
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE & WATCHLIST MANAGEMENT ---
# Default dictionary. You can permanently edit these here.
default_watchlist = {
    "MARKET INDEXES": ['SPY', 'QQQ', 'DIA', 'IWM'],
    "TECH & MOBILITY": ['AAPL', 'NVDA', 'TSLA', 'MSFT', 'GOOG'],
    "MACRO & YIELDS": ['^TNX', 'DX-Y.NYB', 'BTC-USD']
}

# Load into session state so it can be dynamically updated via the sidebar
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = default_watchlist

# --- SIDEBAR COMMAND CENTER ---
with st.sidebar:
    st.header("⌨️ Command Center")
    st.subheader("Add New Ticker")
    
    new_ticker = st.text_input("Ticker Symbol (e.g., AMZN, JPM):").upper()
    target_section = st.selectbox("Select Section:", list(st.session_state.watchlist.keys()))
    
    if st.button("Add to Grid") and new_ticker:
        # Prevent duplicates
        if new_ticker not in st.session_state.watchlist[target_section]:
            st.session_state.watchlist[target_section].append(new_ticker)
            st.rerun()

# --- INSTITUTIONAL DATA ENGINE ---
@st.cache_data(ttl=60) # Caches data for 60 seconds to prevent API limits
def get_market_data(ticker):
    try:
        t = yf.Ticker(ticker)
        # Using fast_info guarantees the true previous close for accurate daily % change
        info = t.fast_info 
        current_price = info['last_price']
        prev_close = info['previous_close']
        
        change = current_price - prev_close
        pct_change = (change / prev_close) * 100
        return current_price, pct_change
    except:
        return None, None

# --- MAIN DASHBOARD RENDERING ---
st.title("⚡ INSTITUTIONAL MARKET DASHBOARD")

# Iterate through sections and build the 4-column grid
for section, tickers in st.session_state.watchlist.items():
    st.markdown(f"<div class='section-header'>{section}</div>", unsafe_allow_html=True)
    
    cols = st.columns(4)
    for i, ticker in enumerate(tickers):
        with cols[i % 4]:
            p, pct = get_market_data(ticker)
            
            if p is not None:
                color_class = "price-up" if pct >= 0 else "price-down"
                arrow = "▲" if pct >= 0 else "▼"
                
                # HTML rendering for the quote boxes
                st.markdown(f"""
                    <div class='metric-container'>
                        <div class='ticker-label'>{ticker}</div>
                        <div class='{color_class}'>{p:,.2f} <span style='font-size:14px;'>{arrow} {abs(pct):.2f}%</span></div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class='metric-container'>
                        <div class='ticker-label'>{ticker}</div>
                        <div style='color: #888;'>Data N/A</div>
                    </div>
                """, unsafe_allow_html=True)

# --- AUTO REFRESH ---
# Triggers the app to re-run every 60,000 milliseconds (1 minute)
st_autorefresh(interval=60000, key="datarefresh")
