import yfinance as yf
from dotenv import load_dotenv
import os

load_dotenv()
import smtplib
import time
import pandas as pd
import ta
import feedparser
from textblob import TextBlob
from email.mime.text import MIMEText

# === CREDENTIALS ===
GMAIL_ADDRESS = os.getenv('GMAIL_ADDRESS')
GMAIL_APP_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL').split(',')

# === ALERT LOGIC ===
def get_alert_badges(rsi, current, ma50, volume_ratio):
    alerts = []
    if rsi < 30:
        alerts.append(("🟢 OVERSOLD (RSI {:.0f})".format(rsi), "#1a7a3f"))
    elif rsi > 70:
        alerts.append(("🔴 OVERBOUGHT (RSI {:.0f})".format(rsi), "#a81c1c"))
    if current > ma50:
        alerts.append(("📈 ABOVE 50-MA", "#1a4fa8"))
    else:
        alerts.append(("📉 BELOW 50-MA", "#a87a1a"))
    if volume_ratio >= 1.5:
        alerts.append(("🔊 VOLUME SPIKE ({:.1f}x avg)".format(volume_ratio), "#6a0dad"))
    badges = ""
    for label, color in alerts:
        badges += (
            f'<span style="display:inline-block;margin:2px 4px 2px 0;'
            f'padding:2px 8px;border-radius:4px;font-size:12px;'
            f'font-weight:bold;color:white;background:{color};">'
            f'{label}</span>'
        )
    return f'<div style="margin-top:5px;">{badges}</div>'

# === SENTIMENT LOGIC ===
def get_sentiment_html(symbol):
    url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={symbol}&region=US&lang=en-US"
    try:
        feed = feedparser.parse(url)
        entries = feed.entries[:8]
        if not entries:
            return '<div style="font-size:12px;color:#888;margin-top:4px;">Sentiment: NEUTRAL (+0.000)</div>'
        scores = [TextBlob(e.get("title", "") + " " + e.get("summary", "")).sentiment.polarity for e in entries]
        avg = sum(scores) / len(scores)
        if avg >= 0.1:
            label, color = "BULLISH", "#1a7a3f"
        elif avg <= -0.1:
            label, color = "BEARISH", "#a81c1c"
        else:
            label, color = "NEUTRAL", "#888888"
        return (
            f'<div style="font-size:12px;color:#555;margin-top:4px;">'
            f'Sentiment: <span style="font-weight:bold;color:{color};">'
            f'{label} ({avg:+.3f})</span></div>'
        )
    except Exception:
        return '<div style="font-size:12px;color:#888;margin-top:4px;">Sentiment: unavailable</div>'

# === FETCH PRICE AND INDICATORS ===
def analyze(symbol):
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period='3mo')
    closes = hist['Close']
    current = closes.iloc[-1]
    rsi = ta.momentum.RSIIndicator(closes).rsi().iloc[-1]
    ma50 = closes.rolling(50).mean().iloc[-1]
    volumes = hist['Volume']
    avg_volume = volumes.iloc[-21:-1].mean()
    today_volume = volumes.iloc[-1]
    volume_ratio = today_volume / avg_volume if avg_volume > 0 else 0
    return current, rsi, ma50, volume_ratio

# === FETCH CRYPTO ===
def fetch_crypto_prices():
    import requests
    url = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd'
    response = requests.get(url)
    data = response.json()
    return data['bitcoin']['usd'], data['ethereum']['usd']

# === MAIN ===
symbols = ['AAPL', 'TSLA', 'NVDA', 'AMZN', 'SPY', 'XLK', 'XLE']
results = {}
for symbol in symbols:
    print(f'Fetching {symbol}...')
    price, rsi, ma50, volume_ratio = analyze(symbol)
    results[symbol] = (price, rsi, ma50, volume_ratio)

btc, eth = fetch_crypto_prices()

# === BUILD HTML EMAIL ===
rows = ""
for symbol, (price, rsi, ma50, volume_ratio) in results.items():
    badges = get_alert_badges(rsi, price, ma50, volume_ratio)
    sentiment = get_sentiment_html(symbol)
    rows += f"""
    <tr>
      <td style="padding:12px 16px;border-bottom:1px solid #eee;vertical-align:top;">
        <div style="font-size:16px;font-weight:bold;color:#222;">{symbol}</div>
        <div style="font-size:13px;color:#555;margin-top:2px;">
          Price: <b>${price:.2f}</b> &nbsp;|&nbsp;
          RSI: <b>{rsi:.1f}</b> &nbsp;|&nbsp;
          50-MA: <b>${ma50:.2f}</b>
        </div>
        {badges}
        {sentiment}
      </td>
    </tr>"""

html = f"""
<html><body style="font-family:Arial,sans-serif;background:#f5f5f5;padding:20px;">
<div style="max-width:600px;margin:auto;background:white;border-radius:8px;
            box-shadow:0 2px 8px rgba(0,0,0,0.08);overflow:hidden;">

  <div style="background:#1a1a2e;padding:20px 24px;">
    <h2 style="color:white;margin:0;font-size:20px;">📊 Daily Market Report</h2>
    <p style="color:#aaa;margin:4px 0 0;font-size:13px;">Stocks &amp; Crypto Summary</p>
  </div>

  <div style="padding:16px 16px 8px;">
    <h3 style="margin:0 0 8px;font-size:14px;color:#888;text-transform:uppercase;
               letter-spacing:1px;">Stocks &amp; ETFs</h3>
    <table style="width:100%;border-collapse:collapse;">{rows}</table>
  </div>

  <div style="padding:16px 24px 24px;">
    <h3 style="margin:0 0 12px;font-size:14px;color:#888;text-transform:uppercase;
               letter-spacing:1px;">Crypto</h3>
    <table style="width:100%;border-collapse:collapse;">
      <tr>
        <td style="padding:10px 0;border-bottom:1px solid #eee;">
          <span style="font-size:16px;font-weight:bold;">₿ Bitcoin</span>
          <span style="float:right;font-size:16px;font-weight:bold;color:#f7931a;">${btc:,}</span>
        </td>
      </tr>
      <tr>
        <td style="padding:10px 0;">
          <span style="font-size:16px;font-weight:bold;">Ξ Ethereum</span>
          <span style="float:right;font-size:16px;font-weight:bold;color:#627eea;">${eth:,}</span>
        </td>
      </tr>
    </table>
  </div>

  <div style="background:#f9f9f9;padding:12px 24px;border-top:1px solid #eee;">
    <p style="margin:0;font-size:11px;color:#aaa;">
      Generated by QuorvexAI · Not financial advice
    </p>
  </div>

</div>
</body></html>
"""

# === SEND EMAIL ===
msg = MIMEText(html, 'html')
msg['Subject'] = '📊 Daily Market Report'
msg['From'] = GMAIL_ADDRESS
msg['To'] = ', '.join(RECIPIENT_EMAIL)

with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
    server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
    server.sendmail(GMAIL_ADDRESS, RECIPIENT_EMAIL, msg.as_string())

print("Email sent successfully!")
