import { appConfig } from '../../../config/appConfig';
import { createUserEntity, sanitizeUserEntity } from '../../domain/entities/userEntity';
import { isGuestEmail } from '../../domain/services/authPolicy';
import { createBrowserStorage } from '../storage/browserStorage';

const createToken = (prefix = 'token') => `${prefix}-${Date.now()}`;

const parseJson = (raw, fallback) => {
  if (!raw) {
    return fallback;
  }

  try {
    return JSON.parse(raw);
  } catch (error) {
    return fallback;
  }
};

export const createMockAuthRepository = (deps = {}) => {
  const storage = deps.storage || createBrowserStorage();
  const config = deps.config || appConfig;
  const keys = config.authStorageKeys;

  const persistSession = (token, user) => {
    storage.setItem(keys.token, token);
    storage.setItem(keys.user, JSON.stringify(user));
    storage.setItem(keys.guestFlag, String(Boolean(user.isGuest)));
  };

  const clearSession = () => {
    storage.removeItem(keys.token);
    storage.removeItem(keys.user);
    storage.removeItem(keys.guestFlag);
  };

  return {
    initializeSession() {
      const token = storage.getItem(keys.token);
      const rawUser = storage.getItem(keys.user);
      const parsedUser = sanitizeUserEntity(parseJson(rawUser, null));

      if (!token || !parsedUser) {
        clearSession();
        return { token: null, user: null };
      }

      return { token, user: parsedUser };
    },

    login({ email, password }) {
      const normalizedEmail = String(email || '').trim().toLowerCase();
      const users = parseJson(storage.getItem(keys.registeredUsers), []);

      if (
        normalizedEmail === config.demoAccount.email.toLowerCase() &&
        password === config.demoAccount.password
      ) {
        const user = createUserEntity({
          id: 1,
          email: config.demoAccount.email,
          username: config.demoAccount.username
        });
        const token = 'mock-jwt-token';
        persistSession(token, user);
        return { token, user };
      }

      if (
        normalizedEmail === config.guestAccount.email.toLowerCase() ||
        isGuestEmail(normalizedEmail)
      ) {
        const guest = createUserEntity({
          id: Date.now(),
          email: config.guestAccount.email,
          username: config.guestAccount.username,
          isGuest: true
        });
        const token = createToken('guest-token');
        persistSession(token, guest);
        return { token, user: guest };
      }

      const existing = users.find(
        (item) =>
          String(item.email || '').toLowerCase() === normalizedEmail && item.password === password
      );

      if (!existing) {
        throw new Error('Неверный email или пароль');
      }

      const user = createUserEntity(existing);
      const token = createToken('user-token');
      persistSession(token, user);
      return { token, user };
    },

    register({ email, password, username }) {
      const normalizedEmail = String(email || '').trim().toLowerCase();
      const normalizedUsername = String(username || '').trim();
      const users = parseJson(storage.getItem(keys.registeredUsers), []);

      if (users.some((item) => String(item.email || '').toLowerCase() === normalizedEmail)) {
        throw new Error('Пользователь с таким email уже существует');
      }

      if (users.some((item) => String(item.username || '').toLowerCase() === normalizedUsername.toLowerCase())) {
        throw new Error('Имя пользователя уже занято');
      }

      const newUser = createUserEntity({
        id: Date.now(),
        email: normalizedEmail,
        username: normalizedUsername
      });

      users.push({
        ...newUser,
        password
      });
      storage.setItem(keys.registeredUsers, JSON.stringify(users));

      const token = createToken('user-token');
      persistSession(token, newUser);
      return { token, user: newUser };
    },

    logout() {
      clearSession();
    }
  };
};

