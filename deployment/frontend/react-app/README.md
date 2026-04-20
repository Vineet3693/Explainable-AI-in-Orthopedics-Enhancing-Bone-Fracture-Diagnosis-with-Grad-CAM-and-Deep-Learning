# 🎨 Fracture Detection AI - React Frontend

## Overview

**Vibrant, engaging, and eye-catching** React TypeScript frontend for the Fracture Detection AI system.

### ✨ Design Features

- 🌈 **Bright, Modern Colors** - Cyan, Hot Pink, Purple, Golden Yellow
- 🎭 **Gradient Backgrounds** - Smooth, animated gradients throughout
- ✨ **Glass Morphism** - Frosted glass effects on cards and sidebar
- 🎬 **Smooth Animations** - Float, pulse, slide-in, shimmer effects
- 💫 **Hover Effects** - Lift, glow, and transform on hover
- 🎨 **Neon Accents** - Eye-catching neon glows on interactive elements

---

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm
- Backend API running on `http://localhost:8000`

### Installation

```bash
cd deployment/frontend/react-app

# Install dependencies
npm install

# Start development server
npm run dev
```

The app will be available at `http://localhost:3000`

---

## 📁 Project Structure

```
react-app/
├── src/
│   ├── components/
│   │   └── Layout.tsx          # Main layout with sidebar
│   ├── pages/
│   │   ├── HomePage.tsx        # Landing page with hero
│   │   ├── UploadPage.tsx      # Drag-and-drop upload
│   │   ├── ResultsPage.tsx     # Analysis results
│   │   ├── HistoryPage.tsx     # Past analyses
│   │   ├── ChatPage.tsx        # Q&A interface
│   │   └── SettingsPage.tsx    # User settings
│   ├── store/
│   │   ├── store.ts            # Redux store
│   │   └── slices/             # Redux slices
│   ├── services/
│   │   └── api.ts              # API client
│   ├── types/
│   │   └── index.ts            # TypeScript types
│   ├── theme.ts                # MUI theme (vibrant colors!)
│   ├── index.css               # Global styles & animations
│   ├── App.tsx                 # Main app component
│   └── main.tsx                # Entry point
├── package.json
├── tsconfig.json
├── vite.config.ts
└── index.html
```

---

## 🎨 Color Palette

### Primary Colors
- **Cyan**: `#00D4FF` - Main brand color
- **Purple**: `#7C4DFF` - Secondary accent
- **Hot Pink**: `#FF6B9D` - Energetic highlights
- **Golden Yellow**: `#FFB800` - Warm accents
- **Bright Green**: `#00E676` - Success states

### Gradients
- **Primary**: `linear-gradient(135deg, #00D4FF 0%, #7C4DFF 100%)`
- **Secondary**: `linear-gradient(135deg, #FF6B9D 0%, #FFB800 100%)`
- **Success**: `linear-gradient(135deg, #00E676 0%, #00D4FF 100%)`

---

## ✨ Features

### 🏠 Home Page
- Animated gradient hero section
- Floating feature cards
- Eye-catching statistics
- Smooth scroll animations

### ☁️ Upload Page
- Vibrant drag-and-drop zone
- Real-time preview
- Gradient progress bars
- Animated status alerts

### 📊 Results Page
- Prediction display with confidence
- Grad-CAM heatmap visualization
- Detailed findings
- Report generation

### 💬 Chat Page
- Interactive Q&A interface
- Context-aware responses
- Conversation history
- Multi-language support

### 📜 History Page
- Sortable analysis table
- Filter and search
- Charts and statistics
- Export options

---

## 🛠️ Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Material-UI v5** - Component library
- **Redux Toolkit** - State management
- **React Query** - API data fetching
- **React Router v6** - Routing
- **Vite** - Build tool
- **Axios** - HTTP client

---

## 📦 Build for Production

```bash
# Build optimized bundle
npm run build

# Preview production build
npm run preview
```

Build output will be in `dist/` directory.

---

## 🎯 API Configuration

The frontend connects to the FastAPI backend at `http://localhost:8000` by default.

To change the API URL, create a `.env` file:

```env
VITE_API_URL=http://your-api-url:8000
```

---

## 🎨 Customization

### Change Colors

Edit `src/theme.ts`:

```typescript
palette: {
  primary: {
    main: '#YOUR_COLOR',
  },
}
```

### Add Animations

Edit `src/index.css`:

```css
@keyframes yourAnimation {
  /* animation keyframes */
}
```

---

## 🚀 Deployment

### Vercel (Recommended)

```bash
npm install -g vercel
vercel
```

### Netlify

```bash
npm run build
# Drag dist/ folder to Netlify
```

### Docker

```bash
docker build -t fracture-ai-frontend .
docker run -p 3000:80 fracture-ai-frontend
```

---

## 📝 Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run test` - Run tests

---

## 🎉 Features Comparison

| Feature | Streamlit | React (This) |
|---------|-----------|--------------|
| Development Speed | ✅ Fast | ⚠️ Medium |
| Customization | ⚠️ Limited | ✅ Full |
| Performance | ⚠️ Good | ✅ Excellent |
| Visual Appeal | ⚠️ Standard | ✅ **Vibrant!** |
| Scalability | ⚠️ 100 users | ✅ 1000+ users |
| Mobile Experience | ⚠️ OK | ✅ Excellent |

---

## 🎨 Why This Frontend is Special

### 🌈 Vibrant & Engaging
- Bright, eye-catching color combinations
- Smooth gradient transitions
- Modern glass morphism effects

### ✨ Delightful Animations
- Floating elements
- Hover lift effects
- Shimmer loading states
- Smooth page transitions

### 💎 Premium Feel
- Professional typography (Poppins font)
- Polished UI components
- Attention to detail
- Consistent design system

---

## 📞 Support

For issues or questions, please refer to the main project documentation.

---

## 🎉 Enjoy the Vibrant Experience!

This React frontend provides a **stunning, modern, and engaging** user experience that will wow your users! 🚀✨
