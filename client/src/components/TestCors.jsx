import { useState } from 'react';
import { fetchFromAPI } from '../services/api';

function TestCors() {
  const [testResult, setTestResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const testCorsConnection = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await fetchFromAPI('/api/test');
      setTestResult(result);
      console.log('CORS Test Result:', result);
    } catch (err) {
      setError(err.message);
      console.error('CORS Test Error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ margin: '20px 0', padding: '15px', border: '1px solid #ddd', borderRadius: '5px' }}>
      <h3>CORS Test</h3>
      <button 
        onClick={testCorsConnection}
        disabled={loading}
        style={{ 
          padding: '8px 15px', 
          background: loading ? '#ccc' : '#007bff', 
          color: 'white', 
          border: 'none', 
          borderRadius: '4px',
          cursor: loading ? 'not-allowed' : 'pointer'
        }}
      >
        {loading ? 'Testing...' : 'Test CORS Connection'}
      </button>
      
      {error && (
        <div style={{ color: 'red', marginTop: '10px' }}>
          Error: {error}
        </div>
      )}
      
      {testResult && (
        <div style={{ marginTop: '10px' }}>
          <div style={{ color: 'green', fontWeight: 'bold' }}>
            {testResult.message}
          </div>
          <div style={{ fontSize: '12px', color: '#666' }}>
            Timestamp: {testResult.timestamp}
          </div>
        </div>
      )}
    </div>
  );
}

export default TestCors; 