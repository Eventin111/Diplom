import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import './TryOnPage.css';

const TryOnPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAuth();
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState(null);

  const outfit = location.state?.outfit || {
    brand: 'Пример бренда',
    type: 'Одежда',
    price: '10,000 ₽'
  };

  const handleTryOn = () => {
    setIsProcessing(true);
    
    // Симуляция обработки примерки
    setTimeout(() => {
      setResult({
        success: true,
        image: 'https://images.unsplash.com/photo-1552374196-c4e7ffc6e126?w=400&h=600&fit=crop',
        message: 'Примерка успешно выполнена!'
      });
      setIsProcessing(false);
    }, 2000);
  };

  const handleSaveResult = () => {
    console.log('Saving result...');
    navigate('/');
  };

  const handleShare = () => {
    console.log('Sharing result...');
  };

  const handleCancel = () => {
    navigate('/');
  };

  return (
    <>
      <style>{`
        .tryon-container { min-height: 100vh; display: flex; flex-direction: column; padding: 14px; background: linear-gradient(179deg, rgba(5,5,13,1) 0%, rgba(15,16,30,1) 100%); color: #fff; font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; animation: fadeIn 0.3s ease-in-out; }
        .tryon-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
        .back-btn { background: rgba(255,255,255,0.12); color: #fff; border: 1px solid rgba(255,255,255,0.25); border-radius: 999px; padding: 8px 14px; cursor: pointer; font-weight: 600; transition: all 0.2s ease; }
        .back-btn:hover { background: rgba(255,255,255,0.2); transform: translateY(-1px); }
        .tryon-title { font-size: 22px; font-weight: 700; letter-spacing: 0.2px; }
        .tryon-content { display: grid; gap: 12px; flex: 1; overflow-y: auto; padding-right: 4px; }
        .outfit-info-card { border: 1px solid rgba(255,255,255,0.18); background: rgba(48,51,78,0.8); border-radius: 16px; padding: 12px; }
        .outfit-info-card h3 { font-size: 16px; font-weight: 700; margin-bottom: 8px; }
        .outfit-details { display: grid; grid-template-columns: repeat(3,minmax(0,1fr)); gap: 8px; }
        .outfit-detail { background: rgba(255,255,255,0.05); border-radius: 10px; padding: 8px; }
        .detail-label { font-size: 11px; opacity: 0.8; }
        .detail-value { font-size: 13px; font-weight: 600; }
        .preview-area { border: 1px solid rgba(255,255,255,0.14); border-radius: 16px; min-height: 220px; background: rgba(15,16,30,0.65); display: flex; align-items: center; justify-content: center; padding: 14px; }
        .instruction-step { display: flex; align-items: flex-start; gap: 10px; margin-bottom: 10px; }
        .step-number { width: 24px; height: 24px; display: inline-flex; align-items: center; justify-content: center; background: #6f8fff; border-radius: 50%; color: #fff; font-weight: 700; }
        .result-image { width: 100%; max-height: 300px; object-fit: cover; border-radius: 14px; border: 1px solid rgba(255,255,255,0.2); box-shadow:0 4px 20px rgba(0,0,0,0.5); margin-bottom: 10px; }
        .action-buttons { display: flex; gap: 8px; flex-wrap: wrap; justify-content: space-between; }
        .action-btn { flex: 1 1 30%; min-width: 98px; display:flex; align-items:center; justify-content:center; gap:8px; padding:10px 12px; border-radius:12px; border:1px solid rgba(255,255,255,0.2); background: rgba(34,39,72,0.75); color:#fff; font-weight:600; cursor:pointer; }
        .action-btn:hover { transform: translateY(-1px); box-shadow: 0 10px 18px rgba(41,201,255,0.18); }
        .action-btn.primary { background: linear-gradient(120deg,#4e71f2,#6f8fff); border-color: rgba(111,143,255,0.9); }
        .user-tryon-info { display:flex; align-items:center; gap:10px; background: rgba(255,255,255,0.06); border:1px solid rgba(255,255,255,0.16); border-radius:14px; padding:10px; }
        .user-avatar { width:44px;height:44px;border-radius:50%;object-fit:cover;border:1px solid rgba(255,255,255,0.28); min-height:44px; }
        .tryon-hint { margin-top:10px; background: rgba(25,30,55,0.7); border:1px solid rgba(111,143,255,0.2); padding:10px; border-radius:12px; font-size:13px; color:#d4e8ff; }
        @keyframes fadeIn { from { opacity:0; } to { opacity:1; } }
        @media (max-width: 540px) { .outfit-details { grid-template-columns: 1fr; } .action-buttons { flex-direction: column; } .action-btn { width: 100%; } }
      `}</style>
      <div className="tryon-container">
      {/* Шапка */}
      <header className="tryon-header">
        <button className="back-btn" onClick={handleCancel}>
          ← Отмена
        </button>
        <h1 className="tryon-title">Виртуальная примерка</h1>
        <div></div> {/* Пустой элемент для выравнивания */}
      </header>

      <div className="tryon-content">
        {/* Информация об одежде */}
        <div className="outfit-info-card">
          <h3>Примеряемая одежда:</h3>
          <div className="outfit-details">
            <div className="outfit-detail">
              <span className="detail-label">Бренд:</span>
              <span className="detail-value">{outfit.brand}</span>
            </div>
            <div className="outfit-detail">
              <span className="detail-label">Тип:</span>
              <span className="detail-value">{outfit.type}</span>
            </div>
            <div className="outfit-detail">
              <span className="detail-label">Цена:</span>
              <span className="detail-value">{outfit.price}</span>
            </div>
          </div>
        </div>

        {/* Область предпросмотра */}
        <div className="preview-area">
          {isProcessing ? (
            <div className="processing">
              <div className="spinner"></div>
              <p>Идет примерка...</p>
            </div>
          ) : result ? (
            <div className="result">
              <img src={result.image} alt="Результат примерки" className="result-image" />
              <p className="result-message">{result.message}</p>
              <div className="result-actions">
                <button className="save-btn" onClick={handleSaveResult}>
                  Сохранить
                </button>
                <button className="share-btn" onClick={handleShare}>
                  Поделиться
                </button>
              </div>
            </div>
          ) : (
            <div className="instructions">
              <div className="instruction-step">
                <span className="step-number">1</span>
                <p>Сделайте фото или выберите из галереи</p>
              </div>
              <div className="instruction-step">
                <span className="step-number">2</span>
                <p>Система автоматически примерит одежду</p>
              </div>
              <div className="instruction-step">
                <span className="step-number">3</span>
                <p>Оцените результат и поделитесь с друзьями</p>
              </div>
            </div>
          )}
        </div>

        {/* Кнопки действий */}
        <div className="action-buttons">
          {!result && (
            <>
              <button className="action-btn secondary">
                <span className="btn-icon">📁</span>
                <span>Выбрать фото</span>
              </button>
              <button className="action-btn primary" onClick={handleTryOn}>
                <span className="btn-icon">🎬</span>
                <span>Сделать фото</span>
              </button>
              <button className="action-btn secondary">
                <span className="btn-icon">📸</span>
                <span>Из галереи</span>
              </button>
            </>
          )}
        </div>

        {/* Информация о пользователе */}
        <div className="user-tryon-info">
          <img src={user?.avatar} alt="Аватар" className="user-avatar" />
          <div className="user-info">
            <h4>{user?.username || 'Пользователь'}</h4>
            <p>Готов примерить {outfit.type.toLowerCase()}!</p>
          </div>
        </div>
      </div>

      {/* Подсказка */}
      <div className="tryon-hint">
        💡 Совет: Используйте хорошее освещение для лучшего результата
      </div>
    </div>
    </>
  );
};

export default TryOnPage;