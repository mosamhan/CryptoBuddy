import { useState, useEffect } from 'react';
import { fetchFromAPI } from '../services/api';

function AIAdvisor({ coinId }) {
  const [aiAnalysis, setAiAnalysis] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchAnalysis = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const data = await fetchFromAPI(`/api/crypto/${coinId}/analysis`);
        setAiAnalysis(data);
      } catch (err) {
        console.error('Error fetching AI analysis:', err);
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };

    fetchAnalysis();
  }, [coinId]);

  if (isLoading) {
    return (
      <div className="card ai-advisor">
        <h2>AI Investment Advisor</h2>
        <div className="loading">
          <div className="loading-spinner"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card ai-advisor">
        <h2>AI Investment Advisor</h2>
        <div className="error">Error: {error}</div>
      </div>
    );
  }

  if (!aiAnalysis || aiAnalysis.error) {
    return (
      <div className="card ai-advisor">
        <h2>AI Investment Advisor</h2>
        <div className="error">
          {aiAnalysis?.error || 'Unable to generate analysis at this time. Insufficient historical data may be available.'}
        </div>
      </div>
    );
  }

  return (
    <div className="card ai-advisor">
      <h2>AI Investment Advisor</h2>
      
      <div className={`trend-indicator trend-${aiAnalysis.trend || 'neutral'}`}>
        {aiAnalysis.trend === 'uptrend' ? '📈 Uptrend' : 
         aiAnalysis.trend === 'downtrend' ? '📉 Downtrend' : 
         '📊 Neutral'}
        {aiAnalysis.trend_days > 0 && ` for ${aiAnalysis.trend_days} days`}
      </div>
      
      <p className="ai-recommendation">
        {aiAnalysis.recommendation || 'No recommendation available at this time.'}
      </p>
      
      <div className="ai-stats">
        <div className="ai-stat">
          <div className="ai-stat-label">RSI (14)</div>
          <div className={`ai-stat-value ${aiAnalysis.rsi < 30 ? 'positive' : aiAnalysis.rsi > 70 ? 'negative' : ''}`}>
            {aiAnalysis.rsi ? aiAnalysis.rsi.toFixed(2) : 'N/A'}
          </div>
        </div>
        
        <div className="ai-stat">
          <div className="ai-stat-label">7-Day MA</div>
          <div className="ai-stat-value">
            {aiAnalysis.ma_7 ? `$${aiAnalysis.ma_7.toLocaleString(undefined, { maximumFractionDigits: 2 })}` : 'N/A'}
          </div>
        </div>
        
        <div className="ai-stat">
          <div className="ai-stat-label">30-Day MA</div>
          <div className="ai-stat-value">
            {aiAnalysis.ma_30 ? `$${aiAnalysis.ma_30.toLocaleString(undefined, { maximumFractionDigits: 2 })}` : 'N/A'}
          </div>
        </div>
        
        <div className="ai-stat">
          <div className="ai-stat-label">MA Signal</div>
          {aiAnalysis.ma_7 && aiAnalysis.ma_30 ? (
            <div className={`ai-stat-value ${aiAnalysis.ma_7 > aiAnalysis.ma_30 ? 'positive' : 'negative'}`}>
              {aiAnalysis.ma_7 > aiAnalysis.ma_30 ? 'Bullish' : 'Bearish'}
            </div>
          ) : (
            <div className="ai-stat-value">N/A</div>
          )}
        </div>
      </div>
      
      <div className="ai-disclaimer">
        <small>This is not financial advice. Always do your own research before investing.</small>
        <small className="simulated-data-note">* Analysis based on simulated data (CoinMarketCap free API tier limitation)</small>
      </div>
    </div>
  );
}

export default AIAdvisor; 