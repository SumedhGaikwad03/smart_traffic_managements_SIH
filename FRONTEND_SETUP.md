# Frontend Setup & Running Guide

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Setup Environment Variables
Make sure `.env` file exists with:
```env
REACT_APP_MAPBOX_TOKEN=your_token_here
REACT_APP_API_URL=http://localhost:5000
```

### 3. Run Development Server
```bash
npm start
```

Server will open at `http://localhost:3000`

---

## 📋 Recommended Code Improvements

### Issue #1: Missing Error Boundary
**Status:** Not implemented  
**Priority:** HIGH  
**Solution:** Add error boundary to handle component crashes

### Issue #2: Mapbox Token Fallback
**Status:** Needs fallback  
**Priority:** MEDIUM  
**Solution:** Use OpenStreetMap/Leaflet as fallback when Mapbox token unavailable

### Issue #3: Settings Persistence
**Status:** Not implemented  
**Priority:** MEDIUM  
**Solution:** Save control panel settings to localStorage

### Issue #4: Improved API Error Handling
**Status:** Basic implementation  
**Priority:** MEDIUM  
**Solution:** Add retry logic and better error messages

### Issue #5: Component Code Splitting
**Status:** Not implemented  
**Priority:** LOW  
**Solution:** Use React.lazy() for MetricsDashboard for better performance

---

## 🛠️ Tech Stack
- **React 19.1** - UI Framework
- **TypeScript 4.9** - Type Safety
- **Tailwind CSS 3.3** - Styling
- **Mapbox GL 3.14** - Map visualization
- **Recharts 3.2** - Charts & Graphs
- **Axios 1.11** - HTTP Client
- **React Query 5.87** - Data Fetching & Caching
- **Framer Motion 12.23** - Animations
- **Heroicons 2.2** - Icons

---

## 📱 Key Features
✅ Real-time traffic monitoring
✅ Interactive map with traffic signals
✅ Live metrics dashboard
✅ Traffic optimization controls
✅ Data export functionality
✅ Multiple optimization strategies
✅ Responsive design
✅ Dark mode support

---

## 🔧 Available Scripts

- `npm start` - Run development server
- `npm build` - Build for production
- `npm test` - Run tests
- `npm eject` - Eject from Create React App (irreversible)

---

## 📦 Deployment Notes

For production build:
```bash
npm run build
```

This creates optimized build in `build/` folder.

Make sure to set proper environment variables:
- `REACT_APP_API_URL` - Production backend URL
- `REACT_APP_MAPBOX_TOKEN` - Valid Mapbox token

