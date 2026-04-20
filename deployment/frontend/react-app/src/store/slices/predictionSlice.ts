import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { apiService } from '@services/api';
import type { PredictionResult, UploadProgress } from '@types/index';

interface PredictionState {
    currentFile: File | null;
    currentResult: PredictionResult | null;
    uploadProgress: UploadProgress;
    isLoading: boolean;
    error: string | null;
}

const initialState: PredictionState = {
    currentFile: null,
    currentResult: null,
    uploadProgress: {
        progress: 0,
        status: 'idle',
    },
    isLoading: false,
    error: null,
};

// Async thunks
export const uploadAndPredict = createAsyncThunk(
    'prediction/uploadImage',
    async (file: File, { rejectWithValue }) => {
        try {
            // Predict directly (no validation endpoint in backend)
            const result = await apiService.predictImage(file);
            return result;
        } catch (error: any) {
            return rejectWithValue(error.response?.data?.detail || error.message || 'Prediction failed');
        }
    }
);

const predictionSlice = createSlice({
    name: 'prediction',
    initialState,
    reducers: {
        setCurrentFile: (state, action: PayloadAction<File | null>) => {
            state.currentFile = action.payload;
        },
        clearPrediction: (state) => {
            state.currentFile = null;
            state.currentResult = null;
            state.uploadProgress = initialState.uploadProgress;
            state.error = null;
        },
        setUploadProgress: (state, action: PayloadAction<number>) => {
            state.uploadProgress.progress = action.payload;
        },
    },
    extraReducers: (builder) => {
        builder
            .addCase(uploadAndPredict.pending, (state) => {
                state.isLoading = true;
                state.error = null;
                state.uploadProgress.status = 'uploading';
            })
            .addCase(uploadAndPredict.fulfilled, (state, action) => {
                state.isLoading = false;
                state.currentResult = action.payload;
                state.uploadProgress.status = 'complete';
                state.uploadProgress.progress = 100;
            })
            .addCase(uploadAndPredict.rejected, (state, action) => {
                state.isLoading = false;
                state.error = action.payload as string;
                state.uploadProgress.status = 'error';
            });
    },
});

export const { setCurrentFile, clearPrediction, setUploadProgress } = predictionSlice.actions;
export default predictionSlice.reducer;
