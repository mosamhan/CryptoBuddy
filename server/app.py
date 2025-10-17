from flask import Flask, jsonify, request, make_response
from flask_cors import CORS, cross_origin
import requests
import numpy as np
from datetime import datetime, timedelta
import json
import time
import logging

app = Flask(__name__)

# Simplify CORS setup - apply to all routes
CORS(app)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# CoinMarketCap API configuration - using production API
CMC_API_URL = "https://pro-api.coinmarketcap.com"
CMC_HEADERS = {
    "X-CMC_PRO_API_KEY": "b018a79d-86fd-4867-927b-a7244e40e6fc",  # User's production API key
    "Accept": "application/json"
}

# Simple in-memory cache for API responses
cache = {}
cache_duration = 60  # Cache duration in seconds

# Mock trending data for testing
MOCK_TRENDING_COINS = [
    {
        "id": "btc",
        "name": "Bitcoin",
        "symbol": "BTC",
        "thumb": "https://s2.coinmarketcap.com/static/img/coins/64x64/1.png"
    },
    {
        "id": "eth",
        "name": "Ethereum",
        "symbol": "ETH",
        "thumb": "https://s2.coinmarketcap.com/static/img/coins/64x64/1027.png"
    },
    {
        "id": "sol",
        "name": "Solana",
        "symbol": "SOL",
        "thumb": "https://s2.coinmarketcap.com/static/img/coins/64x64/5426.png"
    },
    {
        "id": "avax",
        "name": "Avalanche",
        "symbol": "AVAX",
        "thumb": "https://s2.coinmarketcap.com/static/img/coins/64x64/5805.png"
    },
    {
        "id": "dot",
        "name": "Polkadot",
        "symbol": "DOT",
        "thumb": "https://s2.coinmarketcap.com/static/img/coins/64x64/6636.png"
    },
    {
        "id": "link",
        "name": "Chainlink",
        "symbol": "LINK",
        "thumb": "https://s2.coinmarketcap.com/static/img/coins/64x64/1975.png"
    },
    {
        "id": "matic",
        "name": "Polygon",
        "symbol": "MATIC",
        "thumb": "https://s2.coinmarketcap.com/static/img/coins/64x64/3890.png"
    }
]

def get_cached_or_fetch(cache_key, fetch_func):
    """Get data from cache or fetch it if expired/missing"""
    try:
        current_time = time.time()
        if cache_key in cache and current_time - cache[cache_key]['timestamp'] < cache_duration:
            logger.info(f"Serving cached data for key: {cache_key}")
            return cache[cache_key]['data']
        
        # Fetch fresh data
        logger.info(f"Cache miss for key: {cache_key}, fetching fresh data")
        data = fetch_func()
        
        # Only cache successful responses
        if not isinstance(data, tuple):  # Not an error response
            cache[cache_key] = {
                'data': data,
                'timestamp': current_time
            }
        
        return data
    except Exception as e:
        logger.error(f"Error in cache/fetch mechanism: {str(e)}")
        # If an exception occurs, try to return from cache anyway if available
        if cache_key in cache:
            logger.warning(f"Returning stale cache for key: {cache_key} due to error")
            return cache[cache_key]['data']
        # If no cache available, return a generic error
        return {"error": "An error occurred processing your request"}, 500

