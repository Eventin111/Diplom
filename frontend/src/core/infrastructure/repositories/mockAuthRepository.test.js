import { createMockAuthRepository } from './mockAuthRepository';

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

describe('mockAuthRepository', () => {
  it('returns empty session for missing data', () => {
    const repository = createMockAuthRepository({ storage: createMemoryStorage() });
    expect(repository.initializeSession()).toEqual({ token: null, user: null });
  });

  it('logs in demo account', () => {
    const repository = createMockAuthRepository({ storage: createMemoryStorage() });
    const session = repository.login({ email: 'test@mail.ru', password: '123123' });

    expect(session.token).toBe('mock-jwt-token');
    expect(session.user.email).toBe('test@mail.ru');
  });

  it('logs in guest by guest email', () => {
    const repository = createMockAuthRepository({ storage: createMemoryStorage() });
    const session = repository.login({ email: 'guest@swipelt.com', password: 'guest123' });

    expect(session.user.isGuest).toBe(true);
  });

  it('logs in registered user', () => {
    const storage = createMemoryStorage();
    const repository = createMockAuthRepository({ storage });

    repository.register({
      email: 'user@mail.com',
      password: '123456',
      username: 'user1'
    });

    const session = repository.login({
      email: 'user@mail.com',
      password: '123456'
    });

    expect(session.user.username).toBe('user1');
  });

  it('registers and then logs in new user', () => {
    const storage = createMemoryStorage();
    const repository = createMockAuthRepository({ storage });

    const registration = repository.register({
      email: 'new@mail.com',
      password: '123456',
      username: 'newuser'
    });

    expect(registration.user.username).toBe('newuser');
    const session = repository.initializeSession();
    expect(session.user.email).toBe('new@mail.com');
  });

  it('throws on duplicate email', () => {
    const storage = createMemoryStorage();
    const repository = createMockAuthRepository({ storage });

    repository.register({
      email: 'dup@mail.com',
      password: '123456',
      username: 'dupuser'
    });

    expect(() =>
      repository.register({
        email: 'dup@mail.com',
        password: '123456',
        username: 'dupuser2'
      })
    ).toThrow('Пользователь с таким email уже существует');
  });

  it('throws on duplicate username', () => {
    const storage = createMemoryStorage();
    const repository = createMockAuthRepository({ storage });

    repository.register({
      email: 'user1@mail.com',
      password: '123456',
      username: 'same'
    });

    expect(() =>
      repository.register({
        email: 'user2@mail.com',
        password: '123456',
        username: 'same'
      })
    ).toThrow('Имя пользователя уже занято');
  });

  it('throws on invalid credentials', () => {
    const repository = createMockAuthRepository({ storage: createMemoryStorage() });
    expect(() => repository.login({ email: 'wrong@mail.com', password: '123456' })).toThrow(
      'Неверный email или пароль'
    );
  });

  it('clears malformed persisted session', () => {
    const storage = createMemoryStorage();
    storage.setItem('swipelt_token', 'token');
    storage.setItem('swipelt_user', '{invalid');

    const repository = createMockAuthRepository({ storage });
    expect(repository.initializeSession()).toEqual({ token: null, user: null });
  });

  it('clears session on logout', () => {
    const repository = createMockAuthRepository({ storage: createMemoryStorage() });
    repository.login({ email: 'test@mail.ru', password: '123123' });
    repository.logout();

    const session = repository.initializeSession();
    expect(session).toEqual({ token: null, user: null });
  });
});
