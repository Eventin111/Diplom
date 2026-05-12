import { createApiUserRepository } from './apiUserRepository';

const okResponse = (payload) => ({
  ok: true,
  status: 200,
  json: jest.fn().mockResolvedValue(payload),
  text: jest.fn().mockResolvedValue('')
});

const errorResponse = ({ status = 400, payload = { detail: 'Ошибка запроса' }, text = 'Ошибка запроса' } = {}) => ({
  ok: false,
  status,
  json: jest.fn().mockResolvedValue(payload),
  text: jest.fn().mockResolvedValue(text)
});

describe('apiUserRepository', () => {
  beforeEach(() => {
    localStorage.clear();
    global.fetch = jest.fn();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('loads public profile and attaches auth token when present', async () => {
    localStorage.setItem('swipelt_token', 'token');
    global.fetch.mockResolvedValueOnce(okResponse({ username: 'john' }));
    const repository = createApiUserRepository();

    await expect(repository.fetchPublicProfile('john', { limit: 5 })).resolves.toEqual({ username: 'john' });
    expect(global.fetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/users/john/profile?limit=5',
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: 'Bearer token'
        })
      })
    );
  });

  it('works without token and encodes username in urls', async () => {
    global.fetch.mockResolvedValueOnce(okResponse({ ok: true }));
    const repository = createApiUserRepository();

    await expect(repository.followUser('имя user')).resolves.toEqual({ ok: true });
    expect(global.fetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/users/%D0%B8%D0%BC%D1%8F%20user/follow',
      expect.objectContaining({
        method: 'POST',
        headers: {}
      })
    );
  });

  it('unfollows user and normalizes following query parameters', async () => {
    global.fetch
      .mockResolvedValueOnce(okResponse({ ok: true }))
      .mockResolvedValueOnce(okResponse({ items: [] }));
    const repository = createApiUserRepository();

    await expect(repository.unfollowUser('alex')).resolves.toEqual({ ok: true });
    await expect(repository.fetchUserFollowing('alex', { skip: -12, limit: 0 })).resolves.toEqual({ items: [] });

    expect(global.fetch).toHaveBeenNthCalledWith(
      1,
      'http://localhost:8000/api/v1/users/alex/follow',
      expect.objectContaining({ method: 'DELETE' })
    );
    expect(global.fetch).toHaveBeenNthCalledWith(
      2,
      'http://localhost:8000/api/v1/users/alex/following?skip=0&limit=1',
      expect.any(Object)
    );
  });

  it('surfaces json and text backend errors', async () => {
    global.fetch
      .mockResolvedValueOnce(errorResponse({ text: JSON.stringify({ detail: 'cannot follow' }) }))
      .mockResolvedValueOnce(errorResponse({ text: 'server overloaded' }));
    const repository = createApiUserRepository();

    await expect(repository.followUser('alex')).rejects.toThrow('cannot follow');
    await expect(repository.followUser('alex')).rejects.toThrow('server overloaded');
  });

  it('uses default error message when backend detail is empty', async () => {
    global.fetch.mockResolvedValueOnce(errorResponse({ text: '' }));
    const repository = createApiUserRepository();

    await expect(repository.followUser('alex')).rejects.toThrow('Ошибка запроса');
  });
});
