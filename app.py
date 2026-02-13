import streamlit as st
from streamlit_autorefresh import st_autorefresh
import yfinance as yf
from datetime import datetime
import pytz

# Auto-refresh every 60 seconds
st_autorefresh(interval=60000, key="market_pulse_refresh")

# Page configuration
st.set_page_config(
    page_title="Market Pulse",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Eikon/Bloomberg-style UI
st.markdown("""
<style>
    /* Global dark theme */
    .stApp {
        background-color: #0c0c0c;
    }
    
    /* Remove default padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 0rem;
        padding-left: 3rem;
        padding-right: 3rem;
    }
    
    /* Section headers */
    .section-header {
        color: #888888;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 1.5px;
        margin-bottom: 8px;
        margin-top: 16px;
        border-bottom: 1px solid #333333;
        padding-bottom: 4px;
    }
    
    /* Ticker card */
    .ticker-card {
        background-color: #1a1a1a;
        border: 1px solid #2a2a2a;
        border-radius: 4px;
        padding: 10px 12px;
        margin-bottom: 8px;
    }
    
    /* Ticker symbol */
    .ticker-symbol {
        color: #cccccc;
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 2px;
    }
    
    /* Ticker name */
    .ticker-name {
        color: #666666;
        font-size: 11px;
        margin-bottom: 6px;
    }
    
    /* Price - will be colored dynamically */
    .price {
        font-size: 20px;
        font-weight: 700;
        margin-bottom: 2px;
    }
    
    /* Change percentage - will be colored dynamically */
    .change {
        font-size: 14px;
        font-weight: 600;
    }
    
    /* Positive change */
    .positive {
        color: #00FF00;
    }
    
    /* Negative change */
    .negative {
        color: #FF0000;
    }
    
    /* Timestamp */
    .timestamp {
        color: #666666;
        font-size: 11px;
        text-align: right;
        margin-top: 12px;
    }
    
    /* Remove streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Watchlist configuration
WATCHLIST = {
    "EQUITY INDEXES": {
        "^GSPC": "S&P 500",
        "^DJI": "Dow Jones",
        "^IXIC": "NASDAQ",
        "^RUT": "Russell 2000"
    },
    "TECH/GROWTH": {
        "AAPL": "Apple",
        "MSFT": "Microsoft",
        "NVDA": "NVIDIA",
        "GOOGL": "Alphabet",
        "AMZN": "Amazon",
        "META": "Meta",
        "TSLA": "Tesla",
        "AMD": "AMD"
    },
    "MACRO & RATES": {
        "^TNX": "10Y Treasury Yield",
        "DX-Y.NYB": "US Dollar Index",
        "GC=F": "Gold Futures",
        "CL=F": "Crude Oil WTI",
        "BTC-USD": "Bitcoin"
    },
    "FIXED INCOME/FX": {
        "TLT": "20Y+ Treasury ETF",
        "IEF": "7-10Y Treasury ETF",
        "LQD": "Investment Grade Bond",
        "EURUSD=X": "EUR/USD",
        "GBPUSD=X": "GBP/USD"
    }
}

@st.cache_data(ttl=60)
def fetch_ticker_data(symbol):
    """Fetch current price and calculate accurate daily change"""
    try:
        ticker = yf.Ticker(symbol)
        
        # Use fast_info for accurate real-time data
        last_price = ticker.fast_info.get('last_price')
        previous_close = ticker.fast_info.get('previous_close')
        
        if last_price is None or previous_close is None:
            return None
        
        # Calculate accurate daily change
        change = last_price - previous_close
        change_pct = (change / previous_close) * 100
        
        return {
            'price': last_price,
            'change': change,
            'change_pct': change_pct
        }
    except Exception as e:
        return None

def render_ticker_card(symbol, name, data):
    """Render individual ticker card with Eikon-style formatting"""
    if data is None:
        return f"""
        <div class="ticker-card">
            <div class="ticker-symbol">{symbol}</div>
            <div class="ticker-name">{name}</div>
            <div style="color: #666666; font-size: 12px;">Data Unavailable</div>
        </div>
        """
    
    # Determine color class based on change
    color_class = "positive" if data['change'] >= 0 else "negative"
    
    # Format price with appropriate decimals
    if data['price'] < 1:
        price_str = f"${data['price']:.4f}"
    elif data['price'] < 10:
        price_str = f"${data['price']:.3f}"
    else:
        price_str = f"${data['price']:.2f}"
    
    # Special formatting for certain symbols
    if symbol == "^TNX":
        price_str = f"{data['price']:.3f}%"
    elif symbol in ["EURUSD=X", "GBPUSD=X"]:
        price_str = f"{data['price']:.4f}"
    
    # Format change with sign
    sign = "+" if data['change'] >= 0 else ""
    change_str = f"{sign}{data['change_pct']:.2f}%"
    
    return f"""
    <div class="ticker-card">
        <div class="ticker-symbol">{symbol}</div>
        <div class="ticker-name">{name}</div>
        <div class="price {color_class}">{price_str}</div>
        <div class="change {color_class}">{change_str}</div>
    </div>
    """

# Dashboard header
st.markdown("<h1 style='color: #ffffff; font-size: 28px; margin-bottom: 0px;'>MARKET PULSE</h1>", unsafe_allow_html=True)

# Timestamp
ny_tz = pytz.timezone('America/New_York')
current_time = datetime.now(ny_tz).strftime("%Y-%m-%d %H:%M:%S ET")
st.markdown(f"<div class='timestamp'>Last Updated: {current_time}</div>", unsafe_allow_html=True)

# Render dashboard sections
for section_name, tickers in WATCHLIST.items():
    st.markdown(f"<div class='section-header'>{section_name}</div>", unsafe_allow_html=True)
    
    # Create 4-column grid
    cols = st.columns(4)
    
    # Distribute tickers across columns
    ticker_items = list(tickers.items())
    for idx, (symbol, name) in enumerate(ticker_items):
        col_idx = idx % 4
        
        with cols[col_idx]:
            data = fetch_ticker_data(symbol)
            card_html = render_ticker_card(symbol, name, data)
            st.markdown(card_html, unsafe_allow_html=True)

# Footer with data source
st.markdown("<div class='timestamp' style='margin-top: 24px; text-align: center;'>Data Source: Yahoo Finance | Auto-refresh: 60s</div>", unsafe_allow_html=True)