@app.route("/api/crypto/<coin>")
def get_crypto_data(coin):
    """Get data for a specific cryptocurrency"""
    def fetch_data():
        try:
            logger.info(f"Fetching data for cryptocurrency: {coin}")
            # First get the ID using the ID Map endpoint which is more reliable
            map_url = f"{CMC_API_URL}/v1/cryptocurrency/map"
            map_params = {
                "symbol": coin.upper(),
                "listing_status": "active"
            }
            map_response = requests.get(map_url, headers=CMC_HEADERS, params=map_params)
            
            # Check if the request was successful
            if map_response.status_code != 200:
                logger.error(f"Map API request failed with status code {map_response.status_code}: {map_response.text}")
                return {"error": f"Failed to fetch cryptocurrency data: {map_response.status_code}"}, 500
                
            map_data = map_response.json()
            logger.info(f"Map response for {coin.upper()}: {map_data}")
            
            if "data" not in map_data or not map_data["data"]:
                logger.warning(f"No data found for cryptocurrency: {coin}")
                return {"error": f"Could not find cryptocurrency: {coin}"}, 404
            
            # Use the first matching coin ID
            coin_id = map_data["data"][0]["id"]
            logger.info(f"Found coin ID: {coin_id} for symbol: {coin}")
            
            # Now get quotes using ID which is most reliable
            url = f"{CMC_API_URL}/v1/cryptocurrency/quotes/latest"
            params = {
                "id": str(coin_id),
                "convert": "USD",
                "aux": "cmc_rank,max_supply,circulating_supply,total_supply"
            }
            response = requests.get(url, headers=CMC_HEADERS, params=params)
            
            # Check if the request was successful
            if response.status_code != 200:
                logger.error(f"Quotes API request failed with status code {response.status_code}: {response.text}")
                return {"error": f"Failed to fetch quote data: {response.status_code}"}, 500
                
            data = response.json()
            logger.info(f"Quotes response for ID {coin_id}: {data}")
            
            if "data" not in data or not data["data"]:
                logger.warning(f"No quote data found for coin ID: {coin_id}")
                return {"error": f"Could not fetch quotes for: {coin}"}, 404
            
            # Extract the data
            coin_data = list(data["data"].values())[0]
            quote = coin_data["quote"]["USD"]
            
            # Get logo URL
            logo_url = f"https://s2.coinmarketcap.com/static/img/coins/64x64/{coin_id}.png"
            
            result = {
                "id": coin,  # Use the slug/symbol passed in for consistency
                "name": coin_data["name"],
                "symbol": coin_data["symbol"],
                "image": logo_url,
                "current_price": quote["price"],
                "market_cap": quote["market_cap"],
                "total_volume": quote["volume_24h"],
                "price_change_percentage_1h": quote["percent_change_1h"],
                "price_change_percentage_24h": quote["percent_change_24h"],
                "price_change_percentage_7d": quote["percent_change_7d"],
            }
            logger.info(f"Successfully fetched data for {coin}")
            return result
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error fetching crypto data: {str(e)}")
            return {"error": "Network error. Please try again later."}, 503
        except Exception as e:
            logger.error(f"Error fetching crypto data: {str(e)}")
            if 'response' in locals() and hasattr(response, 'text'):
                logger.error(f"API response text: {response.text}")
            return {"error": "An unexpected error occurred. Please try again later."}, 500
    
    result = get_cached_or_fetch(f"crypto_{coin}", fetch_data)
    if isinstance(result, tuple):  # Error response
        return jsonify(result[0]), result[1]
    return jsonify(result)

@app.route("/api/crypto/trending")
@app.route("/api/trending") # Alias for backward compatibility
def get_trending():
    """Get trending cryptocurrencies - MOCK DATA"""
    logger.info("Serving mock trending cryptocurrencies")
    return jsonify({"coins": MOCK_TRENDING_COINS})

