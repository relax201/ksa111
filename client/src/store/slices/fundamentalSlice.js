import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

// Async thunk for fetching fundamental analysis
export const fetchFundamentalAnalysis = createAsyncThunk(
  'fundamental/fetchFundamentalAnalysis',
  async (params, { rejectWithValue }) => {
    try {
      const symbol = (params?.symbol ?? '2222.SR').replace('.SR', '');
      const metrics = params?.metrics ?? ['PE', 'PB', 'ROE', 'EPS'];

      const response = await axios.post(
        '/api/v1/integration/fundamental-analysis',
        { symbol: `${symbol}.SR`, metrics },
        { timeout: 20000 }
      );

      return response.data?.data ?? response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to fetch fundamental analysis');
    }
  }
);

const initialState = {
  symbol: '',
  name: '',
  metrics: {},
  analysisDate: null,
  valuation: '',
  sectorComparison: {},
  status: 'idle', // 'idle' | 'loading' | 'succeeded' | 'failed'
  error: null
};

const fundamentalSlice = createSlice({
  name: 'fundamental',
  initialState,
  reducers: {
    setSymbol: (state, action) => {
      state.symbol = action.payload;
    },
    clearFundamentalAnalysis: (state) => {
      state.metrics = {};
      state.valuation = '';
      state.sectorComparison = {};
      state.status = 'idle';
      state.error = null;
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchFundamentalAnalysis.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(fetchFundamentalAnalysis.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.symbol = action.payload?.symbol ?? '';
        state.name = action.payload?.name ?? '';
        state.metrics = action.payload?.metrics ?? {};
        state.analysisDate = action.payload?.analysis_date ?? null;
        state.valuation = action.payload?.valuation ?? '';
        state.sectorComparison = action.payload?.sector_comparison ?? {};
      })
      .addCase(fetchFundamentalAnalysis.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload;
      });
  }
});

export const { setSymbol, clearFundamentalAnalysis } = fundamentalSlice.actions;

export default fundamentalSlice.reducer;
