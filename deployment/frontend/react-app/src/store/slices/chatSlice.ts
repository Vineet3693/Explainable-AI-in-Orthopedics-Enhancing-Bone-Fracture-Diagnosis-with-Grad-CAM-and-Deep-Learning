import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { apiService } from '@services/api';
import type { QAMessage } from '@types/index';

interface ChatState {
    messages: QAMessage[];
    isLoading: boolean;
    error: string | null;
}

const initialState: ChatState = {
    messages: [],
    isLoading: false,
    error: null,
};

export const sendMessage = createAsyncThunk(
    'chat/sendMessage',
    async ({ question, context }: { question: string; context?: string }) => {
        const response = await apiService.askQuestion(question, context);
        return response;
    }
);

const chatSlice = createSlice({
    name: 'chat',
    initialState,
    reducers: {
        addUserMessage: (state, action: PayloadAction<string>) => {
            state.messages.push({
                id: Date.now().toString(),
                role: 'user',
                content: action.payload,
                timestamp: new Date().toISOString(),
            });
        },
        clearChat: (state) => {
            state.messages = [];
        },
    },
    extraReducers: (builder) => {
        builder
            .addCase(sendMessage.pending, (state) => {
                state.isLoading = true;
                state.error = null;
            })
            .addCase(sendMessage.fulfilled, (state, action) => {
                state.isLoading = false;
                state.messages.push(action.payload);
            })
            .addCase(sendMessage.rejected, (state, action) => {
                state.isLoading = false;
                state.error = action.error.message || 'Failed to send message';
            });
    },
});

export const { addUserMessage, clearChat } = chatSlice.actions;
export default chatSlice.reducer;
