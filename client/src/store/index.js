import { configureStore } from '@reduxjs/toolkit';
import recommendationsReducer from './slices/recommendationsSlice';
import technicalReducer from './slices/technicalSlice';
import fundamentalReducer from './slices/fundamentalSlice';
import marketReducer from './slices/marketSlice';
import financialReducer from './slices/financialSlice';
import sentimentReducer from './slices/sentimentSlice';
import uiReducer from './slices/uiSlice';

export const store = configureStore({
  reducer: {
    recommendations: recommendationsReducer,
    technical: technicalReducer,
    fundamental: fundamentalReducer,
    market: marketReducer,
    financial: financialReducer,
    sentiment: sentimentReducer,
    ui: uiReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false,
    }),
});