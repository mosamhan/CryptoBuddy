import { API_BASE_URL } from '../App';

/**
 * Makes a fetch request to the API with proper CORS settings
 * 
 * @param {string} endpoint - The API endpoint to fetch from
 * @param {Object} options - Additional fetch options
 * @returns {Promise<any>} - The JSON response from the API
 */
export const fetchFromAPI = async (endpoint, options = {}) => {
  try {
    const url = `${API_BASE_URL}${endpoint}`;
    
    // Default options are marked with *
    const fetchOptions = {
      method: options.method || 'GET',
      mode: 'cors', // no-cors, *cors, same-origin
      cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
      credentials: 'omit', // include, *same-origin, omit
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      redirect: 'follow', // manual, *follow, error
      referrerPolicy: 'no-referrer', // no-referrer, *no-referrer-when-downgrade, origin, origin-when-cross-origin, same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url
      ...options,
    };
    
    console.log(`Fetching from: ${url}`, fetchOptions);
    const response = await fetch(url, fetchOptions);
    
    if (!response.ok) {
      let errorMessage = `API error: ${response.status}`;
      try {
        const errorData = await response.json();
        errorMessage = errorData.error || errorMessage;
      } catch (e) {
        // If JSON parsing fails, use the default error message
      }
      throw new Error(errorMessage);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`API request failed for ${endpoint}:`, error);
    throw error;
  }
}; 