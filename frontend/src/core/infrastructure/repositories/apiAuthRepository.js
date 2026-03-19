import { appConfig } from '../../../config/appConfig';
import { createUserEntity } from '../../domain/entities/userEntity';
import { createBrowserStorage } from '../storage/browserStorage';

const buildUrl = (path) => `${appConfig.apiBaseUrl}/api/v1${path}`;

export const createApiAuthRepository = (deps = {}) => {
  const storage = deps.storage || createBrowserStorage();
  const config = deps.config || appConfig;
  const keys = config.authStorageKeys;
  const legacyTokenPrefixes = ['mock-jwt-token', 'user-token-', 'guest-token-'];

  const persistSession = (token, user) => {
    storage.setItem(keys.token, token);
    storage.setItem(keys.user, JSON.stringify(user));
    storage.setItem(keys.guestFlag, 'false');
  };

  const clearSession = () => {
    storage.removeItem(keys.token);
    storage.removeItem(keys.user);
    storage.removeItem(keys.guestFlag);
  };

  const getToken = () => storage.getItem(keys.token);
  const isLegacyToken = (token) =>
    legacyTokenPrefixes.some((prefix) => String(token || '').startsWith(prefix));

  const fetchJson = async (path, init = {}) => {
    const token = getToken();
    const headers = new Headers(init.headers || {});

    if (token) {
      headers.set('Authorization', `Bearer ${token}`);
    }

    const response = await fetch(buildUrl(path), {
      ...init,
      headers
    });

    if (!response.ok) {
      let detail = 'Request failed';
      try {
        const payload = await response.json();
        detail = payload?.detail || JSON.stringify(payload);
      } catch (error) {
        detail = await response.text();
      }

      throw new Error(detail || 'Request failed');
    }

    if (response.status === 204) {
      return null;
    }

    return response.json();
  };

  return {
    async initializeSession() {
      const token = getToken();

      if (!token) {
        clearSession();
        return { token: null, user: null };
      }

       if (isLegacyToken(token)) {
        clearSession();
        return { token: null, user: null };
      }

      try {
        const userPayload = await fetchJson('/auth/me');
        const user = createUserEntity(userPayload);
        persistSession(token, user);
        return { token, user };
      } catch (error) {
        clearSession();
        return { token: null, user: null };
      }
    },

    async login({ email, password }) {
      const body = new URLSearchParams({
        username: String(email || '').trim(),
        password: String(password || '')
      });

      const tokenPayload = await fetchJson('/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        body
      });

      storage.setItem(keys.token, tokenPayload.access_token);
      const userPayload = await fetchJson('/auth/me');
      const user = createUserEntity(userPayload);
      persistSession(tokenPayload.access_token, user);
      return { token: tokenPayload.access_token, user };
    },

    async register({ email, password, username }) {
      await fetchJson('/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, password, username })
      });

      return this.login({ email, password });
    },

    async updateProfile(partialUser) {
      const payload = {};

      if (partialUser.email) {
        payload.email = partialUser.email;
      }
      if (partialUser.username) {
        payload.username = partialUser.username;
      }
      if (partialUser.avatar || partialUser.avatar_url) {
        payload.avatar_url = partialUser.avatar || partialUser.avatar_url;
      }

      const userPayload = await fetchJson('/auth/me', {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      const token = getToken();
      const user = createUserEntity(userPayload);
      if (token) {
        persistSession(token, user);
      }
      return user;
    },

    logout() {
      clearSession();
    }
  };
};
