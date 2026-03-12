import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import ProfilePage from '../ProfilePage/ProfilePage';
import SearchPage from '../SearchPage/SearchPage';
import WardrobePage from '../WardrobePage/WardrobePage';
import ChatPage from '../ChatPage/ChatPage';
import './FeedPage.css';

const FeedPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  
  // Состояние для показа сплеша после входа
  const [showEntrySplash, setShowEntrySplash] = useState(true);
  const [isTransitioning, setIsTransitioning] = useState(false);
  
  // Состояния для постов и навигации
  const [currentPostIndex, setCurrentPostIndex] = useState(0);
  const [currentPhotoIndex, setCurrentPhotoIndex] = useState(0);
  const [isLiked, setIsLiked] = useState({});
  const [photoTransition, setPhotoTransition] = useState(false);
  
  // Настройки из localStorage
  const [settings, setSettings] = useState(() => {
    const savedSettings = localStorage.getItem('appSettings');
    return savedSettings ? JSON.parse(savedSettings) : {
      theme: 'dark',
      showInstructions: true,
      hasChosenTheme: false
    };
  });
  
  // Состояние для активной вкладки
  const [activeTab, setActiveTab] = useState('feed');
  
  const touchStartX = useRef(0);
  const touchStartY = useRef(0);
  const isSwiping = useRef(false);

  // Эффект для скрытия сплеша
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsTransitioning(true);
      setTimeout(() => {
        setShowEntrySplash(false);
      }, 300);
    }, 1500);
    
    return () => clearTimeout(timer);
  }, []);
  
  // Загружаем настройки темы
  useEffect(() => {
    const savedTheme = localStorage.getItem('appTheme');
    if (savedTheme) {
      document.documentElement.className = `theme-${savedTheme}`;
      setSettings(prev => ({ ...prev, theme: savedTheme }));
    }
  }, []);

  // ПОСТЫ С ФОТО
  const samplePosts = [
    {
      id: 1,
      user: {
        name: 'Алексей',
        username: '@alex_style',
        avatar: 'https://ui-avatars.com/api/?name=Алексей&background=ff0000&color=fff'
      },
      photos: [
        'https://images.unsplash.com/photo-1594938298603-c8148c4dae35?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1552374196-c4e7ffc6e126?ixlib=rb-1.2.1&auto=format&fit=crop&w-800&q=80',
        'https://images.unsplash.com/photo-1520975916090-3105956dac38?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80'
      ],
      description: 'Классический костюм от Giorgio Armani #офисныйстиль #деловойкостюм',
      likes: 2450,
      comments: 320,
      shares: 45,
      tryOnCount: 124,
      music: 'Модный бит - Fashion Beats',
      tags: ['#костюм', '#офис', '#деловойстиль'],
      outfit: {
        brand: 'Giorgio Armani',
        type: 'Костюм',
        price: '45,000 ₽',
        available: true
      }
    },
    {
      id: 2,
      user: {
        name: 'Мария',
        username: '@mari_fashion',
        avatar: 'https://ui-avatars.com/api/?name=Мария&background=ff3333&color=fff'
      },
      photos: [
        'https://images.unsplash.com/photo-1490481651871-ab68de25d43d?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1539109136881-3be0616acf4b?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80'
      ],
      description: 'Вечернее платье для особого случая 👗 #вечернийобраз #платье',
      likes: 1890,
      comments: 210,
      shares: 32,
      tryOnCount: 89,
      music: 'Original Sound - Maria Style',
      tags: ['#платье', '#вечер', '#образ'],
      outfit: {
        brand: 'Dolce & Gabbana',
        type: 'Платье',
        price: '78,000 ₽',
        available: true
      }
    },
    {
      id: 3,
      user: {
        name: 'Иван',
        username: '@ivan_sport',
        avatar: 'https://ui-avatars.com/api/?name=Иван&background=0088ff&color=fff'
      },
      photos: [
        'https://images.unsplash.com/photo-1544441893-675973e31985?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1511994717241-7e3d81c6e3e6?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80'
      ],
      description: 'Спортивная одежда для активного отдыха 🏃‍♂️ #спорт #стиль #тренировки',
      likes: 3250,
      comments: 450,
      shares: 120,
      tryOnCount: 210,
      music: 'Workout Mix - Energy Beat',
      tags: ['#спорт', '#тренировки', '#активныйстиль'],
      outfit: {
        brand: 'Nike',
        type: 'Спортивный костюм',
        price: '12,500 ₽',
        available: true
      }
    },
    {
      id: 4,
      user: {
        name: 'Елена',
        username: '@elena_chic',
        avatar: 'https://ui-avatars.com/api/?name=Елена&background=ff00aa&color=fff'
      },
      photos: [
        'https://images.unsplash.com/photo-1552374196-1ab2a1c593e8?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80'
      ],
      description: 'Повседневный стиль от Zara для городских прогулок 🏙️ #повседневка #городскойстиль',
      likes: 1560,
      comments: 189,
      shares: 45,
      tryOnCount: 98,
      music: 'City Vibes - Urban Sounds',
      tags: ['#повседневка', '#зара', '#городскойстиль'],
      outfit: {
        brand: 'Zara',
        type: 'Повседневный комплект',
        price: '8,900 ₽',
        available: true
      }
    },
    {
      id: 5,
      user: {
        name: 'Дмитрий',
        username: '@dima_classic',
        avatar: 'https://ui-avatars.com/api/?name=Дмитрий&background=00aa00&color=fff'
      },
      photos: [
        'https://images.unsplash.com/photo-1552902865-b72c031ac5ea?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1554412933-514a83d2f3c8?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80'
      ],
      description: 'Классическое пальто для осенних вечеров 🍂 #пальто #классика #осень',
      likes: 2780,
      comments: 320,
      shares: 67,
      tryOnCount: 145,
      music: 'Classical Elegance - Timeless',
      tags: ['#пальто', '#классика', '#осень'],
      outfit: {
        brand: 'Burberry',
        type: 'Пальто',
        price: '65,000 ₽',
        available: true
      }
    },
    {
      id: 6,
      user: {
        name: 'Анна',
        username: '@anna_boho',
        avatar: 'https://ui-avatars.com/api/?name=Анна&background=ff8800&color=fff'
      },
      photos: [
        'https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1525171254930-643fc658b64e?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80'
      ],
      description: 'Бохо-стиль для свободных духом 🌼 #бохо #свободныйстиль #творчество',
      likes: 1420,
      comments: 167,
      shares: 38,
      tryOnCount: 76,
      music: 'Boho Dreams - Acoustic',
      tags: ['#бохо', '#свободныйстиль', '#творчество'],
      outfit: {
        brand: 'Mango',
        type: 'Бохо-комплект',
        price: '11,500 ₽',
        available: true
      }
    }
  ];

  // Получаем текущий пост и текущее фото
  const currentPost = activeTab === 'feed' ? samplePosts[currentPostIndex] : null;
  const isFirstPhoto = currentPhotoIndex === 0;

  // Функции для навигации с анимацией
  const nextPhoto = () => {
    if (currentPost && currentPhotoIndex < currentPost.photos.length - 1) {
      setPhotoTransition(true);
      setTimeout(() => {
        setCurrentPhotoIndex(prev => prev + 1);
        setTimeout(() => {
          setPhotoTransition(false);
        }, 50);
      }, 200);
    }
  };

  const prevPhoto = () => {
    if (currentPhotoIndex > 0) {
      setPhotoTransition(true);
      setTimeout(() => {
        setCurrentPhotoIndex(prev => prev - 1);
        setTimeout(() => {
          setPhotoTransition(false);
        }, 50);
      }, 200);
    }
  };

  const nextPost = () => {
    if (currentPostIndex < samplePosts.length - 1) {
      setPhotoTransition(true);
      setTimeout(() => {
        setCurrentPostIndex(prev => prev + 1);
        setCurrentPhotoIndex(0);
        setTimeout(() => {
          setPhotoTransition(false);
        }, 50);
      }, 200);
    } else {
      // Если достигли конца - возвращаемся к первому посту
      setPhotoTransition(true);
      setTimeout(() => {
        setCurrentPostIndex(0);
        setCurrentPhotoIndex(0);
        setTimeout(() => {
          setPhotoTransition(false);
        }, 50);
      }, 200);
    }
  };

  const prevPost = () => {
    if (currentPostIndex > 0) {
      setPhotoTransition(true);
      setTimeout(() => {
        setCurrentPostIndex(prev => prev - 1);
        setCurrentPhotoIndex(0);
        setTimeout(() => {
          setPhotoTransition(false);
        }, 50);
      }, 200);
    } else {
      // Если достигли начала - переходим к последнему посту
      setPhotoTransition(true);
      setTimeout(() => {
        setCurrentPostIndex(samplePosts.length - 1);
        setCurrentPhotoIndex(0);
        setTimeout(() => {
          setPhotoTransition(false);
        }, 50);
      }, 200);
    }
  };

  // Обработка свайпов для мобильных
  useEffect(() => {
    if (!showEntrySplash && activeTab === 'feed') {
      const handleTouchStart = (e) => {
        if (isSwiping.current) return;
        touchStartX.current = e.touches[0].clientX;
        touchStartY.current = e.touches[0].clientY;
        isSwiping.current = true;
      };

      const handleTouchMove = (e) => {
        if (!isSwiping.current) return;
        e.preventDefault();
      };

      const handleTouchEnd = (e) => {
        if (!isSwiping.current) return;
        
        const touchEndX = e.changedTouches[0].clientX;
        const touchEndY = e.changedTouches[0].clientY;
        const diffX = touchStartX.current - touchEndX;
        const diffY = touchStartY.current - touchEndY;

        setTimeout(() => {
          isSwiping.current = false;
        }, 100);

        const minSwipeDistance = 50;
        const isHorizontalSwipe = Math.abs(diffX) > Math.abs(diffY);
        const isSwipeLongEnough = Math.abs(diffX) > minSwipeDistance || Math.abs(diffY) > minSwipeDistance;

        if (isSwipeLongEnough) {
          if (isHorizontalSwipe) {
            if (diffX > 0) {
              // Свайп влево - следующее фото
              nextPhoto();
            } else {
              // Свайп вправо - назад/примерка
              if (currentPhotoIndex > 0) {
                prevPhoto();
              } else if (isFirstPhoto) {
                handleTryOn(currentPost.id);
              }
            }
          } else {
            if (diffY > 0) {
              nextPost(); // Свайп вниз
            } else {
              prevPost(); // Свайп вверх
            }
          }
        }
      };

      const videoFeed = document.querySelector('.photo-feed');
      if (videoFeed) {
        videoFeed.addEventListener('touchstart', handleTouchStart, { passive: false });
        videoFeed.addEventListener('touchmove', handleTouchMove, { passive: false });
        videoFeed.addEventListener('touchend', handleTouchEnd, { passive: false });
      }

      return () => {
        const videoFeed = document.querySelector('.photo-feed');
        if (videoFeed) {
          videoFeed.removeEventListener('touchstart', handleTouchStart);
          videoFeed.removeEventListener('touchmove', handleTouchMove);
          videoFeed.removeEventListener('touchend', handleTouchEnd);
        }
      };
    }
  }, [showEntrySplash, currentPostIndex, currentPhotoIndex, currentPost, isFirstPhoto, activeTab]);

  // Обработка клавиатуры для ПК
  useEffect(() => {
    if (!showEntrySplash) {
      const handleKeyDown = (e) => {
        if (activeTab === 'feed') {
          switch(e.key.toLowerCase()) {
            case 'arrowright':
            case 'd':
              e.preventDefault();
              nextPhoto();
              break;
            case 'arrowleft':
            case 'a':
              e.preventDefault();
              if (currentPhotoIndex > 0) {
                prevPhoto();
              } else if (isFirstPhoto) {
                handleTryOn(currentPost.id);
              }
              break;
            case 'arrowup':
            case 'w':
              e.preventDefault();
              prevPost();
              break;
            case 'arrowdown':
            case 's':
              e.preventDefault();
              nextPost();
              break;
            case 'i':
            case '?':
              e.preventDefault();
              setSettings(prev => ({
                ...prev,
                showInstructions: !prev.showInstructions
              }));
              break;
          }
        }
      };

      const handleWheel = (e) => {
        if (activeTab === 'feed' && Math.abs(e.deltaY) > 30) {
          e.preventDefault();
          if (e.deltaY > 0) {
            nextPost();
          } else {
            prevPost();
          }
        }
      };

      window.addEventListener('keydown', handleKeyDown);
      window.addEventListener('wheel', handleWheel, { passive: false });

      return () => {
        window.removeEventListener('keydown', handleKeyDown);
        window.removeEventListener('wheel', handleWheel);
      };
    }
  }, [showEntrySplash, currentPostIndex, currentPhotoIndex, currentPost, isFirstPhoto, activeTab, settings.showInstructions]);

  // Сохраняем настройки в localStorage
  useEffect(() => {
    localStorage.setItem('appSettings', JSON.stringify(settings));
  }, [settings]);

  const handleLike = (postId) => {
    setIsLiked(prev => ({
      ...prev,
      [postId]: !prev[postId]
    }));

    if (!isLiked[postId]) {
      const heart = document.createElement('div');
      heart.innerHTML = '❤️';
      heart.style.position = 'fixed';
      heart.style.fontSize = '3rem';
      heart.style.pointerEvents = 'none';
      heart.style.zIndex = '1000';
      heart.style.left = '50%';
      heart.style.top = '50%';
      heart.style.transform = 'translate(-50%, -50%)';
      heart.style.animation = 'heartFloat 1s ease-out forwards';
      document.body.appendChild(heart);
      setTimeout(() => {
        document.body.removeChild(heart);
      }, 1000);
    }
  };

  const handleTryOn = (postId) => {
    const post = samplePosts.find(p => p.id === postId);
    navigate('/try-on', { 
      state: { 
        postId, 
        outfit: post.outfit, 
        user: post.user,
        photo: post.photos[0]
      } 
    });
  };

  const handleComment = (postId) => {
    console.log('Open comments for:', postId);
  };

  const handleShare = (postId) => {
    console.log('Share post:', postId);
    if (navigator.share) {
      navigator.share({
        title: 'Swipelt - Виртуальная примерка',
        text: 'Посмотри этот образ в Swipelt!',
        url: window.location.href,
      });
    }
  };

  const handleFollow = (username) => {
    console.log('Follow:', username);
  };

  const handleCamera = () => {
    navigate('/try-on');
  };

  const handlePostClick = (index) => {
    setPhotoTransition(true);
    setTimeout(() => {
      setCurrentPostIndex(index);
      setCurrentPhotoIndex(0);
      setTimeout(() => {
        setPhotoTransition(false);
      }, 50);
    }, 200);
  };

  const handlePhotoClick = (index) => {
    setPhotoTransition(true);
    setTimeout(() => {
      setCurrentPhotoIndex(index);
      setTimeout(() => {
        setPhotoTransition(false);
      }, 50);
    }, 200);
  };

  // Переключение между вкладками
  const handleTabChange = (tab) => {
    setActiveTab(tab);
    if (tab === 'feed') {
      setPhotoTransition(true);
      setTimeout(() => {
        setCurrentPostIndex(0);
        setCurrentPhotoIndex(0);
        setTimeout(() => {
          setPhotoTransition(false);
        }, 50);
      }, 200);
    }
  };

  // Показать инструкцию
  const showInstructions = () => {
    setSettings(prev => ({ ...prev, showInstructions: true }));
  };

  // Скрыть инструкцию
  const hideInstructions = () => {
    setSettings(prev => ({ ...prev, showInstructions: false }));
  };

  // Если показываем сплеш
  if (showEntrySplash) {
    return (
      <div style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        background: '#000',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 9999,
        opacity: isTransitioning ? 0 : 1,
        transform: isTransitioning ? 'translateY(-20px)' : 'translateY(0)',
        transition: 'opacity 0.5s ease, transform 0.5s ease',
        pointerEvents: 'none'
      }}>
        <div style={{
          textAlign: 'center'
        }}>
          <div style={{
            fontSize: '3rem',
            fontWeight: 'bold',
            background: 'linear-gradient(45deg, #ff0000, #ff3333, #ff6666, #ff3333, #ff0000)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
            backgroundSize: '200% auto',
            animation: 'gradientFlow 3s ease-in-out infinite',
            marginBottom: '20px'
          }}>
            Swipelt
          </div>
          <div style={{
            color: 'rgba(255, 255, 255, 0.8)',
            fontSize: '1.2rem',
            opacity: isTransitioning ? 0 : 1,
            transition: 'opacity 0.3s ease'
          }}>
            Загрузка ленты...
          </div>
        </div>
        <style>{`
          @keyframes gradientFlow {
            0% { background-position: 0% center; }
            50% { background-position: 100% center; }
            100% { background-position: 0% center; }
          }
        `}</style>
      </div>
    );
  }

  // Отображаем активную вкладку
  const renderContent = () => {
    switch (activeTab) {
      case 'search':
        return <SearchPage />;
      case 'chat':
        return <ChatPage />;
      case 'profile':
        return <ProfilePage />;
      case 'feed':
      default:
        return (
          <div className="photo-feed">
            {samplePosts.map((post, index) => (
              <div
                key={post.id}
                className={`photo-container ${index === currentPostIndex ? 'active' : ''}`}
                style={{
                  transform: `translateY(${(index - currentPostIndex) * 100}vh)`,
                  opacity: index === currentPostIndex ? 1 : 0.7
                }}
              >
                <div className="photo-wrapper">
                  {currentPost.id === post.id && post.photos.map((photo, photoIndex) => (
                    <img
                      key={photoIndex}
                      src={photo}
                      alt={`Фото ${photoIndex + 1} из ${post.photos.length}`}
                      className={`photo-content ${photoIndex === currentPhotoIndex ? 'active' : ''} ${
                        photoTransition ? 'transitioning' : ''
                      }`}
                      loading="lazy"
                      style={{
                        transform: photoIndex === currentPhotoIndex ? 'translateX(0)' : 
                                 photoIndex < currentPhotoIndex ? 'translateX(-100%)' : 'translateX(100%)'
                      }}
                    />
                  ))}

                  {currentPost.id === post.id && post.photos.length > 1 && (
                    <div className="photo-indicator">
                      {post.photos.map((_, photoIndex) => (
                        <div
                          key={photoIndex}
                          className={`photo-dot ${photoIndex === currentPhotoIndex ? 'active' : ''}`}
                          onClick={() => handlePhotoClick(photoIndex)}
                          title={`Фото ${photoIndex + 1}`}
                        />
                      ))}
                    </div>
                  )}

                  <div className="photo-overlay"></div>

                  {/* TikTok стиль: музыка в левом нижнем углу с диском */}
                  <div className="music-info-tiktok">
                    <div className="music-disc">
                      <div className="disc-icon">🎵</div>
                      <div className="disc-spinner"></div>
                    </div>
                    <div className="music-details">
                      <div className="music-title">{post.music}</div>
                      <div className="music-source">Original audio</div>
                    </div>
                  </div>

                  <div className="post-content-wrapper">
                    <div className="post-content">
                      <div className="post-header">
                        <div className="user-info">
                          <img src={post.user.avatar} alt={post.user.name} className="user-avatar" />
                          <div className="user-details">
                            <h3 className="user-name">{post.user.name}</h3>
                            <p className="user-username">{post.user.username}</p>
                          </div>
                        </div>
                        <button 
                          className="follow-btn" 
                          onClick={() => handleFollow(post.user.username)}
                        >
                          Подписаться
                        </button>
                      </div>

                      <div className="post-description">
                        <p className="description-text">{post.description}</p>
                        <div className="post-tags">
                          {post.tags.map((tag, i) => (
                            <span key={i} className="tag">
                              {tag}
                            </span>
                          ))}
                        </div>
                      </div>

                      <div className="outfit-info">
                        <div className="outfit-item">
                          <span className="outfit-icon">🏷️</span>
                          <span className="outfit-text">{post.outfit.brand}</span>
                        </div>
                        <div className="outfit-item">
                          <span className="outfit-icon">💰</span>
                          <span className="outfit-text">{post.outfit.price}</span>
                        </div>
                        <div className={`outfit-item ${post.outfit.available ? 'available' : 'sold-out'}`}>
                          <span className="outfit-icon">
                            {post.outfit.available ? '✅' : '❌'}
                          </span>
                          <span className="outfit-text">
                            {post.outfit.available ? 'В наличии' : 'Нет в наличии'}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="photo-actions-right">
                  <button 
                    className={`action-btn ${isLiked[post.id] ? 'liked' : ''}`} 
                    onClick={() => handleLike(post.id)} 
                    title="Лайк"
                  >
                    <span className="action-icon">
                      {isLiked[post.id] ? '❤️' : '🤍'}
                    </span>
                    <span className="action-count">
                      {isLiked[post.id] ? post.likes + 1 : post.likes}
                    </span>
                  </button>

                  <button 
                    className="action-btn" 
                    onClick={() => handleComment(post.id)} 
                    title="Комментарии"
                  >
                    <span className="action-icon">💬</span>
                    <span className="action-count">{post.comments}</span>
                  </button>

                  <button 
                    className="action-btn" 
                    onClick={() => handleShare(post.id)} 
                    title="Поделиться"
                  >
                    <span className="action-icon">📤</span>
                    <span className="action-count">{post.shares}</span>
                  </button>

                  {currentPost.id === post.id && isFirstPhoto && (
                    <button 
                      className="action-btn try-on-action" 
                      onClick={() => handleTryOn(post.id)} 
                      title="Примерять эту одежду"
                    >
                      <span className="action-icon">👕</span>
                      <span className="action-text">Примерка</span>
                      <span className="action-count">{post.tryOnCount}</span>
                    </button>
                  )}
                </div>
              </div>
            ))}
            
            <div className="post-indicator">
              {samplePosts.map((_, index) => (
                <div
                  key={index}
                  className={`indicator-dot ${index === currentPostIndex ? 'active' : ''}`}
                  onClick={() => handlePostClick(index)}
                  title={`Пост ${index + 1}`}
                />
              ))}
            </div>
          </div>
        );
    }
  };

  return (
    <div className="tiktok-container">
      <nav className="top-nav">
        <div className="logo">Swipelt</div>
      </nav>

      {renderContent()}

      <nav className="bottom-nav">
        <button 
          className={`bottom-nav-btn ${activeTab === 'feed' ? 'active' : ''}`} 
          onClick={() => handleTabChange('feed')}
          title="Лента"
        >
          <span className="nav-icon">🏠</span>
          <span className="nav-label">Лента</span>
        </button>
        <button 
          className={`bottom-nav-btn ${activeTab === 'search' ? 'active' : ''}`} 
          onClick={() => handleTabChange('search')}
          title="Поиск"
        >
          <span className="nav-icon">🔍</span>
          <span className="nav-label">Поиск</span>
        </button>
        <button className="camera-btn" onClick={handleCamera} title="Новая примерка">
          <span className="camera-icon">📷</span>
        </button>
        <button 
          className={`bottom-nav-btn ${activeTab === 'chat' ? 'active' : ''}`} 
          onClick={() => handleTabChange('chat')}
          title="Чаты"
        >
          <span className="nav-icon">💬</span>
          <span className="nav-label">Чаты</span>
        </button>
        <button 
          className={`bottom-nav-btn ${activeTab === 'profile' ? 'active' : ''}`} 
          onClick={() => handleTabChange('profile')}
          title="Профиль"
        >
          <span className="nav-icon">👤</span>
          <span className="nav-label">Профиль</span>
        </button>
      </nav>

      {/* Инструкция (только на ленте) */}
      {settings.showInstructions && activeTab === 'feed' && (
        <div className="instructions-container">
          <div className="instructions-content">
            <button 
              className="close-instructions-btn" 
              onClick={hideInstructions}
              title="Закрыть инструкцию"
            >
              ×
            </button>
            
            <div className="instructions-scroll">
              <h3 className="instructions-title">📱 Управление</h3>
              
              <div className="instructions-section">
                <h4 className="instructions-subtitle">Для ПК:</h4>
                <div className="instruction-item">
                  <span className="instruction-key">→ D</span>
                  <span className="instruction-text">Фото вперед</span>
                </div>
                <div className="instruction-item">
                  <span className="instruction-key">← A</span>
                  <span className="instruction-text">Назад / Примерка</span>
                </div>
                <div className="instruction-item">
                  <span className="instruction-key">↑ W</span>
                  <span className="instruction-text">Предыдущий пост</span>
                </div>
                <div className="instruction-item">
                  <span className="instruction-key">↓ S</span>
                  <span className="instruction-text">Следующий пост</span>
                </div>
                <div className="instruction-item">
                  <span className="instruction-key">I</span>
                  <span className="instruction-text">Инструкция</span>
                </div>
              </div>

              <div className="instructions-section">
                <h4 className="instructions-subtitle">Для телефона:</h4>
                <div className="instruction-item">
                  <span className="instruction-key">←</span>
                  <span className="instruction-text">Фото вперед</span>
                </div>
                <div className="instruction-item">
                  <span className="instruction-key">→</span>
                  <span className="instruction-text">Назад / Примерка</span>
                </div>
                <div className="instruction-item">
                  <span className="instruction-key">↑</span>
                  <span className="instruction-text">Предыдущий пост</span>
                </div>
                <div className="instruction-item">
                  <span className="instruction-key">↓</span>
                  <span className="instruction-text">Следующий пост</span>
                </div>
              </div>

              <div className="instructions-note">
                <span className="note-icon">💡</span>
                Примерка только на первом фото
              </div>
            </div>
            
            <div className="instructions-footer">
              <button 
                className="instructions-hide-btn"
                onClick={hideInstructions}
              >
                Не показывать
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Кнопка для показа инструкции */}
      {!settings.showInstructions && activeTab === 'feed' && (
        <button 
          className="show-instructions-btn" 
          onClick={showInstructions}
          title="Показать инструкцию"
        >
          ?
        </button>
      )}

      <style jsx="true">{`
        @keyframes heartFloat {
          0% {
            opacity: 1;
            transform: translate(-50%, -50%) scale(1);
          }
          100% {
            opacity: 0;
            transform: translate(-50%, -100px) scale(1.5);
          }
        }
      `}</style>
    </div>
  );
};

export default FeedPage;