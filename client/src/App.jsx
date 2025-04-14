import { useState, useEffect } from 'react'
import './App.css'
import CryptoDashboard from './components/CryptoDashboard'
import AIAdvisor from './components/AIAdvisor'
import SearchBar from './components/SearchBar'
import TrendingCoins from './components/TrendingCoins'

// API URL configuration - can be changed for development/production
export const API_BASE_URL = 'http://localhost:5000';

function App() {
  const [selectedCoin, setSelectedCoin] = useState('bitcoin')
  const [darkMode, setDarkMode] = useState(false)

  useEffect(() => {
    if (darkMode) {
      document.body.classList.add('dark-mode')
    } else {
      document.body.classList.remove('dark-mode')
    }
  }, [darkMode])

  return (
    <div className={`app-container ${darkMode ? 'dark-mode' : ''}`}>
      <header className="app-header">
        <h1>Crypto Buddy</h1>
        <button 
          className="theme-toggle" 
          onClick={() => setDarkMode(!darkMode)}
        >
          {darkMode ? '☀️' : '🌙'}
        </button>
      </header>
      
      <div className="main-content">
        <div className="search-section">
          <SearchBar onSelectCoin={setSelectedCoin} />
          <TrendingCoins onSelectCoin={setSelectedCoin} />
        </div>
        
        <div className="dashboard-container">
          <CryptoDashboard coinId={selectedCoin} />
          <AIAdvisor coinId={selectedCoin} />
        </div>
      </div>
      
      <footer className="app-footer">
        <p>Data provided by CoinMarketCap API • {new Date().getFullYear()}</p>
      </footer>
    </div>
  )
}

export default App