@app.route("/api/crypto/<coin>/history")
def get_crypto_history(coin):
    """Get historical price data for a cryptocurrency"""
    days = request.args.get('days', '7')
    cache_key = f"history_{coin}_{days}"
    
    def fetch_data():
        try:
            # First resolve the coin id from listings endpoint
            listings_url = f"{CMC_API_URL}/v1/cryptocurrency/listings/latest"
            listings_params = {
                "start": "1",
                "limit": "5000",
                "convert": "USD",
                "sort": "market_cap",
                "sort_dir": "desc",
                "cryptocurrency_type": "all",
                "status": "active"
            }
            listings_response = requests.get(listings_url, headers=CMC_HEADERS, params=listings_params)
            listings_data = listings_response.json()
            
            coin_data = None
            # Find the coin in listings
            if "data" in listings_data:
                for listing in listings_data["data"]:
                    if listing["slug"] == coin or listing["symbol"].lower() == coin.lower():
                        coin_data = listing
                        break
            
            if not coin_data:
                # Try to get it directly
                quotes_url = f"{CMC_API_URL}/v1/cryptocurrency/quotes/latest"
                quotes_params = {"symbol": coin.upper(), "convert": "USD"}
                quotes_response = requests.get(quotes_url, headers=CMC_HEADERS, params=quotes_params)
                quotes_data = quotes_response.json()
                
                if "data" in quotes_data and quotes_data["data"] and coin.upper() in quotes_data["data"]:
                    coin_data = quotes_data["data"][coin.upper()]
            
            if not coin_data:
                return {"error": "Cryptocurrency not found"}, 404
            
            # Use current price for simulation
            current_price = coin_data["quote"]["USD"]["price"]
            
            days_int = int(days)
            end_date = datetime.now()
            prices = []
            market_caps = []
            total_volumes = []
            
            # Generate simulated data points
            for i in range(days_int * 24 if days_int <= 3 else days_int):
                # Move backwards in time
                if days_int <= 3:
                    point_time = end_date - timedelta(hours=i)
                else:
                    point_time = end_date - timedelta(days=i)
                timestamp = int(point_time.timestamp() * 1000)
                
                # Add some random price variation (±5%)
                variation = (np.random.random() - 0.5) * 0.1
                point_price = current_price * (1 + variation * (i / (days_int * 24 if days_int <= 3 else days_int)))
                
                prices.append([timestamp, point_price])
                
                # Simulate market cap and volume based on price
                market_cap = point_price * (coin_data.get("total_supply", 1e9) or 1e9)
                volume = market_cap * (np.random.random() * 0.1)  # 0-10% of market cap
                
                market_caps.append([timestamp, market_cap])
                total_volumes.append([timestamp, volume])
            
            # Sort data by timestamp (ascending)
            prices.sort(key=lambda x: x[0])
            market_caps.sort(key=lambda x: x[0])
            total_volumes.sort(key=lambda x: x[0])
            
            return {
                "prices": prices,
                "market_caps": market_caps,
                "total_volumes": total_volumes,
                "note": "Using simulated historical data for free API tier"
            }
        except Exception as e:
            print(f"Error fetching historical data: {e}")
            if 'listings_response' in locals() and hasattr(listings_response, 'text'):
                print(f"Listings API response: {listings_response.text}")
            return {"error": str(e)}, 500
    
    result = get_cached_or_fetch(cache_key, fetch_data)
    if isinstance(result, tuple):  # Error response
        return jsonify(result[0]), result[1]
    return jsonify(result)

