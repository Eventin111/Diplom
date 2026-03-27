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
});
