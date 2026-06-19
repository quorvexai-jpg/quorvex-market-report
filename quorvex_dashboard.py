import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import feedparser
import requests
import plotly.graph_objects as go
from textblob import TextBlob
from dotenv import load_dotenv

load_dotenv()

# === PAGE CONFIG ===
st.set_page_config(
    page_title="QuorvexAI",
    page_icon="📊",
    layout="wide"
)

# === CUSTOM CSS ===
st.markdown("""
<style>
    .main { background-color: #f5f5f5; }
    .quorvex-header {
        background: #1a1a2e;
        padding: 24px 28px;
        border-radius: 10px;
        margin-bottom: 24px;
    }
    .quorvex-header h1 {
        color: white;
        margin: 0;
        font-size: 26px;
    }
    .quorvex-header p {
        color: #aaa;
        margin: 4px 0 0;
        font-size: 13px;
    }
    .ticker-card {
        background: white;
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 12px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.06);
    }
    .ticker-symbol {
        font-size: 18px;
        font-weight: bold;
        color: #1a1a2e;
    }
    .ticker-meta {
        font-size: 13px;
        color: #555;
        margin-top: 4px;
    }
    .badge {
        display: inline-block;
        margin: 3px 4px 3px 0;
        padding: 3px 10px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
        color: white;
    }
    .crypto-card {
        background: white;
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 10px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.06);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .footer {
        text-align: center;
        color: #aaa;
        font-size: 11px;
        margin-top: 32px;
    }
</style>
""", unsafe_allow_html=True)

# === HEADER ===
st.markdown("""
<div class="quorvex-header">
    <h1>📊 QuorvexAI Market Dashboard</h1>
    <p>Enter tickers below to run a live analysis · Not financial advice</p>
</div>
""", unsafe_allow_html=True)

# === ALERT BADGES ===
def get_alert_badges(rsi, current, ma50, volume_ratio):
    badges = ""
    if rsi < 30:
        badges += f'<span class="badge" style="background:#1a7a3f;">🟢 OVERSOLD (RSI {rsi:.0f})</span>'
    elif rsi > 70:
        badges += f'<span class="badge" style="background:#a81c1c;">🔴 OVERBOUGHT (RSI {rsi:.0f})</span>'
    if current > ma50:
        badges += '<span class="badge" style="background:#1a4fa8;">📈 ABOVE 50-MA</span>'
    else:
        badges += '<span class="badge" style="background:#a87a1a;">📉 BELOW 50-MA</span>'
    if volume_ratio >= 1.5:
        badges += f'<span class="badge" style="background:#6a0dad;">🔊 VOLUME SPIKE ({volume_ratio:.1f}x avg)</span>'
    return f'<div style="margin-top:8px;">{badges}</div>'

# === SENTIMENT ===
def get_sentiment_html(symbol):
    url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={symbol}&region=US&lang=en-US"
    try:
        feed = feedparser.parse(url)
        entries = feed.entries[:8]
        if not entries:
            return '<div style="font-size:12px;color:#888;margin-top:6px;">Sentiment: NEUTRAL (+0.000)</div>'
        scores = [TextBlob(e.get("title", "") + " " + e.get("summary", "")).sentiment.polarity for e in entries]
        avg = sum(scores) / len(scores)
        if avg >= 0.1:
            label, color = "BULLISH", "#1a7a3f"
        elif avg <= -0.1:
            label, color = "BEARISH", "#a81c1c"
        else:
            label, color = "NEUTRAL", "#888888"
        return (
            f'<div style="font-size:12px;color:#555;margin-top:6px;">'
            f'Sentiment: <span style="font-weight:bold;color:{color};">{label} ({avg:+.3f})</span></div>'
        )
    except Exception:
        return '<div style="font-size:12px;color:#888;margin-top:6px;">Sentiment: unavailable</div>'

# === ANALYZE ===
def analyze(symbol):
    ticker = yf.Ticker(symbol)
    try:
        hist = ticker.history(period='3mo')
    except Exception:
        return "rate_limited"
    if hist.empty or len(hist) < 10:
        return None
    closes = hist['Close']
    current = closes.iloc[-1]
    rsi = ta.momentum.RSIIndicator(closes).rsi().iloc[-1]
    ma50 = closes.rolling(50).mean().iloc[-1]
    volumes = hist['Volume']
    avg_volume = volumes.iloc[-21:-1].mean()
    today_volume = volumes.iloc[-1]
    volume_ratio = today_volume / avg_volume if avg_volume > 0 else 0
    return current, rsi, ma50, volume_ratio, hist

# === CANDLESTICK CHART ===
def make_candlestick_chart(symbol, hist):
    ma50_series = hist['Close'].rolling(50).mean()

    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=hist.index,
        open=hist['Open'],
        high=hist['High'],
        low=hist['Low'],
        close=hist['Close'],
        name=symbol,
        increasing_line_color='#1a7a3f',
        decreasing_line_color='#a81c1c',
    ))

    fig.add_trace(go.Scatter(
        x=hist.index,
        y=ma50_series,
        line=dict(color='#1a4fa8', width=1.5),
        name='50-MA',
    ))

    fig.update_layout(
        height=350,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis_rangeslider_visible=False,
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white',
        yaxis=dict(side='right', gridcolor='#eee'),
        xaxis=dict(gridcolor='#eee'),
    )
    return fig

