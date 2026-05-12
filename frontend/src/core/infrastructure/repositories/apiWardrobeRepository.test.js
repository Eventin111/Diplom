import { createApiWardrobeRepository } from './apiWardrobeRepository';

const okResponse = (payload, status = 200) => ({
  ok: true,
  status,
  json: jest.fn().mockResolvedValue(payload),
  text: jest.fn().mockResolvedValue('')
});

const errorResponse = ({ status = 400, payload = { detail: 'Ошибка запроса' }, text = 'Ошибка запроса' } = {}) => ({
  ok: false,
  status,
  json: jest.fn().mockResolvedValue(payload),
  text: jest.fn().mockResolvedValue(text)
});

describe('apiWardrobeRepository', () => {
  beforeEach(() => {
    localStorage.clear();
    global.fetch = jest.fn();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('requires auth token for wardrobe endpoints', async () => {
    const repository = createApiWardrobeRepository();

    await expect(repository.fetchWardrobeItems()).rejects.toThrow('Нужно войти в аккаунт.');
    expect(global.fetch).not.toHaveBeenCalled();
  });

  it('loads wardrobe items and saved garment ids', async () => {
    localStorage.setItem('swipelt_token', 'token');
    global.fetch
      .mockResolvedValueOnce(okResponse({ items: [{ id: 1 }] }))
      .mockResolvedValueOnce(okResponse({}))
      .mockResolvedValueOnce(okResponse({ items: [11, 12] }));
    const repository = createApiWardrobeRepository();

    await expect(repository.fetchWardrobeItems({ skip: 3, limit: 5 })).resolves.toEqual([{ id: 1 }]);
    await expect(repository.fetchWardrobeItems({ skip: 3, limit: 5 })).resolves.toEqual([]);
    await expect(repository.fetchSavedGarmentIds()).resolves.toEqual([11, 12]);

    expect(global.fetch).toHaveBeenNthCalledWith(
      1,
      'http://localhost:8000/api/v1/wardrobe/?skip=3&limit=5',
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: 'Bearer token'
        })
      })
    );
  });

  it('saves garment from post and deletes by garment id', async () => {
    localStorage.setItem('swipelt_token', 'token');
    global.fetch
      .mockResolvedValueOnce(okResponse({ id: 9 }))
      .mockResolvedValueOnce(okResponse(null, 204));
    const repository = createApiWardrobeRepository();

    await expect(
      repository.saveFromPost({
        postId: 22,
        title: 'T-shirt',
        brand: 'Swipelt',
        imageUrl: 'https://cdn/img.jpg',
        category: 'upper',
        price: 100
      })
    ).resolves.toEqual({ id: 9 });

    await expect(repository.removeByGarmentId(22)).resolves.toBeNull();

    expect(global.fetch).toHaveBeenNthCalledWith(
      1,
      'http://localhost:8000/api/v1/wardrobe/',
      expect.objectContaining({
        method: 'POST',
        headers: expect.objectContaining({
          'Content-Type': 'application/json'
        })
      })
    );
    expect(global.fetch).toHaveBeenNthCalledWith(
      2,
      'http://localhost:8000/api/v1/wardrobe/22',
      expect.objectContaining({ method: 'DELETE' })
    );
  });

  it('surfaces json and text backend errors', async () => {
    localStorage.setItem('swipelt_token', 'token');
    global.fetch
      .mockResolvedValueOnce(errorResponse({ text: JSON.stringify({ detail: 'not allowed' }) }))
      .mockResolvedValueOnce(errorResponse({ text: 'wardrobe unavailable' }));
    const repository = createApiWardrobeRepository();

    await expect(repository.fetchSavedGarmentIds()).rejects.toThrow('not allowed');
    await expect(repository.fetchSavedGarmentIds()).rejects.toThrow('wardrobe unavailable');
  });
});
