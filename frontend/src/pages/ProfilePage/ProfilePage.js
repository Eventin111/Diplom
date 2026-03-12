import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import WardrobePage from '../WardrobePage/WardrobePage';
import './ProfilePage.css';

const ProfilePage = () => {
  const navigate = useNavigate();
  const { user, logout, isAuthenticated } = useAuth();

  const isGuest = user?.isGuest;
  const [activeView, setActiveView] = useState('profile');
  
  const [tryOnPhotos, setTryOnPhotos] = useState(() => {
    const savedPhotos = localStorage.getItem('tryOnPhotos');
    return savedPhotos ? JSON.parse(savedPhotos) : [];
  });
  const [primaryPhotoIndex, setPrimaryPhotoIndex] = useState(() => {
    const savedIndex = localStorage.getItem('primaryPhotoIndex');
    return savedIndex ? parseInt(savedIndex) : 0;
  });
  const fileInputRef = useRef(null);

  if (!isAuthenticated) {
    navigate('/login');
    return null;
  }

  const userStats = [
    { label: 'Примерок', value: '24' },
    { label: 'Лайков', value: '156' },
    { label: 'Постов', value: '8' },
    { label: 'Подписчиков', value: '89' }
  ];

  const recentOutfits = [
    { id: 1, name: 'Вечерний образ', image: 'https://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=300&h=400&fit=crop' },
    { id: 2, name: 'Спортивный стиль', image: 'https://images.unsplash.com/photo-1523381210434-271e8be1f52b?w=300&h=400&fit=crop' },
    { id: 3, name: 'Деловой костюм', image: 'https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=300&h=400&fit=crop' }
  ];

  const handleUpgradeToUser = () => {
    logout();
    setTimeout(() => {
      window.location.href = '/register';
    }, 100);
  };

  const handleLogin = () => {
    logout();
    setTimeout(() => {
      window.location.href = '/login';
    }, 100);
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handlePhotoUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      const newPhoto = {
        id: Date.now(),
        url: event.target.result,
        name: file.name,
        date: new Date().toLocaleDateString()
      };

      const updatedPhotos = [...tryOnPhotos, newPhoto];
      setTryOnPhotos(updatedPhotos);
      localStorage.setItem('tryOnPhotos', JSON.stringify(updatedPhotos));
      
      if (updatedPhotos.length === 1) {
        setPrimaryPhotoIndex(0);
        localStorage.setItem('primaryPhotoIndex', '0');
      }
    };
    reader.readAsDataURL(file);
    e.target.value = '';
  };

  const handleDeletePhoto = (index, e) => {
    e.stopPropagation();
    const updatedPhotos = tryOnPhotos.filter((_, i) => i !== index);
    setTryOnPhotos(updatedPhotos);
    localStorage.setItem('tryOnPhotos', JSON.stringify(updatedPhotos));
    
    if (primaryPhotoIndex >= updatedPhotos.length) {
      const newIndex = updatedPhotos.length > 0 ? updatedPhotos.length - 1 : 0;
      setPrimaryPhotoIndex(newIndex);
      localStorage.setItem('primaryPhotoIndex', newIndex.toString());
    } else if (index < primaryPhotoIndex) {
      setPrimaryPhotoIndex(primaryPhotoIndex - 1);
      localStorage.setItem('primaryPhotoIndex', (primaryPhotoIndex - 1).toString());
    }
  };

  const handleSetPrimary = (index, e) => {
    if (e) e.stopPropagation();
    setPrimaryPhotoIndex(index);
    localStorage.setItem('primaryPhotoIndex', index.toString());
  };

  const triggerFileInput = () => {
    fileInputRef.current.click();
  };

  useEffect(() => {
    if (!document.documentElement.style.getPropertyValue('--bg-primary')) {
      document.documentElement.style.setProperty('--bg-primary', '#0a0a0a');
      document.documentElement.style.setProperty('--bg-secondary', '#1a1a1a');
      document.documentElement.style.setProperty('--bg-tertiary', '#2a2a2a');
      document.documentElement.style.setProperty('--card-bg', 'rgba(255, 255, 255, 0.05)');
      document.documentElement.style.setProperty('--text-primary', '#ffffff');
      document.documentElement.style.setProperty('--text-secondary', '#aaaaaa');
      document.documentElement.style.setProperty('--border-color', 'rgba(255, 255, 255, 0.1)');
      document.documentElement.style.setProperty('--accent-color', '#ff0000');
    }
  }, []);

  if (activeView === 'wardrobe') {
    return (
      <div className="profile-container">
        <header className="profile-header">
          <button className="back-btn" onClick={() => setActiveView('profile')}>
            ← Профиль
          </button>
          <h1 className="profile-title">Мой гардероб</h1>
          <div style={{ width: '70px' }}></div>
        </header>

        <div className="profile-scroll-container">
          <WardrobePage isEmbedded={true} onBack={() => setActiveView('profile')} />
        </div>
      </div>
    );
  }

  return (
    <div className="profile-container">
      {/* Шапка профиля БЕЗ кнопки "Назад" */}
      <header className="profile-header">
        <div style={{ width: '20px' }}></div>
        <h1 className="profile-title">Профиль</h1>
        {!isGuest ? (
          <button className="logout-btn" onClick={handleLogout}>
            Выйти
          </button>
        ) : (
          <div style={{ width: '20px' }}></div>
        )}
      </header>

      <div className="profile-scroll-container">
        
        {isGuest ? (
          <div className="guest-banner">
            <div className="guest-banner-content">
              <span className="guest-badge">👤 Гость</span>
              <h3>Вы используете гостевой режим</h3>
              <p>Войдите или зарегистрируйтесь, чтобы сохранить историю примерок и получить больше возможностей</p>
              <div className="guest-banner-buttons">
                <button className="guest-action-btn primary" onClick={handleLogin}>
                  Войти
                </button>
                <button className="guest-action-btn secondary" onClick={handleUpgradeToUser}>
                  Зарегистрироваться
                </button>
              </div>
            </div>
          </div>
        ) : (
          <>
            <div className="profile-info">
              <div className="avatar-section">
                <img 
                  src={user?.avatar || 'https://ui-avatars.com/api/?name=User&background=ff0000&color=fff'} 
                  alt="Аватар" 
                  className="profile-avatar"
                />
                <button className="edit-avatar-btn">✎</button>
              </div>
              
              <div className="user-details">
                <h2 className="username">{user?.username || 'Пользователь'}</h2>
                <p className="user-email">{user?.email || 'email@example.com'}</p>
                <button className="edit-profile-btn">Редактировать профиль</button>
              </div>
            </div>

            <div className="stats-section">
              <h3 className="section-title">Статистика</h3>
              <div className="stats-grid">
                {userStats.map((stat, index) => (
                  <div key={index} className="stat-card">
                    <div className="stat-value">{stat.value}</div>
                    <div className="stat-label">{stat.label}</div>
                  </div>
                ))}
              </div>
            </div>

            <div className="photos-section">
              <div className="section-header">
                <h3 className="section-title">Фото для примерок</h3>
                <button className="add-photo-btn" onClick={triggerFileInput}>
                  + Добавить фото
                </button>
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handlePhotoUpload}
                  accept="image/*"
                  style={{ display: 'none' }}
                />
              </div>
              
              {tryOnPhotos.length === 0 ? (
                <div className="empty-photos">
                  <div className="empty-photos-icon">📷</div>
                  <h4>Нет загруженных фото</h4>
                  <p>Загрузите фото, чтобы использовать их для виртуальных примерок</p>
                  <button className="upload-btn" onClick={triggerFileInput}>
                    Загрузить первое фото
                  </button>
                </div>
              ) : (
                <>
                  <div className="photos-grid">
                    {tryOnPhotos.map((photo, index) => (
                      <div 
                        key={photo.id} 
                        className={`photo-item ${index === primaryPhotoIndex ? 'primary' : ''}`}
                      >
                        <img src={photo.url} alt={`Фото ${index + 1}`} />
                        <div className="photo-overlay">
                          {index === primaryPhotoIndex && (
                            <div className="primary-badge">★ Основное</div>
                          )}
                          <div className="photo-actions">
                            <button 
                              className="photo-action-btn delete-btn"
                              onClick={(e) => handleDeletePhoto(index, e)}
                              title="Удалить фото"
                            >
                              🗑️
                            </button>
                            {index !== primaryPhotoIndex && (
                              <button 
                                className="photo-action-btn set-primary-btn"
                                onClick={(e) => handleSetPrimary(index, e)}
                                title="Сделать основным"
                              >
                                ⭐
                              </button>
                            )}
                          </div>
                        </div>
                        <div className="photo-info">
                          <span className="photo-name">Фото {index + 1}</span>
                          <span className="photo-date">{photo.date}</span>
                        </div>
                      </div>
                    ))}
                    
                    <div className="photo-item add-photo-item" onClick={triggerFileInput}>
                      <div className="add-photo-content">
                        <span className="add-icon">+</span>
                        <span className="add-text">Добавить фото</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="photos-info">
                    <p className="photos-hint">
                      <span className="hint-icon">💡</span>
                      <span>Нажмите на кнопку ⭐ чтобы сделать фото основным для примерок</span>
                    </p>
                    <p className="photos-count">
                      Загружено фото: {tryOnPhotos.length} | Основное: {primaryPhotoIndex + 1}
                    </p>
                  </div>
                </>
              )}
            </div>

            <div className="outfits-section">
              <div className="section-header">
                <h3 className="section-title">Недавние примерки</h3>
                <button className="view-all-btn" onClick={() => setActiveView('wardrobe')}>
                  Все →
                </button>
              </div>
              
              <div className="outfits-grid">
                {recentOutfits.map((outfit) => (
                  <div key={outfit.id} className="outfit-card">
                    <img src={outfit.image} alt={outfit.name} />
                    <div className="outfit-overlay">
                      <span className="outfit-name">{outfit.name}</span>
                      <button className="try-again-btn">Примерять снова</button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}

        <div className="settings-section">
          <h3 className="section-title">Настройки</h3>
          <div className="settings-list">
            {!isGuest && (
              <>
                <button className="setting-item" onClick={() => setActiveView('wardrobe')}>
                  <span>👔</span>
                  <span>Мой гардероб</span>
                  <span>→</span>
                </button>
                <button className="setting-item">
                  <span>👁️</span>
                  <span>Вид</span>
                  <span>→</span>
                </button>
                <button className="setting-item">
                  <span>🔔</span>
                  <span>Уведомления</span>
                  <span>→</span>
                </button>
                <button className="setting-item">
                  <span>🔒</span>
                  <span>Конфиденциальность</span>
                  <span>→</span>
                </button>
              </>
            )}
            
            <button className="setting-item logout-item" onClick={isGuest ? logout : handleLogout}>
              <span>🚪</span>
              <span>{isGuest ? 'Выйти из гостевого режима' : 'Выйти из аккаунта'}</span>
              <span>→</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;