# === CRYPTO ===
def fetch_crypto(coin_id):
    try:
        url = f'https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd'
        response = requests.get(url, timeout=5)
        data = response.json()
        return data[coin_id]['usd']
    except Exception:
        return None

# === SUPABASE CLIENT ===
from supabase import create_client

@st.cache_resource
def get_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    st.write(f"DEBUG URL: {url}")
    return create_client(url, key)

supabase = get_supabase()

# === WATCHLIST (Supabase-backed, single shared watchlist for now) ===
def load_watchlist():
    try:
        response = supabase.table("watchlists").select("*").eq("id", "default").execute()
        if response.data:
            return response.data[0]["stocks"], response.data[0]["crypto"]
        return "", ""
    except Exception:
        return "", ""
def save_watchlist(stocks, crypto):
    try:
        supabase.table("watchlists").upsert({
            "id": "default",
            "stocks": stocks,
            "crypto": crypto
        }).execute()
        return True
    except Exception as e:
        st.error(f"DEBUG: {e}")
        return False

# === INPUT SECTION ===
saved_stocks, saved_crypto = load_watchlist()
default_stocks = saved_stocks if saved_stocks else ""
default_crypto = saved_crypto if saved_crypto else ""

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("#### Stocks & ETFs")
    stock_input = st.text_input(
        "Enter stock/ETF tickers separated by commas",
        value=default_stocks,
        placeholder="e.g. AAPL, TSLA, SPY",
        key="stock_input_box"
    )

with col2:
    st.markdown("#### Crypto")
    crypto_input = st.text_input(
        "Enter crypto CoinGecko IDs separated by commas",
        value=default_crypto,
        placeholder="e.g. bitcoin, ethereum, solana"
    )

btn_col1, btn_col2 = st.columns([3, 1])
with btn_col1:
    run = st.button("🚀 Run Analysis", type="primary", use_container_width=True)
with btn_col2:
    save_clicked = st.button("💾 Save Watchlist", use_container_width=True)

if save_clicked:
    success = save_watchlist(stock_input, crypto_input)
    if success:
        st.toast("Watchlist saved!", icon="✅")
    else:
        st.toast("Couldn't save watchlist - try again.", icon="⚠️")

# === RUN ANALYSIS ===
if run:
    stock_symbols = [s.strip().upper() for s in stock_input.split(',') if s.strip()]
    crypto_ids = [c.strip().lower() for c in crypto_input.split(',') if c.strip()]

    # --- STOCKS ---
    if stock_symbols:
        st.markdown("---")
        st.markdown("### 📈 Stocks & ETFs")
        for symbol in stock_symbols:
            with st.spinner(f"Fetching {symbol}..."):
                result = analyze(symbol)
            if result == "rate limited":
                st.warning(f"⚠️ Cahoo Finance is currently rate-limiting requests. Please wait a moment and try again for **{symbol}** .")
                continue
            if result is None:
                st.warning(f"⚠️ Could not fetch data  for **{symbol}** - check the ticker and try again.")
                continue
            price, rsi, ma50, volume_ratio, hist = result
            badges = get_alert_badges(rsi, price, ma50, volume_ratio)
            sentiment = get_sentiment_html(symbol)
            st.markdown(f"""
            <div class="ticker-card">
                <div class="ticker-symbol">{symbol}</div>
                <div class="ticker-meta">
                    Price: <b>${price:.2f}</b> &nbsp;|&nbsp;
                    RSI: <b>{rsi:.1f}</b> &nbsp;|&nbsp;
                    50-MA: <b>${ma50:.2f}</b>
                </div>
                {badges}
                {sentiment}
            </div>
            """, unsafe_allow_html=True)
            with st.expander(f"📊 View {symbol} candlestick chart (3mo)"):
                fig = make_candlestick_chart(symbol, hist)
                st.plotly_chart(fig, use_container_width=True, key=f"chart_{symbol}")

    # --- CRYPTO ---
    if crypto_ids:
        st.markdown("---")
        st.markdown("### 🪙 Crypto")

        crypto_display = {
            "bitcoin": ("₿ Bitcoin", "#f7931a"),
            "ethereum": ("Ξ Ethereum", "#627eea"),
            "solana": ("◎ Solana", "#9945ff"),
            "dogecoin": ("Ð Dogecoin", "#c2a633"),
            "cardano": ("₳ Cardano", "#0033ad"),
        }

        for coin_id in crypto_ids:
            with st.spinner(f"Fetching {coin_id}..."):
                price = fetch_crypto(coin_id)
            if price is None:
                st.warning(f"⚠️ Could not fetch data for **{coin_id}** — check the CoinGecko ID.")
                continue
            label, color = crypto_display.get(coin_id, (coin_id.capitalize(), "#333333"))
            st.markdown(f"""
            <div class="crypto-card">
                <span style="font-size:16px;font-weight:bold;">{label}</span>
                <span style="font-size:18px;font-weight:bold;color:{color};">${price:,}</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="footer">Generated by QuorvexAI · Not financial advice</div>', unsafe_allow_html=True)
# trigger redeploy
# trigger redeploy
