import { appConfig } from '../../../config/appConfig';

const getAuthToken = () => localStorage.getItem(appConfig.authStorageKeys.token);

const normalizeUrl = (url) => {
  if (!url) {
    return '';
  }

  if (/^https?:\/\//i.test(url) || url.startsWith('data:')) {
    return url;
  }

  if (url.startsWith('/')) {
    return `${appConfig.apiBaseUrl}${url}`;
  }

  return `${appConfig.apiBaseUrl}/${url}`;
};

export const createApiMediaRepository = () => ({
  async uploadMedia(file) {
    const token = getAuthToken();
    if (!token) {
      throw new Error('Нужно войти в аккаунт, чтобы загружать файлы.');
    }

    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${appConfig.apiBaseUrl}/api/v1/media/upload`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`
      },
      body: formData
    });

    if (!response.ok) {
      let detail = 'Ошибка загрузки файла';
      try {
        const payload = await response.json();
        detail = payload?.detail || JSON.stringify(payload);
      } catch (error) {
        detail = await response.text();
      }
      throw new Error(detail || 'Ошибка загрузки файла');
    }

    const payload = await response.json();

    return {
      ...payload,
      upload_url: normalizeUrl(payload.upload_url),
      media: payload.media
        ? {
            ...payload.media,
            public_url: normalizeUrl(payload.media.public_url)
          }
        : payload.media
    };
  }
});

