# AI Crypto Dashboard

A modern cryptocurrency dashboard with artificial intelligence-powered investment suggestions based on technical analysis and market trends.

## Features

- **Crypto Price Dashboard**
  - Live price data from CoinMarketCap API
  - Price change percentages (1h, 24h, 7d)
  - Volume and market cap data
  - Interactive price charts with various timeframes
  - Search functionality and trending coins display

- **AI Investment Advisor**
  - Technical indicator analysis (RSI, Moving Averages)
  - Trend detection (uptrends/downtrends)
  - Automatic investment recommendations
  - Clear visual indicators for market conditions

## Optimized API Implementation

- **Server-Side Caching**: 60-second caching for all API requests to minimize API usage
- **Simulated Historical Data**: For free API tier users, the app generates realistic simulated data for charts and analysis
- **Efficient Batch Requests**: Where possible, data is fetched in batches (e.g., all trending coin logos in one request)
- **Error Handling**: Comprehensive error handling with friendly user messages

## Tech Stack

- **Frontend:** React, Vite, Recharts, TailwindCSS
- **Backend:** Flask, NumPy
- **APIs:** CoinMarketCap API

## Installation

### Prerequisites
- Node.js (v14+)
- Python (v3.6+)
- npm or yarn
- CoinMarketCap API Key (provided in code)

### Backend Setup

```bash
cd server
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install flask flask-cors requests numpy
python app.py
```

The Flask server will start on http://localhost:5000

### Frontend Setup

```bash
cd client
npm install
npm run dev
```

The React development server will start on http://localhost:5173

## Usage

1. Browse trending cryptocurrencies or search for a specific coin
2. View detailed price information and historical charts
3. Check the AI Investment Advisor panel for technical analysis and recommendations
4. Switch between different timeframes to analyze price movements
5. Use the dark/light mode toggle for your preferred theme

## API Key

This application uses the CoinMarketCap API which requires an API key. A key is already configured in the application, but if you need to use your own:

1. Sign up for an API key at [CoinMarketCap](https://coinmarketcap.com/api/)
2. Replace the `CMC_API_KEY` variable in `server/app.py` with your new key

## Free Tier Limitations & Solutions

The CoinMarketCap API has limitations on the free Basic plan:
- 10,000 call credits per month
- 30 calls per minute
- No access to historical data endpoints

To work around these limitations, our implementation includes:
- **Efficient Caching**: Responses are cached for 60 seconds to reduce API calls
- **Simulated Historical Data**: Charts use simulated data based on current prices
- **AI Analysis on Simulated Data**: Technical indicators and recommendations are based on simulated historical prices

If you need actual historical data, consider upgrading to a paid CoinMarketCap API plan.

## Disclaimer

The AI investment suggestions provided by this application are for informational purposes only and should not be considered financial advice. Always do your own research before making investment decisions.
