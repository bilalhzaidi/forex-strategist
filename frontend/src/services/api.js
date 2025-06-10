import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response) {
      console.error('API Error:', error.response.data);
    } else if (error.request) {
      console.error('Network Error:', error.request);
    } else {
      console.error('Error:', error.message);
    }
    return Promise.reject(error);
  }
);

export const forexAPI = {
  // Health check
  healthCheck: async () => {
    const response = await api.get('/health');
    return response.data;
  },

  // Analyze currency pair
  analyzeCurrencyPair: async (currencyPair) => {
    const response = await api.post('/analyze', {
      currency_pair: currencyPair
    });
    return response.data;
  },

  // Get current exchange rate
  getCurrentRate: async (currencyPair) => {
    const response = await api.get(`/rates/${currencyPair}`);
    return response.data;
  },

  // Get news for currency pair
  getCurrencyNews: async (currencyPair, days = 7) => {
    const response = await api.get(`/news/${currencyPair}`, {
      params: { days }
    });
    return response.data;
  },

  // Get recommendation history
  getRecommendationHistory: async (currencyPair, limit = 20) => {
    const response = await api.get(`/history/${currencyPair}`, {
      params: { limit }
    });
    return response.data;
  },

  // Get supported currency pairs
  getSupportedPairs: async () => {
    const response = await api.get('/supported-pairs');
    return response.data;
  }
};

export default api;