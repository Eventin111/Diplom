import React, { useEffect, useRef, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { runTryOn } from '../../services/api/tryon';
import './TryOnPage.css';

const INFERENCE_STEPS = ['Подбираем стиль', 'Уточняем посадку', 'Собираем образ', 'Финальный штрих'];

const readPrimaryProfilePhoto = () => {
  try {
    const photosRaw = localStorage.getItem('tryOnPhotos');
    const indexRaw = localStorage.getItem('primaryPhotoIndex');
    const photos = photosRaw ? JSON.parse(photosRaw) : [];
    const parsedIndex = indexRaw ? Number(indexRaw) : 0;
    const safeIndex =
      Number.isInteger(parsedIndex) && parsedIndex >= 0 && parsedIndex < photos.length ? parsedIndex : 0;

    return {
      photo: Array.isArray(photos) && photos.length > 0 ? photos[safeIndex]?.url || '' : '',
      count: Array.isArray(photos) ? photos.length : 0,
      index: safeIndex
    };
  } catch (error) {
    return { photo: '', count: 0, index: 0 };
  }
};

const fileToDataUrl = (file) =>
  new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (event) => resolve(event.target?.result || '');
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });

const TryOnPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const clothInputRef = useRef(null);
  const autoStartTriggeredRef = useRef(false);
  const requestInFlightRef = useRef(false);

  const presetClothPhoto = location.state?.clothPhoto || location.state?.photo || '';
  const [profileInfo, setProfileInfo] = useState(readPrimaryProfilePhoto);
  const [clothFile, setClothFile] = useState(null);
  const [clothPreview, setClothPreview] = useState(presetClothPhoto);
  const [isProcessing, setIsProcessing] = useState(false);
  const [resultImage, setResultImage] = useState('');
  const [error, setError] = useState('');
  const [progress, setProgress] = useState(0);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [activeStepIndex, setActiveStepIndex] = useState(0);

  const outfit = location.state?.outfit || {
    brand: 'Бренд не указан',
    type: 'Одежда',
    price: 'Цена не указана'
  };

  const shouldAutoStart = Boolean(location.state?.autoStart);
  const profileModelPhoto = profileInfo.photo;
  const clothSourceLabel = clothFile
    ? 'Загружено пользователем'
    : presetClothPhoto
      ? 'Выбрано из ленты'
      : 'Фото не выбрано';

  useEffect(() => {
    const syncProfilePhoto = () => {
      setProfileInfo(readPrimaryProfilePhoto());
    };

    syncProfilePhoto();
    window.addEventListener('storage', syncProfilePhoto);
    return () => window.removeEventListener('storage', syncProfilePhoto);
  }, []);

  useEffect(() => {
    setClothPreview(presetClothPhoto);
    setClothFile(null);
    setResultImage('');
    setError('');
    autoStartTriggeredRef.current = false;
  }, [presetClothPhoto]);

  const handlePickClothPhoto = () => {
    clothInputRef.current?.click();
  };

  const handleClothChange = async (event) => {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }

    setClothFile(file);
    setResultImage('');
    setError('');
    setClothPreview(await fileToDataUrl(file));
    event.target.value = '';
  };

  const handleTryOn = async () => {
    if (requestInFlightRef.current) {
      return;
    }

    const clothImageInput = clothFile || clothPreview;

    if (!profileModelPhoto) {
      setError('Сначала добавьте и выберите основное фото в профиле.');
      return;
    }

    if (!clothImageInput) {
      setError('Выберите одежду из ленты или загрузите фото одежды.');
      return;
    }

    requestInFlightRef.current = true;
    setIsProcessing(true);
    setError('');
    setProgress(3);
    setElapsedSeconds(0);
    setActiveStepIndex(0);

    try {
      const payload = await runTryOn({
        modelImage: profileModelPhoto,
        clothImage: clothImageInput,
        modelType: 'hd',
        category: 0,
        scale: 2.0,
        numSteps: 4,
        numSamples: 1,
        seed: -1
      });

      if (!payload.resultUrl) {
        throw new Error('Сервер вернул пустой результат примерки.');
      }

      setProgress(100);
      setActiveStepIndex(INFERENCE_STEPS.length - 1);
      setResultImage(payload.resultUrl);
    } catch (requestError) {
      setError(requestError?.message || 'Ошибка обработки примерки');
    } finally {
      setIsProcessing(false);
      requestInFlightRef.current = false;
    }
  };

  const handleSaveResult = () => {
    if (!resultImage) {
      return;
    }

    const link = document.createElement('a');
    link.href = resultImage;
    link.download = `tryon-result-${Date.now()}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleShare = async () => {
    if (!resultImage || !navigator.share) {
      return;
    }

    try {
      await navigator.share({
        title: 'Результат виртуальной примерки',
        text: 'Примерка в Swipelt',
        url: window.location.href
      });
    } catch (shareError) {
      // user canceled share action
    }
  };

  const goToProfileWithNav = () => {
    navigate('/', { state: { openTab: 'profile' } });
  };

  useEffect(() => {
    if (!shouldAutoStart || autoStartTriggeredRef.current) {
      return;
    }

    if (!profileModelPhoto || !clothPreview) {
      return;
    }

    const autoStartKey = `tryon-autostart:${location.key || 'default'}`;
    try {
      if (sessionStorage.getItem(autoStartKey) === '1') {
        autoStartTriggeredRef.current = true;
        return;
      }
      sessionStorage.setItem(autoStartKey, '1');
    } catch (storageError) {
      // ignore storage limitations in private mode
    }

    autoStartTriggeredRef.current = true;
    void handleTryOn();
  }, [clothPreview, location.key, profileModelPhoto, shouldAutoStart]);

  useEffect(() => {
    if (!isProcessing) {
      return;
    }

    const progressTimer = window.setInterval(() => {
      setProgress((current) => {
        if (current >= 92) {
          return current;
        }

        const next = Math.min(92, current + Math.floor(Math.random() * 8) + 3);
        const stepIndex = Math.min(
          INFERENCE_STEPS.length - 1,
          Math.floor((next / 100) * INFERENCE_STEPS.length)
        );
        setActiveStepIndex(stepIndex);
        return next;
      });
    }, 850);

    const elapsedTimer = window.setInterval(() => {
      setElapsedSeconds((sec) => sec + 1);
    }, 1000);

    return () => {
      window.clearInterval(progressTimer);
      window.clearInterval(elapsedTimer);
    };
  }, [isProcessing]);

  return (
    <div className="tryon-page">
      <header className="tryon-page__header">
        <button className="tryon-page__back" onClick={() => navigate('/')}>
          Назад
        </button>
        <h1 className="tryon-page__title">Примерка</h1>
        <button className="tryon-page__link" onClick={goToProfileWithNav}>
          Профиль
        </button>
      </header>

      <div className="tryon-page__content">
        <section className="tryon-card tryon-card--meta">
          <div className="tryon-meta">
            <span className="tryon-meta__label">Бренд</span>
            <span className="tryon-meta__value">{outfit.brand}</span>
          </div>
          <div className="tryon-meta">
            <span className="tryon-meta__label">Тип</span>
            <span className="tryon-meta__value">{outfit.type}</span>
          </div>
          <div className="tryon-meta">
            <span className="tryon-meta__label">Цена</span>
            <span className="tryon-meta__value">{outfit.price}</span>
          </div>
        </section>

        <section className="tryon-grid">
          <article className="tryon-card">
            <div className="tryon-card__head">
              <h2>Фото из профиля</h2>
              <span className="tryon-badge">
                {profileInfo.count > 0 ? `Основное ${profileInfo.index + 1}/${profileInfo.count}` : 'Не выбрано'}
              </span>
            </div>
            {profileModelPhoto ? (
              <img className="tryon-photo" src={profileModelPhoto} alt="Фото пользователя" />
            ) : (
              <div className="tryon-empty">Добавьте фото в профиле и отметьте его как основное</div>
            )}
          </article>

          <article className="tryon-card">
            <div className="tryon-card__head">
              <h2>Одежда</h2>
              <span className="tryon-badge tryon-badge--source">{clothSourceLabel}</span>
            </div>
            {clothPreview ? (
              <img className="tryon-photo tryon-photo--cloth" src={clothPreview} alt="Фото одежды" />
            ) : (
              <div className="tryon-empty">Откройте примерку из ленты или загрузите фото одежды вручную</div>
            )}
          </article>
        </section>

        <section className="tryon-actions">
          <button className="tryon-btn tryon-btn--secondary" onClick={goToProfileWithNav}>
            Выбрать фото в профиле
          </button>
          <button className="tryon-btn tryon-btn--secondary" onClick={handlePickClothPhoto}>
            Загрузить одежду
          </button>
          <button className="tryon-btn tryon-btn--primary" onClick={handleTryOn} disabled={isProcessing}>
            {isProcessing ? 'Создаем образ...' : 'Запустить примерку'}
          </button>
        </section>

        {error && <div className="tryon-alert tryon-alert--error">{error}</div>}

        {isProcessing && (
          <section className="tryon-card tryon-card--status">
            <div className="tryon-loader" />
            <p className="tryon-status-title">Создаем вашу примерку</p>
            <p className="tryon-status-subtitle">
              {INFERENCE_STEPS[activeStepIndex]} · {elapsedSeconds}с
            </p>
            <div className="tryon-progress">
              <div className="tryon-progress__bar" style={{ width: `${progress}%` }} />
            </div>
            <div className="tryon-steps">
              {INFERENCE_STEPS.map((step, index) => (
                <div
                  key={step}
                  className={`tryon-step ${index <= activeStepIndex ? 'is-active' : ''}`}
                >
                  {step}
                </div>
              ))}
            </div>
          </section>
        )}

        {resultImage && !isProcessing && (
          <section className="tryon-card tryon-card--result">
            <h2>Результат примерки</h2>
            <img className="tryon-result-image" src={resultImage} alt="Результат примерки" />
            <div className="tryon-result-actions">
              <button className="tryon-btn tryon-btn--secondary" onClick={handleSaveResult}>
                Сохранить
              </button>
              <button className="tryon-btn tryon-btn--secondary" onClick={handleShare}>
                Поделиться
              </button>
              <button className="tryon-btn tryon-btn--primary" onClick={() => setResultImage('')}>
                Новая примерка
              </button>
            </div>
          </section>
        )}

        <input
          ref={clothInputRef}
          type="file"
          accept="image/*"
          style={{ display: 'none' }}
          onChange={handleClothChange}
        />
      </div>
    </div>
  );
};

export default TryOnPage;
