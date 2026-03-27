import { createApiTryOnRepository } from './apiTryOnRepository';

const okResponse = (payload, extras = {}) => ({
  ok: true,
  status: 200,
  json: jest.fn().mockResolvedValue(payload),
  text: jest.fn().mockResolvedValue(''),
  blob: jest.fn(),
  ...extras
});

const errorResponse = ({ status = 400, payload = { detail: 'Ошибка' }, text = 'Ошибка', jsonFails = false } = {}) => ({
  ok: false,
  status,
  json: jsonFails ? jest.fn().mockRejectedValue(new Error('bad json')) : jest.fn().mockResolvedValue(payload),
  text: jest.fn().mockResolvedValue(text)
});

class MockWebSocket {
  static instances = [];

  constructor(url) {
    this.url = url;
    MockWebSocket.instances.push(this);
  }
}

describe('apiTryOnRepository', () => {
  beforeEach(() => {
    localStorage.clear();
    global.fetch = jest.fn();
    global.WebSocket = MockWebSocket;
    MockWebSocket.instances = [];
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('submits try-on request with files and auth token', async () => {
    localStorage.setItem('swipelt_token', 'token');
    global.fetch.mockResolvedValueOnce(
      okResponse({
        session_id: 21,
        queued: true,
        results: ['https://cdn.example.com/result.jpg'],
        status: 'queued'
      })
    );
    const repository = createApiTryOnRepository();

    const payload = await repository.runTryOn({
      modelImage: new File(['model'], 'model.png', { type: 'image/png' }),
      clothImage: new File(['cloth'], 'cloth.jpg', { type: 'image/jpeg' }),
      modelType: 'hd',
      category: 1,
      scale: 2.5,
      numSteps: 8,
      numSamples: 2,
      seed: 99
    });

    expect(payload).toEqual(
      expect.objectContaining({
        sessionId: 21,
        queued: true,
        resultUrl: 'https://cdn.example.com/result.jpg',
        status: 'queued'
      })
    );
    expect(global.fetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/tryon/try-on',
      expect.objectContaining({
        method: 'POST',
        headers: expect.objectContaining({
          Authorization: 'Bearer token'
        }),
        body: expect.any(FormData)
      })
    );
  });

  it('supports string and blob image inputs', async () => {
    const sourceBlob = new Blob(['image'], { type: 'image/png' });
    global.fetch
      .mockResolvedValueOnce(
        okResponse(null, {
          blob: jest.fn().mockResolvedValue(sourceBlob)
        })
      )
      .mockResolvedValueOnce(
        okResponse({
          session_id: 33,
          queued: false,
          result_image_url: '/media/tryon/result.png',
          success: true
        })
      );
    const repository = createApiTryOnRepository();

    const payload = await repository.runTryOn({
      modelImage: 'https://example.com/model.png',
      clothImage: new Blob(['cloth'], { type: 'image/jpeg' })
    });

    expect(payload.sessionId).toBe(33);
    expect(payload.resultUrl).toBe('/media/tryon/result.png');
    expect(global.fetch).toHaveBeenNthCalledWith(1, 'https://example.com/model.png');
    expect(global.fetch).toHaveBeenNthCalledWith(
      2,
      'http://localhost:8000/api/v1/tryon/try-on',
      expect.objectContaining({ method: 'POST' })
    );
  });

  it('maps network TypeError to a friendly api message', async () => {
    global.fetch.mockRejectedValueOnce(new TypeError('Failed to fetch'));
    const repository = createApiTryOnRepository();

    await expect(
      repository.runTryOn({
        modelImage: new File(['model'], 'model.png', { type: 'image/png' }),
        clothImage: new File(['cloth'], 'cloth.jpg', { type: 'image/jpeg' })
      })
    ).rejects.toThrow('Сетевой доступ к API недоступен');
  });

  it('throws a detailed error when image source fetch fails', async () => {
    global.fetch.mockResolvedValueOnce(errorResponse({ status: 404, text: 'not found', jsonFails: true }));
    const repository = createApiTryOnRepository();

    await expect(
      repository.runTryOn({
        modelImage: 'https://example.com/missing.png',
        clothImage: new Blob(['cloth'], { type: 'image/jpeg' })
      })
    ).rejects.toThrow('Failed to fetch image source: 404');
  });

  it('rejects unsupported image input types', async () => {
    const repository = createApiTryOnRepository();

    await expect(repository.runTryOn({ modelImage: 123, clothImage: new Blob(['cloth'], { type: 'image/jpeg' }) })).rejects.toThrow(
      'Unsupported image input type'
    );
  });

  it('loads try-on session details and surfaces backend errors', async () => {
    global.fetch
      .mockResolvedValueOnce(okResponse({ id: 55, status: 'completed' }))
      .mockResolvedValueOnce(errorResponse({ status: 500, payload: { detail: 'boom' } }));
    const repository = createApiTryOnRepository();

    await expect(repository.getTryOnSession(55)).resolves.toEqual({ id: 55, status: 'completed' });
    await expect(repository.getTryOnSession(55)).rejects.toThrow('Try-on session request failed: 500 boom');
  });

  it('subscribes to websocket events and routes handlers', () => {
    localStorage.setItem('swipelt_token', 'token');
    const onMessage = jest.fn();
    const onError = jest.fn();
    const onClose = jest.fn();
    const repository = createApiTryOnRepository();

    const socket = repository.subscribeToTryOnSession(44, {
      onMessage,
      onError,
      onClose
    });

    expect(socket.url).toBe('ws://localhost:8000/api/v1/tryon/sessions/44/ws?token=token');

    socket.onmessage({ data: JSON.stringify({ status: 'queued' }) });
    socket.onmessage({ data: 'not-json' });
    socket.onerror({ type: 'error' });
    socket.onclose({ code: 1000 });

    expect(onMessage).toHaveBeenCalledWith({ status: 'queued' });
    expect(onError).toHaveBeenCalledTimes(2);
    expect(onClose).toHaveBeenCalledWith({ code: 1000 });
  });

  it('surfaces backend error details for failed try-on requests', async () => {
    global.fetch.mockResolvedValueOnce(errorResponse({ status: 422, payload: { detail: 'bad input' } }));
    const repository = createApiTryOnRepository();

    await expect(
      repository.runTryOn({
        modelImage: new File(['model'], 'model.png', { type: 'image/png' }),
        clothImage: new File(['cloth'], 'cloth.jpg', { type: 'image/jpeg' })
      })
    ).rejects.toThrow('Try-on request failed: 422 bad input');
  });
});
