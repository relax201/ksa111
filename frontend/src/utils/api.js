import axios from 'axios';
import { API_URL } from './constants';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
});

// Add request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle common errors
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response && error.response.status === 401) {
      // Unauthorized - clear token and redirect to login
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Market API
export const marketApi = {
  getOverview: () => api.get('/market'),
  getIndices: () => api.get('/market/indices'),
  getSectors: () => api.get('/market/sectors'),
  getTopGainers: (limit = 5) => api.get(`/market/top-gainers?limit=${limit}`),
  getTopLosers: (limit = 5) => api.get(`/market/top-losers?limit=${limit}`),
  getMostActive: (limit = 5) => api.get(`/market/most-active?limit=${limit}`),
  updateMarketData: () => api.post('/market/update')
};

// Stock API
export const stockApi = {
  getAll: (params = {}) => api.get('/stocks', { params }),
  getBySymbol: (symbol) => api.get(`/stocks/${symbol}`),
  getHistoricalPrices: (symbol, timeFrame = '1m') => api.get(`/stocks/${symbol}/prices?time_frame=${timeFrame}`),
  getFinancials: (symbol) => api.get(`/stocks/${symbol}/financials`),
  search: (term) => api.get(`/stocks/search?term=${term}`)
};

// Technical Analysis API
export const technicalApi = {
  getIndicators: (symbol, indicators = [], timeFrame = '1m') => {
    return api.get(`/analysis/technical/${symbol}?indicators=${indicators.join(',')}&time_frame=${timeFrame}`);
  },
  getChartPatterns: (symbol, timeFrame = '1m') => {
    return api.get(`/analysis/technical/${symbol}/patterns?time_frame=${timeFrame}`);
  },
  getSupportResistance: (symbol) => {
    return api.get(`/analysis/technical/${symbol}/support-resistance`);
  }
};

// Fundamental Analysis API
export const fundamentalApi = {
  getRatios: (symbol) => api.get(`/analysis/fundamental/${symbol}/ratios`),
  getValuation: (symbol) => api.get(`/analysis/fundamental/${symbol}/valuation`),
  getGrowth: (symbol) => api.get(`/analysis/fundamental/${symbol}/growth`),
  getPeerComparison: (symbol) => api.get(`/analysis/fundamental/${symbol}/peer-comparison`)
};

// Recommendation API
export const recommendationApi = {
  getAll: (params = {}) => api.get('/recommendations', { params }),
  getBySymbol: (symbol) => api.get(`/recommendations/stock/${symbol}`),
  getPortfolioRecommendations: () => api.get('/recommendations/portfolio'),
  updateSettings: (settings) => api.put('/recommendations/settings', settings)
};

// Screener API
export const screenerApi = {
  screen: (filters) => api.post('/screener', { filters }),
  getSavedScreens: () => api.get('/screener/saved'),
  saveScreen: (screen) => api.post('/screener/save', screen),
  deleteScreen: (id) => api.delete(`/screener/saved/${id}`)
};

// Portfolio API
export const portfolioApi = {
  getAll: () => api.get('/portfolios'),
  getById: (id) => api.get(`/portfolios/${id}`),
  create: (data) => api.post('/portfolios', data),
  update: (id, data) => api.put(`/portfolios/${id}`, data),
  delete: (id) => api.delete(`/portfolios/${id}`),
  addStock: (portfolioId, data) => api.post(`/portfolios/${portfolioId}/stocks`, data),
  removeStock: (portfolioId, stockId) => api.delete(`/portfolios/${portfolioId}/stocks/${stockId}`),
  updateStock: (portfolioId, stockId, data) => api.put(`/portfolios/${portfolioId}/stocks/${stockId}`, data)
};

// Alerts API
export const alertsApi = {
  getAll: () => api.get('/alerts'),
  getById: (id) => api.get(`/alerts/${id}`),
  create: (data) => api.post('/alerts', data),
  update: (id, data) => api.put(`/alerts/${id}`, data),
  delete: (id) => api.delete(`/alerts/${id}`),
  markAsRead: (id) => api.put(`/alerts/${id}/read`)
};

// User API
export const userApi = {
  getProfile: () => api.get('/user/profile'),
  updateProfile: (data) => api.put('/user/profile', data),
  updatePassword: (data) => api.put('/user/password', data),
  updateNotificationSettings: (data) => api.put('/user/notifications', data)
};

export default api;