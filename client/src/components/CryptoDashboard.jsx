import { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { fetchFromAPI } from '../services/api';

function CryptoDashboard({ coinId }) {
  const [coinData, setCoinData] = useState(null);
  const [historicalData, setHistoricalData] = useState([]);
  const [timeframe, setTimeframe] = useState('7');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      setError(null);
      try {
        // Fetch coin data
        const coinDataResult = await fetchFromAPI(`/api/crypto/${coinId}`);
        setCoinData(coinDataResult);

        // Fetch historical data
        const historyDataResult = await fetchFromAPI(`/api/crypto/${coinId}/history?days=${timeframe}`);
        
        // Format chart data
        if (historyDataResult.prices && historyDataResult.prices.length > 0) {
          const formattedData = historyDataResult.prices.map(item => ({
            timestamp: item[0],
            date: new Date(item[0]).toLocaleDateString(),
            price: item[1],
          }));
          
          setHistoricalData(formattedData);
        } else {
          setHistoricalData([]);
          console.warn('No historical price data available');
        }
      } catch (err) {
        console.error('Error fetching data:', err);
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [coinId, timeframe]);

  const formatPrice = (price) => {
    if (!price && price !== 0) return '$0.00';
    
    if (price >= 1000) {
      return `$${price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    } else if (price >= 1) {
      return `$${price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 6 })}`;
    } else {
      return `$${price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 8 })}`;
    }
  };

  const formatPercentage = (percentage) => {
    if (!percentage && percentage !== 0) return '0.00%';
    return `${percentage >= 0 ? '+' : ''}${percentage.toFixed(2)}%`;
  };

  if (isLoading) {
    return (
      <div className="card">
        <div className="loading">
          <div className="loading-spinner"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card error">
        <h2>Error</h2>
        <p>{error}</p>
        <p>Please try another cryptocurrency or refresh the page.</p>
      </div>
    );
  }

  if (!coinData) {
    return <div className="card error">No data available</div>;
  }

  const isPositiveChange = (percentage) => percentage >= 0;

  return (
    <div className="card">
      <div className="coin-info-header">
        <img src={coinData.image} alt={coinData.name} />
        <div>
          <h2 className="coin-title">{coinData.name}<span className="coin-symbol">{coinData.symbol.toUpperCase()}</span></h2>
          <div className="coin-price">{formatPrice(coinData.current_price)}</div>
          <div className={isPositiveChange(coinData.price_change_percentage_24h) ? 'positive' : 'negative'}>
            {formatPercentage(coinData.price_change_percentage_24h)} (24h)
          </div>
        </div>
      </div>

      <div className="coin-info">
        <div className="coin-stat">
          <div className="coin-stat-label">Market Cap</div>
          <div className="coin-stat-value">${(coinData.market_cap || 0).toLocaleString()}</div>
        </div>
        <div className="coin-stat">
          <div className="coin-stat-label">Trading Volume (24h)</div>
          <div className="coin-stat-value">${(coinData.total_volume || 0).toLocaleString()}</div>
        </div>
        <div className="coin-stat">
          <div className="coin-stat-label">1h Change</div>
          <div className={`coin-stat-value ${isPositiveChange(coinData.price_change_percentage_1h) ? 'positive' : 'negative'}`}>
            {formatPercentage(coinData.price_change_percentage_1h)}
          </div>
        </div>
        <div className="coin-stat">
          <div className="coin-stat-label">7d Change</div>
          <div className={`coin-stat-value ${isPositiveChange(coinData.price_change_percentage_7d) ? 'positive' : 'negative'}`}>
            {formatPercentage(coinData.price_change_percentage_7d)}
          </div>
        </div>
      </div>

      <div className="time-filter">
        <button
          className={`time-button ${timeframe === '1' ? 'active' : ''}`}
          onClick={() => setTimeframe('1')}
        >
          24h
        </button>
        <button
          className={`time-button ${timeframe === '7' ? 'active' : ''}`}
          onClick={() => setTimeframe('7')}
        >
          7d
        </button>
        <button
          className={`time-button ${timeframe === '14' ? 'active' : ''}`}
          onClick={() => setTimeframe('14')}
        >
          14d
        </button>
        <button
          className={`time-button ${timeframe === '30' ? 'active' : ''}`}
          onClick={() => setTimeframe('30')}
        >
          30d
        </button>
        <button
          className={`time-button ${timeframe === '90' ? 'active' : ''}`}
          onClick={() => setTimeframe('90')}
        >
          90d
        </button>
      </div>

      <div className="chart-container">
        {historicalData.length > 0 ? (
          <>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart
                data={historicalData}
                margin={{ top: 5, right: 20, left: 10, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(128, 128, 128, 0.2)" />
                <XAxis 
                  dataKey="date" 
                  tick={{ fontSize: 12 }}
                  tickCount={7}
                />
                <YAxis 
                  domain={['auto', 'auto']}
                  tickFormatter={(value) => `$${value.toLocaleString()}`}
                  tick={{ fontSize: 12 }}
                  width={80}
                />
                <Tooltip 
                  formatter={(value) => [`${formatPrice(value)}`, 'Price']}
                  labelFormatter={(label) => `Date: ${label}`}
                />
                <Line 
                  type="monotone" 
                  dataKey="price" 
                  stroke={coinData.price_change_percentage_24h >= 0 ? '#16c784' : '#ea3943'} 
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
            <div className="chart-note">
              * Chart shows simulated data based on current price (CoinMarketCap free API tier limitation)
            </div>
          </>
        ) : (
          <div className="loading">No chart data available for this timeframe</div>
        )}
      </div>
    </div>
  );
}

export default CryptoDashboard; 