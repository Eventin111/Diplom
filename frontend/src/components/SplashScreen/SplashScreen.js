import React, { useEffect, useState } from 'react';
import './SplashScreen.css';

const SplashScreen = ({ 
  onFinish, 
  showImmediately = false, 
  customText = null 
}) => {
  const [isVisible, setIsVisible] = useState(true);
  const [isLoading, setIsLoading] = useState(true);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    // Анимация прогресс-бара
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          return 100;
        }
        return prev + 4;
      });
    }, 50);

    // Завершение загрузки
    const timer = setTimeout(() => {
      setIsLoading(false);
      clearInterval(interval);
      setProgress(100);
      
      // Небольшая пауза перед исчезновением
      setTimeout(() => {
        setIsVisible(false);
        
        // Пауза перед вызовом onFinish для анимации
        setTimeout(() => {
          if (onFinish) onFinish();
        }, 300);
      }, 300);
    }, 2000);

    return () => {
      clearInterval(interval);
      clearTimeout(timer);
    };
  }, [onFinish]);

  return (
    <div className={`splash-screen ${isVisible ? 'visible' : 'hidden'}`}>
      <div className="splash-content">
        {/* Анимированный логотип */}
        <div className="logo-container">
          <span 
            className={`logo-letter ${showImmediately ? 'immediate' : ''}`} 
            style={{ animationDelay: showImmediately ? '0s' : '0s' }}
          >
            S
          </span>
          <span 
            className={`logo-letter ${showImmediately ? 'immediate' : ''}`} 
            style={{ animationDelay: showImmediately ? '0s' : '0.1s' }}
          >
            w
          </span>
          <span 
            className={`logo-letter ${showImmediately ? 'immediate' : ''}`} 
            style={{ animationDelay: showImmediately ? '0s' : '0.2s' }}
          >
            i
          </span>
          <span 
            className={`logo-letter ${showImmediately ? 'immediate' : ''}`} 
            style={{ animationDelay: showImmediately ? '0s' : '0.3s' }}
          >
            p
          </span>
          <span 
            className={`logo-letter ${showImmediately ? 'immediate' : ''}`} 
            style={{ animationDelay: showImmediately ? '0s' : '0.4s' }}
          >
            e
          </span>
          <span 
            className={`logo-letter ${showImmediately ? 'immediate' : ''}`} 
            style={{ animationDelay: showImmediately ? '0s' : '0.5s' }}
          >
            l
          </span>
          <span 
            className={`logo-letter ${showImmediately ? 'immediate' : ''}`} 
            style={{ animationDelay: showImmediately ? '0s' : '0.6s' }}
          >
            t
          </span>
        </div>
        
        <div className="splash-subtitle">
          {customText || 'Виртуальная примерка одежды'}
        </div>
        
        {/* Прогресс-бар */}
        <div className="progress-container">
          <div 
            className="progress-bar" 
            style={{ width: `${progress}%` }}
          />
        </div>
        
        {/* Загрузочный текст */}
        <div className={`loading-text ${!isLoading ? 'fade-out' : ''}`}>
          {isLoading ? 'Загрузка...' : 'Готово!'}
        </div>
      </div>
    </div>
  );
};

export default SplashScreen;