@app.route("/api/crypto/<coin>/analysis")
def get_ai_analysis(coin):
    """Generate AI analysis for a cryptocurrency"""
    cache_key = f"analysis_{coin}"
    
    def fetch_data():
        try:
            # Get coin price from listings endpoint
            listings_url = f"{CMC_API_URL}/v1/cryptocurrency/listings/latest"
            listings_params = {
                "start": "1",
                "limit": "5000",
                "convert": "USD",
                "sort": "market_cap",
                "sort_dir": "desc",
                "cryptocurrency_type": "all",
                "status": "active"
            }
            listings_response = requests.get(listings_url, headers=CMC_HEADERS, params=listings_params)
            listings_data = listings_response.json()
            
            coin_info = None
            # Find the coin in listings
            if "data" in listings_data:
                for listing in listings_data["data"]:
                    if listing["slug"] == coin or listing["symbol"].lower() == coin.lower():
                        coin_info = listing
                        break
            
            if not coin_info:
                # Try to get it directly
                quotes_url = f"{CMC_API_URL}/v1/cryptocurrency/quotes/latest"
                quotes_params = {"symbol": coin.upper(), "convert": "USD"}
                quotes_response = requests.get(quotes_url, headers=CMC_HEADERS, params=quotes_params)
                quotes_data = quotes_response.json()
                
                if "data" in quotes_data and quotes_data["data"] and coin.upper() in quotes_data["data"]:
                    coin_info = quotes_data["data"][coin.upper()]
            
            if not coin_info:
                return {"error": "Cryptocurrency not found"}, 404
            
            current_price = coin_info["quote"]["USD"]["price"]
            
            # Generate simulated historical prices for analysis
            days = 30
            end_date = datetime.now()
            prices = []
            
            # Create 30 days of simulated price data
            for i in range(days):
                day = end_date - timedelta(days=i)
                # More realistic price movements: trend with some randomness
                trend_factor = np.sin(i / 5) * 0.1  # Cyclical trend
                random_factor = (np.random.random() - 0.5) * 0.05  # Daily noise
                day_price = current_price * (1 + trend_factor + random_factor)
                prices.append(day_price)
            
            # Reverse to get chronological order
            prices.reverse()
            
            # Calculate technical indicators
            analysis = {}
            
            # Calculate RSI
            def calculate_rsi(prices, period=14):
                deltas = np.diff(prices)
                seed = deltas[:period+1]
                up = seed[seed >= 0].sum()/period
                down = -seed[seed < 0].sum()/period
                rs = up/down if down != 0 else float('inf')
                rsi = 100 - (100/(1+rs))
                return rsi
            
            try:
                analysis["rsi"] = calculate_rsi(prices)
                
                # Moving Averages
                analysis["ma_7"] = sum(prices[-7:])/7
                analysis["ma_30"] = sum(prices)/len(prices)
                
                # Determine trend
                uptrend_days = 0
                for i in range(len(prices)-1, 0, -1):
                    if prices[i] > prices[i-1]:
                        uptrend_days += 1
                    else:
                        break
                
                downtrend_days = 0
                for i in range(len(prices)-1, 0, -1):
                    if prices[i] < prices[i-1]:
                        downtrend_days += 1
                    else:
                        break
                
                # Generate recommendation
                recommendation = ""
                coin_name = coin_info["name"].upper()
                
                if analysis["rsi"] < 30:
                    recommendation += f"{coin_name} looks oversold. RSI at {analysis['rsi']:.2f}. "
                    if uptrend_days > 0:
                        recommendation += f"Trending up {uptrend_days} days. Might be a good entry point."
                    else:
                        recommendation += f"But still in a downtrend for {downtrend_days} days. Consider waiting for trend reversal."
                elif analysis["rsi"] > 70:
                    recommendation += f"{coin_name} looks overbought. RSI at {analysis['rsi']:.2f}. "
                    if downtrend_days > 0:
                        recommendation += f"Trending down {downtrend_days} days. Consider taking profits."
                    else:
                        recommendation += f"Still in an uptrend for {uptrend_days} days. Monitor closely."
                else:
                    if uptrend_days > 2:
                        recommendation += f"{coin_name} is in an uptrend for {uptrend_days} days. "
                        if analysis["ma_7"] > analysis["ma_30"]:
                            recommendation += "Short term MA above long term MA signals bullish momentum."
                        else:
                            recommendation += "Wait for short term MA to cross above long term MA for stronger confirmation."
                    elif downtrend_days > 2:
                        recommendation += f"{coin_name} is in a downtrend for {downtrend_days} days. "
                        if analysis["ma_7"] < analysis["ma_30"]:
                            recommendation += "Short term MA below long term MA signals bearish momentum."
                        else:
                            recommendation += "Wait for short term MA to cross below long term MA for stronger confirmation."
                    else:
                        recommendation += f"{coin_name} is consolidating. No clear trend. Wait for a breakout."
                
                analysis["recommendation"] = recommendation
                analysis["trend"] = "uptrend" if uptrend_days > downtrend_days else "downtrend" if downtrend_days > uptrend_days else "neutral"
                analysis["trend_days"] = max(uptrend_days, downtrend_days)
                analysis["note"] = "Analysis based on simulated historical data for free API tier"
                
            except Exception as e:
                analysis["error"] = str(e)
                analysis["recommendation"] = f"Unable to generate recommendation for {coin_info['name']}. Insufficient data."
            
            return analysis
            
        except Exception as e:
            print(f"Error performing analysis: {e}")
            if 'listings_response' in locals() and hasattr(listings_response, 'text'):
                print(f"Listings API response: {listings_response.text}")
            return {"error": str(e)}, 500
    
    result = get_cached_or_fetch(cache_key, fetch_data)
    if isinstance(result, tuple):  # Error response
        return jsonify(result[0]), result[1]
    return jsonify(result)

