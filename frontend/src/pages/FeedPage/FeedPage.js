import React, { useState, useRef, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import ProfilePage from '../ProfilePage/ProfilePage';
import SearchPage from '../SearchPage/SearchPage';
import ChatPage from '../ChatPage/ChatPage';
import MusicTicker from '../../components/MusicTicker/MusicTicker';
import { likeFeedItem } from '../../core/application/usecases/likeFeedItem';
import { unlikeFeedItem } from '../../core/application/usecases/unlikeFeedItem';
import { createApiFeedRepository } from '../../core/infrastructure/repositories/apiFeedRepository';
import feedIcon from '../../assets/icons/feed.png';
import searchIcon from '../../assets/icons/search.png';
import profileIcon from '../../assets/icons/profile.png';
import commentsIcon from '../../assets/icons/comments.png';
import likeIcon from '../../assets/icons/like.png';
import downloadIcon from '../../assets/icons/download.png';
import wardrobeIcon from '../../assets/icons/wardrobe.png';
import './FeedPage.css';

const feedRepository = createApiFeedRepository();

const FeedPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  
  // Состояние для показа сплеша после входа
  const [showEntrySplash, setShowEntrySplash] = useState(true);
  const [isTransitioning, setIsTransitioning] = useState(false);
  
  // Состояния для постов и навигации
  const [currentPostIndex, setCurrentPostIndex] = useState(0);
  const [currentPhotoIndex, setCurrentPhotoIndex] = useState(0);
  const [isLiked, setIsLiked] = useState({});
  const [likeCounts, setLikeCounts] = useState({});
  const [commentCounts, setCommentCounts] = useState({});
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
    const savedTheme = localStorage.getItem('appTheme') || 'dark';
    const root = document.documentElement;
    root.classList.remove('theme-dark', 'theme-light');
    root.classList.add(`theme-${savedTheme}`);
    localStorage.setItem('appTheme', savedTheme);
    setSettings(prev => ({ ...prev, theme: savedTheme }));
  }, []);

  const COMMON_AUDIO_URL = 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3';
  const COMMON_TRACK_TITLE = 'Calm Ambient Flow';
  const COMMON_TRACK_SOURCE = 'SoundHelix';

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
        'https://images.unsplash.com/photo-1483985988355-763728e1935b?auto=format&fit=crop&w=900&q=85&fm=jpg',
        'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?auto=format&fit=crop&w=900&q=85&fm=jpg'
      ],
      description: 'Классический костюм и рубашка для офиса #офисныйстиль #деловойкостюм',
      likes: 0,
      comments: 0,
      shares: 0,
      tryOnCount: 0,
      music: COMMON_TRACK_TITLE,
      audioUrl: COMMON_AUDIO_URL,
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
        'https://images.unsplash.com/photo-1591369822096-ffd140ec948f?auto=format&fit=crop&w=900&q=85&fm=jpg',
        'https://images.unsplash.com/photo-1496747611176-843222e1e57c?auto=format&fit=crop&w=900&q=85&fm=jpg'
      ],
      description: 'Подборка вечерних платьев для особого случая #вечернийобраз #платье',
      likes: 0,
      comments: 0,
      shares: 0,
      tryOnCount: 0,
      music: COMMON_TRACK_TITLE,
      audioUrl: COMMON_AUDIO_URL,
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
        'https://images.unsplash.com/photo-1485968579580-b6d095142e6e?auto=format&fit=crop&w=900&q=85&fm=jpg',
        'https://images.unsplash.com/photo-1512436991641-6745cdb1723f?auto=format&fit=crop&w=900&q=85&fm=jpg'
      ],
      description: 'Спортивная коллекция для активного отдыха #спорт #стиль #тренировки',
      likes: 0,
      comments: 0,
      shares: 0,
      tryOnCount: 0,
      music: COMMON_TRACK_TITLE,
      audioUrl: COMMON_AUDIO_URL,
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
        'https://images.unsplash.com/photo-1463100099107-aa0980c362e6?auto=format&fit=crop&w=900&q=85&fm=jpg',
        'https://images.unsplash.com/photo-1491553895911-0055eca6402d?auto=format&fit=crop&w=900&q=85&fm=jpg'
      ],
      description: 'Капсула для города: обувь и базовые вещи #повседневка #городскойстиль',
      likes: 0,
      comments: 0,
      shares: 0,
      tryOnCount: 0,
      music: COMMON_TRACK_TITLE,
      audioUrl: COMMON_AUDIO_URL,
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
        'https://images.unsplash.com/photo-1544441893-675973e31985?auto=format&fit=crop&w=900&q=85&fm=jpg',
        'https://images.unsplash.com/photo-1445205170230-053b83016050?auto=format&fit=crop&w=900&q=85&fm=jpg'
      ],
      description: 'Верхняя одежда на осень: пальто и куртки #пальто #классика #осень',
      likes: 0,
      comments: 0,
      shares: 0,
      tryOnCount: 0,
      music: COMMON_TRACK_TITLE,
      audioUrl: COMMON_AUDIO_URL,
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
        'https://images.unsplash.com/photo-1485230895905-ec40ba36b9bc?auto=format&fit=crop&w=900&q=85&fm=jpg',
        'https://images.unsplash.com/photo-1434389677669-e08b4cac3105?auto=format&fit=crop&w=900&q=85&fm=jpg'
      ],
      description: 'Бохо-образы и легкие ткани для теплого сезона #бохо #свободныйстиль #творчество',
      likes: 0,
      comments: 0,
      shares: 0,
      tryOnCount: 0,
      music: COMMON_TRACK_TITLE,
      audioUrl: COMMON_AUDIO_URL,
      tags: ['#бохо', '#свободныйстиль', '#творчество'],
      outfit: {
        brand: 'Mango',
        type: 'Бохо-комплект',
        price: '11,500 ₽',
        available: true
      }
    }
  ];

  useEffect(() => {
    let isMounted = true;

    void (async () => {
      try {
        const feedItems = await feedRepository.fetchFeedItems({ skip: 0, limit: 200 });
        if (!isMounted) {
          return;
        }

        const byId = new Map(feedItems.map((item) => [Number(item?.id), item]));

        setLikeCounts(
          samplePosts.reduce((acc, post) => {
            acc[post.id] = Number(byId.get(post.id)?.likes_count || 0);
            return acc;
          }, {})
        );

        setCommentCounts(
          samplePosts.reduce((acc, post) => {
            acc[post.id] = Number(byId.get(post.id)?.comments_count || 0);
            return acc;
          }, {})
        );

        setIsLiked(
          samplePosts.reduce((acc, post) => {
            acc[post.id] = Boolean(byId.get(post.id)?.is_liked);
            return acc;
          }, {})
        );
      } catch (error) {
        if (!isMounted) {
          return;
        }
        setLikeCounts(
          samplePosts.reduce((acc, post) => {
            acc[post.id] = 0;
            return acc;
          }, {})
        );
        setCommentCounts(
          samplePosts.reduce((acc, post) => {
            acc[post.id] = 0;
            return acc;
          }, {})
        );
        setIsLiked({});
      }
    })();

    return () => {
      isMounted = false;
    };
  }, []);

  // Получаем текущий пост и текущее фото
  const currentPost = activeTab === 'feed' ? samplePosts[currentPostIndex] : null;
  const isFirstPhoto = currentPhotoIndex === 0;

  useEffect(() => {
    const requestedTab = location.state?.openTab;
    if (!requestedTab) {
      return;
    }

    const allowedTabs = ['feed', 'search', 'chat', 'profile'];
    if (!allowedTabs.includes(requestedTab)) {
      return;
    }

    setActiveTab(requestedTab);
    if (requestedTab === 'feed') {
      setCurrentPostIndex(0);
      setCurrentPhotoIndex(0);
    }
  }, [location.state]);

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
                handleTryOn(currentPost.id, currentPhotoIndex);
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
                handleTryOn(currentPost.id, currentPhotoIndex);
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
        if (activeTab !== 'feed') {
          return;
        }

        if (Math.abs(e.deltaX) > 24 && Math.abs(e.deltaX) > Math.abs(e.deltaY)) {
          e.preventDefault();
          if (e.deltaX > 0) {
            nextPhoto();
          } else if (currentPhotoIndex > 0) {
            prevPhoto();
          } else if (isFirstPhoto) {
            handleTryOn(currentPost.id, currentPhotoIndex);
          }
          return;
        }

        if (Math.abs(e.deltaY) > 30) {
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

  const handleLike = async (postId) => {
    const wasLiked = Boolean(isLiked[postId]);

    setIsLiked((prev) => ({
      ...prev,
      [postId]: !wasLiked
    }));
    setLikeCounts((prev) => ({
      ...prev,
      [postId]: Math.max(0, (prev[postId] ?? 0) + (wasLiked ? -1 : 1))
    }));

    try {
      if (wasLiked) {
        await unlikeFeedItem(feedRepository, postId);
      } else {
        await likeFeedItem(feedRepository, postId);
      }
    } catch (error) {
      setIsLiked((prev) => ({
        ...prev,
        [postId]: wasLiked
      }));
      setLikeCounts((prev) => ({
        ...prev,
        [postId]: Math.max(0, (prev[postId] ?? 0) + (wasLiked ? 1 : -1))
      }));
      return;
    }

    if (!wasLiked) {
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

  const handleTryOn = (postId, photoIndex = 0) => {
    const post = samplePosts.find(p => p.id === postId);
    const clothPhoto = post?.photos?.[photoIndex] || post?.photos?.[0] || '';
    navigate('/try-on', { 
      state: { 
        postId, 
        outfit: post.outfit, 
        user: post.user,
        photo: clothPhoto,
        clothPhoto,
        autoStart: true
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

                      <MusicTicker
                        title={post.music}
                        source={COMMON_TRACK_SOURCE}
                        audioUrl={post.audioUrl}
                        isActive={currentPost.id === post.id && activeTab === 'feed'}
                      />

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
                      <img src={likeIcon} alt="" className="action-icon-img" />
                    </span>
                    <span className="action-count">
                      {likeCounts[post.id] ?? post.likes}
                    </span>
                  </button>

                  <button 
                    className="action-btn" 
                    onClick={() => handleComment(post.id)} 
                    title="Комментарии"
                  >
                    <span className="action-icon">
                      <img src={commentsIcon} alt="" className="action-icon-img" />
                    </span>
                    <span className="action-count">{commentCounts[post.id] ?? 0}</span>
                  </button>

                  <button 
                    className="action-btn" 
                    onClick={() => handleShare(post.id)} 
                    title="Поделиться"
                  >
                    <span className="action-icon">
                      <img src={downloadIcon} alt="" className="action-icon-img" />
                    </span>
                    <span className="action-count">{post.shares}</span>
                  </button>

                  {currentPost.id === post.id && isFirstPhoto && (
                    <button 
                      className="action-btn try-on-action" 
                      onClick={() => handleTryOn(post.id, currentPhotoIndex)} 
                      title="Примерять эту одежду"
                    >
                      <span className="action-icon">
                        <img src={wardrobeIcon} alt="" className="action-icon-img" />
                      </span>
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
          <span className="nav-icon">
            <img src={feedIcon} alt="" className="nav-icon-img" />
          </span>
          <span className="nav-label">Лента</span>
        </button>
        <button 
          className={`bottom-nav-btn ${activeTab === 'search' ? 'active' : ''}`} 
          onClick={() => handleTabChange('search')}
          title="Поиск"
        >
          <span className="nav-icon">
            <img src={searchIcon} alt="" className="nav-icon-img" />
          </span>
          <span className="nav-label">Поиск</span>
        </button>
        <button className="camera-btn" onClick={handleCamera} title="Новая примерка">
          <span className="camera-icon">
            <img src={wardrobeIcon} alt="" className="camera-icon-img" />
          </span>
        </button>
        <button 
          className={`bottom-nav-btn ${activeTab === 'chat' ? 'active' : ''}`} 
          onClick={() => handleTabChange('chat')}
          title="Чаты"
        >
          <span className="nav-icon">
            <img src={commentsIcon} alt="" className="nav-icon-img" />
          </span>
          <span className="nav-label">Чаты</span>
        </button>
        <button 
          className={`bottom-nav-btn ${activeTab === 'profile' ? 'active' : ''}`} 
          onClick={() => handleTabChange('profile')}
          title="Профиль"
        >
          <span className="nav-icon">
            <img src={profileIcon} alt="" className="nav-icon-img" />
          </span>
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
