# QuorvexAI Market Report

Automated daily market intelligence — stocks, crypto, sentiment, and technical signals — delivered straight to your inbox.

## Overview

QuorvexAI Market Report is a Python-based financial analysis tool that runs automatically each weekday morning and emails a professionally formatted HTML report covering equity and cryptocurrency markets. It combines price data, technical indicators, sentiment analysis, and trend signals into a single, actionable digest.

Built for investors and analysts who want a daily edge without manual research.

## Features

- Stock and Crypto Coverage: Tracks a configurable list of equities and cryptocurrency pairs
- RSI Signals: Flags overbought (>70) and oversold (<30) conditions per ticker
- 50-Day Moving Average: Identifies price position relative to the 50-MA trend line
- Per-Ticker Sentiment Scoring: Pulls recent headlines via Yahoo Finance RSS and scores them using TextBlob
- HTML Email Delivery: Styled report with color-coded badges sent automatically via Gmail SMTP
- Scheduled Automation: Runs via cron on weekdays at 10:00 AM

## Tech Stack

- Market Data: yfinance
- Technical Indicators: ta
- Data Processing: pandas
- Sentiment Analysis: TextBlob
- Email Delivery: smtplib via Gmail SMTP
- Scheduling: cron (Linux)

## Getting Started

### Prerequisites

- Python 3.x
- A Gmail account with an App Password enabled
- Linux environment for cron scheduling

### Installation

Clone the repo and install dependencies:

    git clone https://github.com/quorvexai-jpg/quorvex-market-report.git
    cd quorvex-market-report
    pip install yfinance pandas ta textblob requests python-dotenv

### Configuration

Create a .env file in the project folder:

    GMAIL_ADDRESS=your-email@gmail.com
    GMAIL_APP_PASSWORD=your-app-password
    RECIPIENT_EMAIL=recipient1@example.com,recipient2@example.com

Never commit your .env file to GitHub.

### Running Manually

    python3 stock_crypto_report.py

### Automating with Cron

Open crontab with: crontab -e

Then add this line:

    0 10 * * 1-5 /usr/bin/python3 /path/to/stock_crypto_report.py

## Roadmap

- [x] RSI signals per ticker
- [x] 50-Day moving average trend detection
- [x] Per-ticker sentiment scoring via Yahoo Finance RSS and TextBlob
- [x] Styled HTML email with color-coded badges
- [x] Crypto section
- [x] Volume spike detection
- [ ] Sector-level performance grouping
- [ ] Web dashboard (SaaS frontend)
- [ ] User subscription management
- [ ] Configurable ticker watchlists via UI

## Disclaimer

QuorvexAI Market Report is an informational tool only. Nothing in this report constitutes financial advice, a recommendation to buy or sell any security, or investment guidance of any kind. Always do your own research and consult a licensed financial advisor before making investment decisions.

## License

MIT License — free to use, modify, and distribute with attribution.

Built by QuorvexAI
