import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  darkMode: false,
  sidebarOpen: true,
  language: 'ar',
  notifications: [],
  selectedStock: null,
  stockSearchQuery: '',
  dateRange: {
    start: null,
    end: null
  }
};

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    toggleDarkMode: (state) => {
      state.darkMode = !state.darkMode;
    },
    toggleSidebar: (state) => {
      state.sidebarOpen = !state.sidebarOpen;
    },
    setLanguage: (state, action) => {
      state.language = action.payload;
    },
    addNotification: (state, action) => {
      state.notifications.push({
        id: Date.now(),
        ...action.payload
      });
    },
    removeNotification: (state, action) => {
      state.notifications = state.notifications.filter(
        (notification) => notification.id !== action.payload
      );
    },
    clearNotifications: (state) => {
      state.notifications = [];
    },
    setSelectedStock: (state, action) => {
      state.selectedStock = action.payload;
    },
    setStockSearchQuery: (state, action) => {
      state.stockSearchQuery = action.payload;
    },
    setDateRange: (state, action) => {
      state.dateRange = action.payload;
    }
  }
});

export const {
  toggleDarkMode,
  toggleSidebar,
  setLanguage,
  addNotification,
  removeNotification,
  clearNotifications,
  setSelectedStock,
  setStockSearchQuery,
  setDateRange
} = uiSlice.actions;

export default uiSlice.reducer;