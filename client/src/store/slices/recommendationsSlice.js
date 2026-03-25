import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

// Async thunk for fetching recommendations
export const fetchRecommendations = createAsyncThunk(
  'recommendations/fetchRecommendations',
  async (params, { rejectWithValue }) => {
    try {
      const response = await axios.post(
        '/api/v1/integration/recommendations',
        {
          risk_profile:        params?.riskProfile        ?? 'moderate',
          investment_horizon:  params?.investmentHorizon  ?? 'medium',
          sectors:             params?.sectors            ?? [],
          exclude_symbols:     params?.excludeSymbols     ?? [],
          max_results:         params?.maxResults         ?? 10,
        },
        { timeout: 30000 }
      );

      const payload = response.data?.data ?? response.data ?? {};
      return {
        recommendations:    payload.recommendations    ?? [],
        risk_profile:       payload.risk_profile       ?? params?.riskProfile ?? 'moderate',
        investment_horizon: payload.investment_horizon ?? params?.investmentHorizon ?? 'medium',
        analysis_date:      payload.analysis_date      ?? null,
      };
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to fetch recommendations');
    }
  }
);

const initialState = {
  recommendations: [],
  riskProfile: 'moderate',
  investmentHorizon: 'medium',
  analysisDate: null,
  status: 'idle', // 'idle' | 'loading' | 'succeeded' | 'failed'
  error: null
};

const recommendationsSlice = createSlice({
  name: 'recommendations',
  initialState,
  reducers: {
    setRiskProfile: (state, action) => {
      state.riskProfile = action.payload;
    },
    setInvestmentHorizon: (state, action) => {
      state.investmentHorizon = action.payload;
    },
    clearRecommendations: (state) => {
      state.recommendations = [];
      state.status = 'idle';
      state.error = null;
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchRecommendations.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(fetchRecommendations.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.recommendations = action.payload?.recommendations ?? [];
        state.riskProfile = action.payload?.risk_profile ?? state.riskProfile;
        state.investmentHorizon = action.payload?.investment_horizon ?? state.investmentHorizon;
        state.analysisDate = action.payload?.analysis_date ?? null;
      })
      .addCase(fetchRecommendations.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload;
      });
  }
});

export const { setRiskProfile, setInvestmentHorizon, clearRecommendations } = recommendationsSlice.actions;

export default recommendationsSlice.reducer;
