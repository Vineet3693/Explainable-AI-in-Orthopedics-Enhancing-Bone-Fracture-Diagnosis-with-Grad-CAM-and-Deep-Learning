# 🚀 Running the Frontend - Quick Start

## Current Status

You have a **React + TypeScript + Material-UI** frontend already set up in:
```
deployment/frontend/react-app/
```

## Quick Start (3 Steps)

### Step 1: Navigate to Frontend Directory
```bash
cd "d:\Coding Workspace\fracture detection ai\deployment\frontend\react-app"
```

### Step 2: Install Dependencies (if needed)
```bash
npm install
```

### Step 3: Start Development Server
```bash
npm run dev
```

The frontend will open at: **http://localhost:5173**

---

## What's Already Installed

✅ React 18
✅ TypeScript
✅ Material-UI (MUI)
✅ React Router
✅ Redux Toolkit
✅ React Query
✅ Axios (for API calls)
✅ React Hook Form
✅ Recharts (for metrics visualization)
✅ React Dropzone (for file upload)
✅ Vite (fast build tool)

---

## Project Structure

```
react-app/
├── src/
│   ├── App.tsx              # Main app component
│   ├── main.tsx             # Entry point
│   ├── index.css            # Global styles
│   ├── theme.ts             # MUI theme configuration
│   ├── components/          # Reusable components
│   ├── pages/               # Page components
│   ├── services/            # API services
│   ├── store/               # Redux store
│   └── types/               # TypeScript types
├── package.json
└── vite.config.ts
```

---

## API Configuration

The frontend needs to connect to your backend API.

### Update API URL

Edit `src/services/api.ts` (or create if missing):

```typescript
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const predictFracture = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post('/api/v1/predict', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};
```

---

## Matching the UI Prototype

The UI prototype shows:
- **Left Panel (40%)**: Upload area
- **Right Panel (60%)**: Results display
- **Purple gradient background**
- **Modern medical UI**

### To Update the UI:

1. **Check existing pages:**
   ```bash
   # List pages
   dir src\pages
   ```

2. **Update the main upload page** to match the prototype design

3. **Use Material-UI components** for consistency

---

## Available Scripts

```bash
# Development server (with hot reload)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linter
npm run lint

# Run tests
npm run test
```

---

## Troubleshooting

### Port Already in Use
If port 5173 is busy:
```bash
# Vite will automatically try the next port (5174, 5175, etc.)
```

### Dependencies Not Installed
```bash
npm install
```

### Build Errors
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

---

## Next Steps

1. **Start the frontend:**
   ```bash
   cd deployment/frontend/react-app
   npm run dev
   ```

2. **Ensure backend is running:**
   ```bash
   # In another terminal
   cd "d:\Coding Workspace\fracture detection ai"
   py app_simple.py
   ```

3. **Test the complete flow:**
   - Upload X-ray → Get prediction → View results

---

## Production Build

When ready to deploy:

```bash
# Build optimized production bundle
npm run build

# Output will be in: dist/
# Deploy the dist/ folder to your hosting service
```

---

**The frontend is ready to run! Just navigate to the folder and run `npm run dev`** 🚀
