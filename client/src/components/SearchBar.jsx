import { useState, useEffect, useRef } from 'react';
import { fetchFromAPI } from '../services/api';

function SearchBar({ onSelectCoin }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const searchContainerRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (searchContainerRef.current && !searchContainerRef.current.contains(event.target)) {
        setShowResults(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  useEffect(() => {
    const delayDebounce = setTimeout(() => {
      if (searchTerm.length > 1) {
        performSearch();
      } else {
        setSearchResults([]);
      }
    }, 500);

    return () => clearTimeout(delayDebounce);
  }, [searchTerm]);

  const performSearch = async () => {
    setIsLoading(true);
    try {
      const data = await fetchFromAPI(`/api/search?query=${searchTerm}`);
      setSearchResults(data.coins || []);
      setShowResults(true);
    } catch (error) {
      console.error('Error searching coins:', error);
      setSearchResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectCoin = (coinId) => {
    onSelectCoin(coinId);
    setSearchTerm('');
    setShowResults(false);
  };

  return (
    <div className="search-container" ref={searchContainerRef}>
      <input
        type="text"
        className="search-input"
        placeholder="Search for a cryptocurrency..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        onFocus={() => searchTerm.length > 1 && setShowResults(true)}
      />
      
      {showResults && searchResults.length > 0 && (
        <div className="search-results">
          {searchResults.map((coin) => (
            <div 
              key={coin.id}
              className="search-result-item"
              onClick={() => handleSelectCoin(coin.id)}
            >
              <img src={coin.thumb} alt={coin.name} />
              <span className="coin-name">{coin.name}</span>
              <span className="coin-symbol">{coin.symbol}</span>
            </div>
          ))}
        </div>
      )}
      
      {isLoading && (
        <div className="loading">
          <div className="loading-spinner"></div>
        </div>
      )}
    </div>
  );
}

export default SearchBar; 