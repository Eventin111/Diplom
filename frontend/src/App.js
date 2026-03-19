import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { useAuth } from './hooks/useAuth';
import SplashScreen from './components/SplashScreen/SplashScreen';
import LoginPage from './pages/LoginPage/LoginPage';
import RegisterPage from './pages/RegisterPage/RegisterPage';
import ForgotPasswordPage from './pages/ForgotPasswordPage/ForgotPasswordPage';
import FeedPage from './pages/FeedPage/FeedPage';
import ProfilePage from './pages/ProfilePage/ProfilePage';
import SearchPage from './pages/SearchPage/SearchPage';
import TryOnPage from './pages/TryOnPage/TryOnPage';
import WardrobePage from './pages/WardrobePage/WardrobePage';
import './styles/global.css';

function FeedSplashScreen({ isVisible, onFinish }) {
  if (!isVisible) return null;
  
  return (
    <div className="feed-splash-overlay">
      <SplashScreen 
        showImmediately={true}
        customText="Загрузка ленты"
        onFinish={onFinish}
      />
    </div>
  );
}

function AppContent() {
  const { isAuthenticated, loading } = useAuth();
  const location = useLocation();
  const [showInitialSplash, setShowInitialSplash] = useState(true);
  const [showFeedSplash, setShowFeedSplash] = useState(false);
  const [isInitialLoad, setIsInitialLoad] = useState(true);

  useEffect(() => {
    const savedTheme = localStorage.getItem('appTheme') || 'dark';
    const root = document.documentElement;
    root.classList.remove('theme-dark', 'theme-light');
    root.classList.add(`theme-${savedTheme}`);
    localStorage.setItem('appTheme', savedTheme);
  }, []);

  useEffect(() => {
    const hasSeenSplash = localStorage.getItem('hasSeenSplash');
    
    if (hasSeenSplash) {
      setShowInitialSplash(false);
    } else {
      const timer = setTimeout(() => {
        setShowInitialSplash(false);
        localStorage.setItem('hasSeenSplash', 'true');
      }, 2000);
      
      return () => clearTimeout(timer);
    }
  }, []);

  useEffect(() => {
    if (loading) return;
    
    if (isAuthenticated && location.pathname === '/') {
      if (isInitialLoad) {
        setShowFeedSplash(true);
        setIsInitialLoad(false);
        
        const timer = setTimeout(() => {
          setShowFeedSplash(false);
        }, 2000);
        
        return () => clearTimeout(timer);
      }
    }
  }, [isAuthenticated, location.pathname, loading, isInitialLoad]);

  if (loading || showInitialSplash) {
    return <SplashScreen showImmediately={true} />;
  }

  return (
    <div className="app-container">
      <Routes>
        <Route 
          path="/login" 
          element={
            !isAuthenticated ? <LoginPage /> : <Navigate to="/" replace />
          } 
        />
        
        <Route 
          path="/register" 
          element={
            !isAuthenticated ? <RegisterPage /> : <Navigate to="/" replace />
          } 
        />

        <Route 
          path="/forgot-password" 
          element={
            !isAuthenticated ? <ForgotPasswordPage /> : <Navigate to="/login" replace />
          } 
        />

        <Route 
          path="/" 
          element={
            <>
              {isAuthenticated ? <FeedPage /> : <Navigate to="/login" replace />}
              <FeedSplashScreen 
                isVisible={showFeedSplash}
                onFinish={() => setShowFeedSplash(false)}
              />
            </>
          } 
        />

        <Route 
          path="/profile" 
          element={
            isAuthenticated ? <ProfilePage /> : <Navigate to="/login" replace />
          } 
        />

        <Route 
          path="/search" 
          element={
            isAuthenticated ? <SearchPage /> : <Navigate to="/login" replace />
          } 
        />

        <Route 
          path="/try-on" 
          element={
            isAuthenticated ? <TryOnPage /> : <Navigate to="/login" replace />
          } 
        />

        <Route 
          path="/wardrobe" 
          element={
            isAuthenticated ? <WardrobePage /> : <Navigate to="/login" replace />
          } 
        />

        <Route path="*" element={<Navigate to={isAuthenticated ? "/" : "/login"} replace />} />
      </Routes>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}

export default App;
