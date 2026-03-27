import { appConfig } from '../../../config/appConfig';

const getAuthToken = () => localStorage.getItem(appConfig.authStorageKeys.token);

const request = async (path, init = {}) => {
  const token = getAuthToken();
  if (!token) {
    throw new Error('Нужно войти в аккаунт.');
  }

  const response = await fetch(`${appConfig.apiBaseUrl}/api/v1/feed${path}`, {
    ...init,
    headers: {
      ...(init.headers || {}),
      Authorization: `Bearer ${token}`
    }
  });

  if (!response.ok) {
    let detail = 'Ошибка запроса';
    try {
      const payload = await response.json();
      detail = payload?.detail || JSON.stringify(payload);
    } catch (error) {
      detail = await response.text();
    }
    throw new Error(detail || 'Ошибка запроса');
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
};

export const createApiFeedRepository = () => ({
  async fetchLikedFeedIds() {
    const payload = await request('/liked-ids');
    return Array.isArray(payload?.items) ? payload.items : [];
  },

  async likeFeedItem(feedItemId) {
    return request(`/${feedItemId}/like`, { method: 'POST' });
  },

  async unlikeFeedItem(feedItemId) {
    return request(`/${feedItemId}/like`, { method: 'DELETE' });
  }
});

