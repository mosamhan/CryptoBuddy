import { useState, useEffect } from 'react';
import { fetchFromAPI } from '../services/api';

function TrendingCoins({ onSelectCoin }) {
  const [trendingCoins, setTrendingCoins] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchTrendingCoins = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const data = await fetchFromAPI('/api/crypto/trending');
        setTrendingCoins(data.coins || []);
      } catch (err) {
        console.error('Error fetching trending coins:', err);
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };

    fetchTrendingCoins();
  }, []);

  if (isLoading) {
    return (
      <div className="trending-section">
        <div className="loading">
          <div className="loading-spinner"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  if (!trendingCoins.length) {
    return <div>No trending coins available at the moment.</div>;
  }

  return (
    <div>
      <h3>Trending Coins</h3>
      <div className="trending-section">
        {trendingCoins.slice(0, 7).map((coin) => (
          <div 
            key={coin.id} 
            className="trending-coin"
            onClick={() => onSelectCoin(coin.id)}
          >
            <img src={coin.thumb} alt={coin.name} />
            <span>{coin.symbol}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default TrendingCoins; 