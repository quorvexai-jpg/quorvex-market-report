# QuorvexAI Market Report

Automated daily market intelligence — stocks, crypto, sentiment, and technical signals — delivered straight to your inbox, or explored live in an interactive web dashboard.

**🚀 Try the live dashboard: [quorvexai.streamlit.app](https://quorvexai.streamlit.app/)**

## Overview

QuorvexAI is a Python-based financial analysis project covering equity and cryptocurrency markets. It combines price data, technical indicators, sentiment analysis, and trend signals into actionable insights — available two ways:

- **Email Report**: An automated daily HTML report sent each weekday morning for a fixed watchlist
- **Web Dashboard**: An interactive Streamlit app where anyone can enter their own tickers, view candlestick charts, and run analysis on demand

Built for investors and analysts who want a daily edge without manual research.

## Features

### Core Analysis
- Stock and Crypto Coverage: Tracks a configurable list of equities and cryptocurrency pairs
- RSI Signals: Flags overbought (>70) and oversold (<30) conditions per ticker
- 50-Day Moving Average: Identifies price position relative to the 50-MA trend line
- Per-Ticker Sentiment Scoring: Pulls recent headlines via Yahoo Finance RSS and scores them using TextBlob
- Volume Spike Detection: Flags days with volume 1.5x or more above the 20-day average

### Email Report (`stock_crypto_report.py`)
- HTML Email Delivery: Styled report with color-coded badges sent automatically via Gmail SMTP
- Scheduled Automation: Runs via cron on weekdays at 10:00 AM

### Web Dashboard (`quorvex_dashboard.py`)
- Custom Ticker Input: Enter any stocks, ETFs, or crypto IDs to analyze on demand
- Interactive Candlestick Charts: 3-month price history with 50-MA overlay, zoom/pan support, per ticker
- Browser-Saved Watchlists: Save your ticker list locally in your browser — no account required — and have it auto-load next visit
- Live, publicly hosted on Streamlit Community Cloud

## Tech Stack

- Market Data: yfinance
- Technical Indicators: ta
- Data Processing: pandas
- Sentiment Analysis: TextBlob
- Charting: Plotly
- Web Dashboard: Streamlit
- Browser Storage: streamlit-js-eval
- Email Delivery: smtplib via Gmail SMTP
- Scheduling: cron (Linux)
- Hosting: Streamlit Community Cloud

## Getting Started

### Prerequisites

- Python 3.x (3.12 recommended)
- A Gmail account with an App Password enabled (for the email report only)
- Linux environment for cron scheduling (for the email report only)

### Installation

Clone the repo and install dependencies:

    git clone https://github.com/quorvexai-jpg/quorvex-market-report.git
    cd quorvex-market-report
    pip install -r requirements.txt

### Configuration

Create a `.env` file in the project folder (required for the email report; not needed to run the dashboard locally):

    GMAIL_ADDRESS=your-email@gmail.com
    GMAIL_APP_PASSWORD=your-app-password
    RECIPIENT_EMAIL=recipient1@example.com,recipient2@example.com

Never commit your `.env` file to GitHub.

### Running the Email Report Manually

    python3 stock_crypto_report.py

### Running the Web Dashboard Locally

    streamlit run quorvex_dashboard.py

Then open `http://localhost:8501` in your browser.

### Automating the Email Report with Cron

Open crontab with: `crontab -e`

Then add this line:

    0 10 * * 1-5 /usr/bin/python3 /path/to/stock_crypto_report.py

## Roadmap

- [x] RSI signals per ticker
- [x] 50-Day moving average trend detection
- [x] Per-ticker sentiment scoring via Yahoo Finance RSS and TextBlob
- [x] Styled HTML email with color-coded badges
- [x] Crypto section
- [x] Volume spike detection
- [x] Web dashboard (SaaS frontend)
- [x] Interactive candlestick charts
- [x] Browser-saved watchlists
- [ ] Sector-level performance grouping
- [ ] AI-generated buy/sell/hold analysis (premium tier)
- [ ] User accounts and subscription management
- [ ] Custom domain

## Disclaimer

QuorvexAI Market Report is an informational tool only. Nothing in this report or dashboard constitutes financial advice, a recommendation to buy or sell any security, or investment guidance of any kind. Always do your own research and consult a licensed financial advisor before making investment decisions.

## License

MIT License — free to use, modify, and distribute with attribution.

Built by QuorvexAI
