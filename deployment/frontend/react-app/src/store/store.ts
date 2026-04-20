import { configureStore } from '@reduxjs/toolkit';
import { TypedUseSelectorHook, useDispatch, useSelector } from 'react-redux';

// Import slices (will create these next)
import predictionReducer from './slices/predictionSlice';
import historyReducer from './slices/historySlice';
import chatReducer from './slices/chatSlice';
import uiReducer from './slices/uiSlice';

export const store = configureStore({
    reducer: {
        prediction: predictionReducer,
        history: historyReducer,
        chat: chatReducer,
        ui: uiReducer,
    },
    middleware: (getDefaultMiddleware) =>
        getDefaultMiddleware({
            serializableCheck: {
                // Ignore these action types
                ignoredActions: ['prediction/uploadImage/pending'],
                // Ignore these field paths in all actions
                ignoredActionPaths: ['payload.file'],
                // Ignore these paths in the state
                ignoredPaths: ['prediction.currentFile'],
            },
        }),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

// Typed hooks
export const useAppDispatch: () => AppDispatch = useDispatch;
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;
