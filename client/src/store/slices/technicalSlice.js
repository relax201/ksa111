import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

// Async thunk for fetching technical analysis
export const fetchTechnicalAnalysis = createAsyncThunk(
  'technical/fetchTechnicalAnalysis',
  async (params, { rejectWithValue }) => {
    try {
      const symbol = (params?.symbol ?? '2222.SR').replace('.SR', '');
      const indicators = params?.indicators ?? ['SMA', 'RSI', 'MACD'];
      const timeframe = params?.timeframe ?? 'daily';

      const response = await axios.post(
        '/api/v1/integration/technical-analysis',
        { symbol: `${symbol}.SR`, indicators, timeframe },
        { timeout: 20000 }
      );

      return response.data?.data ?? response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to fetch technical analysis');
    }
  }
);

const initialState = {
  symbol: '',
  name: '',
  timeframe: 'daily',
  indicators: {},
  analysisDate: null,
  trend: '',
  supportLevels: [],
  resistanceLevels: [],
  status: 'idle', // 'idle' | 'loading' | 'succeeded' | 'failed'
  error: null
};

const technicalSlice = createSlice({
  name: 'technical',
  initialState,
  reducers: {
    setSymbol: (state, action) => {
      state.symbol = action.payload;
    },
    setTimeframe: (state, action) => {
      state.timeframe = action.payload;
    },
    clearTechnicalAnalysis: (state) => {
      state.indicators = {};
      state.trend = '';
      state.supportLevels = [];
      state.resistanceLevels = [];
      state.status = 'idle';
      state.error = null;
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchTechnicalAnalysis.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(fetchTechnicalAnalysis.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.symbol = action.payload?.symbol ?? '';
        state.name = action.payload?.name ?? '';
        state.timeframe = action.payload?.timeframe ?? 'daily';
        state.indicators = action.payload?.indicators ?? {};
        state.analysisDate = action.payload?.analysis_date ?? null;
        state.trend = action.payload?.trend ?? '';
        state.supportLevels = action.payload?.support_levels ?? [];
        state.resistanceLevels = action.payload?.resistance_levels ?? [];
      })
      .addCase(fetchTechnicalAnalysis.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload;
      });
  }
});

export const { setSymbol, setTimeframe, clearTechnicalAnalysis } = technicalSlice.actions;

export default technicalSlice.reducer;
