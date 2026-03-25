import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

// Async thunk for fetching sentiment analysis
export const fetchSentimentAnalysis = createAsyncThunk(
  'sentiment/fetchSentimentAnalysis',
  async (params, { rejectWithValue }) => {
    try {
      const symbol = (params.symbols?.[0] ?? '2222.SR').replace('.SR', '');
      const response = await axios.get(`/api/v1/stocks/${encodeURIComponent(symbol)}/sentiment`, {
        timeout: 20000,
      });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to fetch sentiment analysis');
    }
  }
);

const initialState = {
  symbols: [],
  sentiment: {},
  analysisDate: null,
  status: 'idle', // 'idle' | 'loading' | 'succeeded' | 'failed'
  error: null
};

const sentimentSlice = createSlice({
  name: 'sentiment',
  initialState,
  reducers: {
    setSymbols: (state, action) => {
      state.symbols = action.payload;
    },
    clearSentimentAnalysis: (state) => {
      state.sentiment = {};
      state.status = 'idle';
      state.error = null;
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchSentimentAnalysis.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(fetchSentimentAnalysis.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.symbols = action.payload?.symbols ?? [];
        state.sentiment = action.payload?.sentiment ?? {};
        state.analysisDate = action.payload?.analysis_date ?? null;
      })
      .addCase(fetchSentimentAnalysis.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload;
      });
  }
});

export const { setSymbols, clearSentimentAnalysis } = sentimentSlice.actions;

export default sentimentSlice.reducer;