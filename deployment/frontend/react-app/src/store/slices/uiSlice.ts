import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface UIState {
    sidebarOpen: boolean;
    theme: 'light' | 'dark';
    notifications: Array<{
        id: string;
        message: string;
        severity: 'success' | 'error' | 'warning' | 'info';
    }>;
}

const initialState: UIState = {
    sidebarOpen: true,
    theme: 'light',
    notifications: [],
};

const uiSlice = createSlice({
    name: 'ui',
    initialState,
    reducers: {
        toggleSidebar: (state) => {
            state.sidebarOpen = !state.sidebarOpen;
        },
        setSidebarOpen: (state, action: PayloadAction<boolean>) => {
            state.sidebarOpen = action.payload;
        },
        toggleTheme: (state) => {
            state.theme = state.theme === 'light' ? 'dark' : 'light';
        },
        addNotification: (state, action: PayloadAction<Omit<UIState['notifications'][0], 'id'>>) => {
            state.notifications.push({
                ...action.payload,
                id: Date.now().toString(),
            });
        },
        removeNotification: (state, action: PayloadAction<string>) => {
            state.notifications = state.notifications.filter((n) => n.id !== action.payload);
        },
    },
});

export const {
    toggleSidebar,
    setSidebarOpen,
    toggleTheme,
    addNotification,
    removeNotification,
} = uiSlice.actions;

export default uiSlice.reducer;
