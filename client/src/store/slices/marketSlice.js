import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

// Async thunk for fetching market data
export const fetchMarketData = createAsyncThunk(
  'market/fetchMarketData',
  async (params, { rejectWithValue }) => {
    try {
      const symbolFilter = params?.symbols?.[0] ?? '';
      const url = symbolFilter
        ? `/api/v1/stocks/?symbol=${encodeURIComponent(symbolFilter.replace('.SR', ''))}`
        : '/api/v1/stocks/';

      const response = await axios.get(url, { timeout: 15000 });

      // Transform array to map keyed by symbol
      const stocks = response.data?.data ?? [];
      const dataMap = {};
      stocks.forEach(stock => {
        if (stock.symbol) dataMap[stock.symbol] = stock;
      });

      return {
        symbols: stocks.map(s => s.symbol).filter(Boolean),
        data: dataMap,
        collection_date: new Date().toISOString().slice(0, 10),
      };
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to fetch market data');
    }
  }
);

const initialState = {
  symbols: [],
  data: {},
  collectionDate: null,
  status: 'idle', // 'idle' | 'loading' | 'succeeded' | 'failed'
  error: null
};

const marketSlice = createSlice({
  name: 'market',
  initialState,
  reducers: {
    setSymbols: (state, action) => {
      state.symbols = action.payload;
    },
    clearMarketData: (state) => {
      state.data = {};
      state.status = 'idle';
      state.error = null;
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchMarketData.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(fetchMarketData.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.symbols = action.payload?.symbols ?? [];
        state.data = action.payload?.data ?? {};
        state.collectionDate = action.payload?.collection_date ?? null;
      })
      .addCase(fetchMarketData.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload;
      });
  }
});

export const { setSymbols, clearMarketData } = marketSlice.actions;

export default marketSlice.reducer;
