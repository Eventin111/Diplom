import React, { useState, useRef, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { uploadMedia } from '../../services/api/media';
import WardrobePage from '../WardrobePage/WardrobePage';
import './ProfilePage.css';

const readFileAsDataUrl = (file) =>
  new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result || ''));
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });

const compressImage = async (file, { maxSize = 1600, quality = 0.85 } = {}) => {
  if (!file.type.startsWith('image/')) {
    return file;
  }

  const dataUrl = await readFileAsDataUrl(file);
  const image = await new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = reject;
    img.src = dataUrl;
  });

  const longestSide = Math.max(image.width, image.height);
  if (longestSide <= maxSize) {
    return file;
  }

  const scale = maxSize / longestSide;
  const width = Math.round(image.width * scale);
  const height = Math.round(image.height * scale);

  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;

  const context = canvas.getContext('2d');
  if (!context) {
    return file;
  }

  context.drawImage(image, 0, 0, width, height);

  const blob = await new Promise((resolve) => {
    canvas.toBlob(resolve, 'image/jpeg', quality);
  });

  if (!blob) {
    return file;
  }

  const nextName = file.name.replace(/\.[^.]+$/, '') || 'image';
  return new File([blob], `${nextName}.jpg`, { type: 'image/jpeg' });
};

const ProfilePage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout, isAuthenticated, updateUserProfile, previewUserProfile } = useAuth();

  const isGuest = user?.isGuest;
  const isStandaloneProfileRoute = location.pathname === '/profile';
  const [activeView, setActiveView] = useState('profile');
  const [isAppearanceOpen, setIsAppearanceOpen] = useState(false);
  const [themeMode, setThemeMode] = useState(() => localStorage.getItem('appTheme') || 'dark');
  
  const [tryOnPhotos, setTryOnPhotos] = useState(() => {
    const savedPhotos = localStorage.getItem('tryOnPhotos');
    return savedPhotos ? JSON.parse(savedPhotos) : [];
  });
  const [primaryPhotoIndex, setPrimaryPhotoIndex] = useState(() => {
    const savedIndex = localStorage.getItem('primaryPhotoIndex');
    return savedIndex ? parseInt(savedIndex) : 0;
  });
  const fileInputRef = useRef(null);
  const avatarInputRef = useRef(null);
  const [uploadError, setUploadError] = useState('');

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
    const files = Array.from(e.target.files || []);
    if (!files.length) return;

    setUploadError('');
    void (async () => {
      try {
        const preparedFiles = await Promise.all(
          files.map(async (file) => ({
            originalName: file.name,
            previewUrl: await readFileAsDataUrl(file),
            uploadFile: await compressImage(file)
          }))
        );

        const tempPhotos = preparedFiles.map((item, index) => ({
          id: `temp-${Date.now()}-${index}`,
          mediaId: null,
          url: item.previewUrl,
          name: item.originalName,
          date: new Date().toLocaleDateString(),
          isUploading: true
        }));

        setTryOnPhotos((prevPhotos) => {
          const updatedPhotos = [...prevPhotos, ...tempPhotos];
          localStorage.setItem('tryOnPhotos', JSON.stringify(updatedPhotos));

          if (prevPhotos.length === 0 && updatedPhotos.length > 0) {
            setPrimaryPhotoIndex(0);
            localStorage.setItem('primaryPhotoIndex', '0');
          }

          return updatedPhotos;
        });

        const uploads = await Promise.all(
          preparedFiles.map((item) => uploadMedia(item.uploadFile))
        );

        setTryOnPhotos((prevPhotos) => {
          const uploadedPhotos = uploads.map((payload, index) => ({
            id: payload.media.id,
            mediaId: payload.media.id,
            url: payload.upload_url || payload.media.public_url || tempPhotos[index].url,
            name: preparedFiles[index].originalName,
            date: tempPhotos[index].date
          }));

          const updatedPhotos = prevPhotos.map((photo) => {
            const tempIndex = tempPhotos.findIndex((tempPhoto) => tempPhoto.id === photo.id);
            return tempIndex === -1 ? photo : uploadedPhotos[tempIndex];
          });

          localStorage.setItem('tryOnPhotos', JSON.stringify(updatedPhotos));
          return updatedPhotos;
        });
      } catch (error) {
        setUploadError(error?.message || 'Не удалось загрузить фото');
      }
    })();
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

  const triggerAvatarInput = () => {
    avatarInputRef.current?.click();
  };

  const handleAvatarUpload = (e) => {
    const file = e.target.files?.[0];
    if (!file) {
      return;
    }

    setUploadError('');
    void (async () => {
      try {
        const previewUrl = await readFileAsDataUrl(file);
        previewUserProfile({ avatar: previewUrl });
        const uploadFile = await compressImage(file, { maxSize: 1200, quality: 0.82 });
        const payload = await uploadMedia(uploadFile);
        const avatarUrl = payload.upload_url || payload.media.public_url;
        if (!avatarUrl) {
          throw new Error('Сервер не вернул ссылку на аватар');
        }
        await updateUserProfile({ avatar: avatarUrl });
      } catch (error) {
        setUploadError(error?.message || 'Не удалось обновить аватар');
      }
    })();
    e.target.value = '';
  };

  useEffect(() => {
    const savedTheme = localStorage.getItem('appTheme') || 'dark';
    const root = document.documentElement;
    root.classList.remove('theme-dark', 'theme-light');
    root.classList.add(`theme-${savedTheme}`);
    localStorage.setItem('appTheme', savedTheme);
    setThemeMode(savedTheme);
  }, []);

  const handleThemeChange = (nextTheme) => {
    if (!nextTheme || nextTheme === themeMode) {
      return;
    }

    const root = document.documentElement;
    root.classList.remove('theme-dark', 'theme-light');
    root.classList.add(`theme-${nextTheme}`);
    localStorage.setItem('appTheme', nextTheme);
    setThemeMode(nextTheme);

    const settingsRaw = localStorage.getItem('appSettings');
    if (settingsRaw) {
      try {
        const parsed = JSON.parse(settingsRaw);
        localStorage.setItem('appSettings', JSON.stringify({ ...parsed, theme: nextTheme }));
      } catch (error) {
        localStorage.setItem('appSettings', JSON.stringify({ theme: nextTheme, showInstructions: true }));
      }
    }
  };

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
        {isStandaloneProfileRoute ? (
          <button className="back-btn" onClick={() => navigate('/')}>
            ← Лента
          </button>
        ) : (
          <div style={{ width: '20px' }}></div>
        )}
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
            {uploadError && <div className="tryon-alert tryon-alert--error">{uploadError}</div>}
            <div className="profile-info">
              <div className="avatar-section">
                <img 
                  src={user?.avatar || 'https://ui-avatars.com/api/?name=User&background=ff0000&color=fff'} 
                  alt="Аватар" 
                  className="profile-avatar"
                />
                <button className="edit-avatar-btn" onClick={triggerAvatarInput} title="Сменить аватар">
                  ✎
                </button>
                <input
                  type="file"
                  ref={avatarInputRef}
                  onChange={handleAvatarUpload}
                  accept="image/*"
                  style={{ display: 'none' }}
                />
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
                  multiple
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
                <button className="setting-item" onClick={() => setIsAppearanceOpen((prev) => !prev)}>
                  <span>👁️</span>
                  <span>Вид</span>
                  <span>{isAppearanceOpen ? '↓' : '→'}</span>
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

          {!isGuest && isAppearanceOpen && (
            <div className="appearance-panel">
              <p className="appearance-title">Тема приложения</p>
              <div className="appearance-options">
                <button
                  className={`appearance-option ${themeMode === 'dark' ? 'active' : ''}`}
                  onClick={() => handleThemeChange('dark')}
                >
                  <span>🌙</span>
                  <span>Темная</span>
                </button>
                <button
                  className={`appearance-option ${themeMode === 'light' ? 'active' : ''}`}
                  onClick={() => handleThemeChange('light')}
                >
                  <span>☀️</span>
                  <span>Светлая</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
