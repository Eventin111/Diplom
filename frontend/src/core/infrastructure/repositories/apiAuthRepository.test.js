import { createApiAuthRepository } from './apiAuthRepository';

const createMemoryStorage = () => {
  const store = new Map();
  return {
    getItem(key) {
      return store.has(key) ? store.get(key) : null;
    },
    setItem(key, value) {
      store.set(key, value);
    },
    removeItem(key) {
      store.delete(key);
    }
  };
};

const authStorageKeys = {
  token: 'swipelt_token',
  user: 'swipelt_user',
  guestFlag: 'swipelt_is_guest'
};

const createConfig = () => ({
  authStorageKeys
});

const okResponse = (payload, status = 200) => ({
  ok: true,
  status,
  json: jest.fn().mockResolvedValue(payload),
  text: jest.fn().mockResolvedValue('')
});

const errorResponse = (payload, asJson = true) => ({
  ok: false,
  status: 400,
  json: asJson ? jest.fn().mockResolvedValue(payload) : jest.fn().mockRejectedValue(new Error('bad json')),
  text: jest.fn().mockResolvedValue(typeof payload === 'string' ? payload : JSON.stringify(payload))
});

describe('apiAuthRepository', () => {
  beforeEach(() => {
    global.fetch = jest.fn();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('returns empty session when token is missing', async () => {
    const storage = createMemoryStorage();
    const repository = createApiAuthRepository({ storage, config: createConfig() });

    await expect(repository.initializeSession()).resolves.toEqual({ token: null, user: null });
    expect(global.fetch).not.toHaveBeenCalled();
  });

  it('clears legacy tokens during initialization', async () => {
    const storage = createMemoryStorage();
    storage.setItem(authStorageKeys.token, 'mock-jwt-token-1');
    storage.setItem(authStorageKeys.user, '{"id":1}');
    storage.setItem(authStorageKeys.guestFlag, 'true');

    const repository = createApiAuthRepository({ storage, config: createConfig() });

    await expect(repository.initializeSession()).resolves.toEqual({ token: null, user: null });
    expect(storage.getItem(authStorageKeys.token)).toBeNull();
    expect(storage.getItem(authStorageKeys.user)).toBeNull();
    expect(storage.getItem(authStorageKeys.guestFlag)).toBeNull();
  });

  it('loads current user for a valid persisted token', async () => {
    const storage = createMemoryStorage();
    storage.setItem(authStorageKeys.token, 'real-token');
    global.fetch.mockResolvedValueOnce(
      okResponse({ id: 7, email: 'user@mail.com', username: 'user7', avatar_url: 'https://img.test/a.png' })
    );

    const repository = createApiAuthRepository({ storage, config: createConfig() });
    const result = await repository.initializeSession();

    expect(result.token).toBe('real-token');
    expect(result.user.email).toBe('user@mail.com');
    expect(storage.getItem(authStorageKeys.user)).toContain('user@mail.com');
    expect(global.fetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/auth/me',
      expect.objectContaining({
        headers: expect.any(Headers)
      })
    );
  });

  it('clears session when initialize request fails', async () => {
    const storage = createMemoryStorage();
    storage.setItem(authStorageKeys.token, 'bad-token');
    storage.setItem(authStorageKeys.user, '{"id":1}');
    global.fetch.mockResolvedValueOnce(errorResponse({ detail: 'Unauthorized' }));

    const repository = createApiAuthRepository({ storage, config: createConfig() });

    await expect(repository.initializeSession()).resolves.toEqual({ token: null, user: null });
    expect(storage.getItem(authStorageKeys.token)).toBeNull();
    expect(storage.getItem(authStorageKeys.user)).toBeNull();
  });

  it('logs in and persists token with user', async () => {
    const storage = createMemoryStorage();
    global.fetch
      .mockResolvedValueOnce(okResponse({ access_token: 'api-token' }))
      .mockResolvedValueOnce(
        okResponse({ id: 2, email: 'user@mail.com', username: 'user2', avatar_url: 'https://img.test/u2.png' })
      );

    const repository = createApiAuthRepository({ storage, config: createConfig() });
    const result = await repository.login({ email: ' user@mail.com ', password: 'secret' });

    expect(result.token).toBe('api-token');
    expect(result.user.username).toBe('user2');
    expect(storage.getItem(authStorageKeys.token)).toBe('api-token');
    expect(global.fetch).toHaveBeenNthCalledWith(
      1,
      'http://localhost:8000/api/v1/auth/login',
      expect.objectContaining({
        method: 'POST',
        body: expect.any(URLSearchParams)
      })
    );
  });

  it('registers and then logs in', async () => {
    const storage = createMemoryStorage();
    global.fetch
      .mockResolvedValueOnce(okResponse({}, 200))
      .mockResolvedValueOnce(okResponse({ access_token: 'reg-token' }))
      .mockResolvedValueOnce(
        okResponse({ id: 3, email: 'new@mail.com', username: 'newuser', avatar_url: 'https://img.test/u3.png' })
      );

    const repository = createApiAuthRepository({ storage, config: createConfig() });
    const result = await repository.register({
      email: 'new@mail.com',
      password: 'secret',
      username: 'newuser'
    });

    expect(result.token).toBe('reg-token');
    expect(result.user.email).toBe('new@mail.com');
    expect(global.fetch).toHaveBeenCalledTimes(3);
  });

  it('updates profile and persists the returned user', async () => {
    const storage = createMemoryStorage();
    storage.setItem(authStorageKeys.token, 'api-token');
    global.fetch.mockResolvedValueOnce(
      okResponse({ id: 2, email: 'user@mail.com', username: 'updated', avatar_url: 'https://img.test/new.png' })
    );

    const repository = createApiAuthRepository({ storage, config: createConfig() });
    const user = await repository.updateProfile({ username: 'updated', avatar: 'https://img.test/new.png' });

    expect(user.username).toBe('updated');
    expect(user.avatar).toBe('https://img.test/new.png');
    expect(storage.getItem(authStorageKeys.user)).toContain('updated');
    expect(global.fetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/auth/me',
      expect.objectContaining({
        method: 'PATCH',
        body: JSON.stringify({ username: 'updated', avatar_url: 'https://img.test/new.png' })
      })
    );
  });

  it('clears stored session on logout', () => {
    const storage = createMemoryStorage();
    storage.setItem(authStorageKeys.token, 'api-token');
    storage.setItem(authStorageKeys.user, '{"id":2}');
    storage.setItem(authStorageKeys.guestFlag, 'false');

    const repository = createApiAuthRepository({ storage, config: createConfig() });
    repository.logout();

    expect(storage.getItem(authStorageKeys.token)).toBeNull();
    expect(storage.getItem(authStorageKeys.user)).toBeNull();
    expect(storage.getItem(authStorageKeys.guestFlag)).toBeNull();
  });
});
