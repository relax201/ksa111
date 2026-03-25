import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

// Async thunk for fetching financial data
export const fetchFinancialData = createAsyncThunk(
  'financial/fetchFinancialData',
  async (params, { rejectWithValue }) => {
    try {
      const symbol = (params.symbols?.[0] ?? '2222.SR').replace('.SR', '');
      const response = await axios.get(`/api/v1/stocks/${encodeURIComponent(symbol)}/financials`, {
        timeout: 15000,
      });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to fetch financial data');
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

const financialSlice = createSlice({
  name: 'financial',
  initialState,
  reducers: {
    setSymbols: (state, action) => {
      state.symbols = action.payload;
    },
    clearFinancialData: (state) => {
      state.data = {};
      state.status = 'idle';
      state.error = null;
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchFinancialData.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(fetchFinancialData.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.symbols = action.payload?.symbols ?? [];
        state.data = action.payload?.data ?? {};
        state.collectionDate = action.payload?.collection_date ?? null;
      })
      .addCase(fetchFinancialData.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload;
      });
  }
});

export const { setSymbols, clearFinancialData } = financialSlice.actions;

export default financialSlice.reducer;