@app.route("/api/search")
def search_crypto():
    """Search for cryptocurrencies"""
    query = request.args.get("query", "")
    # Also check for 'q' parameter for backwards compatibility
    if not query:
        query = request.args.get("q", "")
        
    query = query.lower()
    if not query:
        logger.warning("Search request with no query parameter")
        return jsonify({"error": "Query parameter is required"}), 400
    
    logger.info(f"Searching for cryptocurrency with query: '{query}'")
    
    def fetch_data():
        try:
            # Use the map endpoint for a broader search
            url = f"{CMC_API_URL}/v1/cryptocurrency/map"
            params = {
                "listing_status": "active",
                "limit": "2000"  # Increased from 100 to get more coins
            }
            response = requests.get(url, headers=CMC_HEADERS, params=params)
            
            # Check if the request was successful
            if response.status_code != 200:
                logger.error(f"Map API request failed with status code {response.status_code}: {response.text}")
                return {"error": f"Failed to search cryptocurrencies: {response.status_code}"}, 500
                
            data = response.json()
            logger.info(f"Map response received with {len(data.get('data', []))} coins")
            
            if "data" not in data:
                logger.warning("No data in map response")
                return {"error": "Failed to retrieve cryptocurrency data"}, 500
            
            # Filter coins based on search query (search in both name and symbol)
            filtered_coins = []
            for coin in data["data"]:
                if (query in coin["name"].lower() or 
                    query in coin["symbol"].lower() or
                    (coin.get("slug") and query in coin["slug"].lower())):
                    
                    coin_id = coin["id"]
                    filtered_coins.append({
                        "id": coin["slug"],  # Using slug instead of symbol"].lower(),
                        "name": coin["name"],
                        "symbol": coin["symbol"],
                        "image": f"https://s2.coinmarketcap.com/static/img/coins/64x64/{coin_id}.png"
                    })
                
                # Limit results to 20 coins
                if len(filtered_coins) >= 20:
                    break
            
            logger.info(f"Found {len(filtered_coins)} coins matching query '{query}'")
            return {"coins": filtered_coins}
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error searching for cryptocurrencies: {str(e)}")
            return {"error": "Network error. Please try again later."}, 503
        except Exception as e:
            logger.error(f"Error searching for cryptocurrencies: {str(e)}")
            if 'response' in locals() and hasattr(response, 'text'):
                logger.error(f"API response text: {response.text}")
            return {"error": "An unexpected error occurred. Please try again later."}, 500
    
    result = get_cached_or_fetch(f"search_{query}", fetch_data)
    if isinstance(result, tuple):  # Error response
        return jsonify(result[0]), result[1]
    return jsonify(result)

@app.route('/health')
def health_check():
    """Health check endpoint to verify API is running"""
    try:
        # Verify we can reach CoinMarketCap API
        response = requests.get(
            f"{CMC_API_URL}/v1/cryptocurrency/map",
            headers=CMC_HEADERS,
            params={"limit": "1"}
        )
        api_status = "healthy" if response.status_code == 200 else "unhealthy"
        
        return jsonify({
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "coinmarketcap_api": api_status,
            "version": "1.0.0"
        })
    except Exception as e:
        logger.error(f"Error in health check: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

# Explicitly add CORS headers to all responses
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    if request.method == 'OPTIONS':
        # Handle OPTIONS request specially
        response.status_code = 200
    return response

# Simple test endpoint that doesn't require API calls
@app.route('/api/test')
def test_endpoint():
    return jsonify({
        "status": "success",
        "message": "CORS is working correctly!",
        "timestamp": datetime.now().isoformat()
    })

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
