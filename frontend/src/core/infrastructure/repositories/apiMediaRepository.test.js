import { createApiMediaRepository } from './apiMediaRepository';

const okResponse = (payload) => ({
  ok: true,
  status: 200,
  json: jest.fn().mockResolvedValue(payload),
  text: jest.fn().mockResolvedValue('')
});

const errorResponse = ({ payload = { detail: 'Ошибка загрузки файла' }, text = 'Ошибка загрузки файла', jsonFails = false } = {}) => ({
  ok: false,
  status: 400,
  json: jsonFails ? jest.fn().mockRejectedValue(new Error('bad json')) : jest.fn().mockResolvedValue(payload),
  text: jest.fn().mockResolvedValue(text)
});

describe('apiMediaRepository', () => {
  beforeEach(() => {
    localStorage.clear();
    global.fetch = jest.fn();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('requires auth token before upload', async () => {
    const repository = createApiMediaRepository();

    await expect(repository.uploadMedia(new File(['x'], 'x.png', { type: 'image/png' }))).rejects.toThrow(
      'Нужно войти в аккаунт, чтобы загружать файлы.'
    );
  });

  it('uploads media and normalizes returned urls', async () => {
    localStorage.setItem('swipelt_token', 'token');
    global.fetch.mockResolvedValueOnce(
      okResponse({
        upload_url: '/uploads/result.png',
        media: {
          id: 3,
          public_url: 'media/item.png'
        }
      })
    );
    const repository = createApiMediaRepository();

    await expect(repository.uploadMedia(new File(['x'], 'x.png', { type: 'image/png' }))).resolves.toEqual({
      upload_url: 'http://localhost:8000/uploads/result.png',
      media: {
        id: 3,
        public_url: 'http://localhost:8000/media/item.png'
      }
    });

    expect(global.fetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/media/upload',
      expect.objectContaining({
        method: 'POST',
        headers: expect.objectContaining({
          Authorization: 'Bearer token'
        }),
        body: expect.any(FormData)
      })
    );
  });

  it('preserves absolute and data urls from the backend payload', async () => {
    localStorage.setItem('swipelt_token', 'token');
    global.fetch.mockResolvedValueOnce(
      okResponse({
        upload_url: 'https://cdn.example.com/result.png',
        media: {
          id: 8,
          public_url: 'data:image/png;base64,abc'
        }
      })
    );
    const repository = createApiMediaRepository();

    await expect(repository.uploadMedia(new File(['x'], 'x.png', { type: 'image/png' }))).resolves.toEqual({
      upload_url: 'https://cdn.example.com/result.png',
      media: {
        id: 8,
        public_url: 'data:image/png;base64,abc'
      }
    });
  });

  it('surfaces text fallback when upload error payload is not json', async () => {
    localStorage.setItem('swipelt_token', 'token');
    global.fetch.mockResolvedValueOnce(errorResponse({ text: 'upload failed', jsonFails: true }));
    const repository = createApiMediaRepository();

    await expect(repository.uploadMedia(new File(['x'], 'x.png', { type: 'image/png' }))).rejects.toThrow('upload failed');
  });

  it('loads current user media and normalizes public urls', async () => {
    localStorage.setItem('swipelt_token', 'token');
    global.fetch.mockResolvedValueOnce(
      okResponse([
        { id: 1, public_url: '/api/v1/media/1/file' },
        { id: 2, public_url: 'https://cdn.example.com/media/2.png' }
      ])
    );
    const repository = createApiMediaRepository();

    await expect(repository.fetchMyMedia()).resolves.toEqual([
      { id: 1, public_url: 'http://localhost:8000/api/v1/media/1/file' },
      { id: 2, public_url: 'https://cdn.example.com/media/2.png' }
    ]);
    expect(global.fetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/media/mine',
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: 'Bearer token'
        })
      })
    );
  });

  it('deletes media through the api', async () => {
    localStorage.setItem('swipelt_token', 'token');
    global.fetch.mockResolvedValueOnce({
      ok: true,
      status: 204,
      json: jest.fn(),
      text: jest.fn()
    });
    const repository = createApiMediaRepository();

    await expect(repository.deleteMedia(15)).resolves.toBeNull();
    expect(global.fetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/media/15',
      expect.objectContaining({
        method: 'DELETE',
        headers: expect.objectContaining({
          Authorization: 'Bearer token'
        })
      })
    );
  });
});
