import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { apiService } from '@services/api';
import type { AnalysisHistory } from '@types/index';

interface HistoryState {
    items: AnalysisHistory[];
    isLoading: boolean;
    error: string | null;
}

const initialState: HistoryState = {
    items: [],
    isLoading: false,
    error: null,
};

export const fetchHistory = createAsyncThunk(
    'history/fetchHistory',
    async (limit: number = 50) => {
        const data = await apiService.getHistory(limit);
        return data;
    }
);

const historySlice = createSlice({
    name: 'history',
    initialState,
    reducers: {
        clearHistory: (state) => {
            state.items = [];
        },
    },
    extraReducers: (builder) => {
        builder
            .addCase(fetchHistory.pending, (state) => {
                state.isLoading = true;
                state.error = null;
            })
            .addCase(fetchHistory.fulfilled, (state, action) => {
                state.isLoading = false;
                state.items = action.payload;
            })
            .addCase(fetchHistory.rejected, (state, action) => {
                state.isLoading = false;
                state.error = action.error.message || 'Failed to fetch history';
            });
    },
});

export const { clearHistory } = historySlice.actions;
export default historySlice.reducer;
