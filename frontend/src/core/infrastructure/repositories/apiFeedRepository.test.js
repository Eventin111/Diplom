import { createApiFeedRepository } from './apiFeedRepository';

const okResponse = (payload, status = 200) => ({
  ok: true,
  status,
  json: jest.fn().mockResolvedValue(payload),
  text: jest.fn().mockResolvedValue('')
});

const errorResponse = ({ payload = { detail: 'Ошибка запроса' }, text = 'Ошибка запроса', jsonFails = false } = {}) => ({
  ok: false,
  status: 400,
  json: jsonFails ? jest.fn().mockRejectedValue(new Error('bad json')) : jest.fn().mockResolvedValue(payload),
  text: jest.fn().mockResolvedValue(text)
});

describe('apiFeedRepository', () => {
  beforeEach(() => {
    localStorage.clear();
    global.fetch = jest.fn();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('requires auth token for feed requests', async () => {
    const repository = createApiFeedRepository();

    await expect(repository.fetchLikedFeedIds()).rejects.toThrow('Нужно войти в аккаунт.');
    expect(global.fetch).not.toHaveBeenCalled();
  });

  it('returns liked feed ids and normalizes missing items to empty array', async () => {
    localStorage.setItem('swipelt_token', 'token');
    global.fetch
      .mockResolvedValueOnce(okResponse({ items: [11, 12] }))
      .mockResolvedValueOnce(okResponse({}));
    const repository = createApiFeedRepository();

    await expect(repository.fetchLikedFeedIds()).resolves.toEqual([11, 12]);
    await expect(repository.fetchLikedFeedIds()).resolves.toEqual([]);
    expect(global.fetch).toHaveBeenNthCalledWith(
      1,
      'http://localhost:8000/api/v1/feed/liked-ids',
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: 'Bearer token'
        })
      })
    );
  });

  it('returns feed items with stats from feed endpoint', async () => {
    localStorage.setItem('swipelt_token', 'token');
    global.fetch.mockResolvedValueOnce(okResponse({ items: [{ id: 1, likes_count: 3, comments_count: 0, is_liked: true }] }));
    const repository = createApiFeedRepository();

    await expect(repository.fetchFeedItems({ skip: 0, limit: 5 })).resolves.toEqual([
      { id: 1, likes_count: 3, comments_count: 0, is_liked: true }
    ]);
    expect(global.fetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/feed/?skip=0&limit=5',
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: 'Bearer token'
        })
      })
    );
  });

  it('sends like and unlike requests with proper methods', async () => {
    localStorage.setItem('swipelt_token', 'token');
    global.fetch
      .mockResolvedValueOnce(okResponse({ ok: true }))
      .mockResolvedValueOnce(okResponse(null, 204));
    const repository = createApiFeedRepository();

    await expect(repository.likeFeedItem(9)).resolves.toEqual({ ok: true });
    await expect(repository.unlikeFeedItem(9)).resolves.toBeNull();

    expect(global.fetch).toHaveBeenNthCalledWith(
      1,
      'http://localhost:8000/api/v1/feed/9/like',
      expect.objectContaining({ method: 'POST' })
    );
    expect(global.fetch).toHaveBeenNthCalledWith(
      2,
      'http://localhost:8000/api/v1/feed/9/like',
      expect.objectContaining({ method: 'DELETE' })
    );
  });

  it('surfaces response text when json parsing fails', async () => {
    localStorage.setItem('swipelt_token', 'token');
    global.fetch.mockResolvedValueOnce(errorResponse({ text: 'feed text error', jsonFails: true }));
    const repository = createApiFeedRepository();

    await expect(repository.likeFeedItem(5)).rejects.toThrow('feed text error');
  });
});
