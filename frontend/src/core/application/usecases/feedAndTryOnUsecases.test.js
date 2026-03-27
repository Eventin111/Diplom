import { fetchLikedFeedIds } from './fetchLikedFeedIds';
import { getTryOnSession } from './getTryOnSession';
import { likeFeedItem } from './likeFeedItem';
import { startTryOnSession } from './startTryOnSession';
import { subscribeToTryOnSession } from './subscribeToTryOnSession';
import { unlikeFeedItem } from './unlikeFeedItem';
import { uploadMedia } from './uploadMedia';

describe('feed and try-on use-cases', () => {
  it('delegates feed use-cases to repository methods', async () => {
    const feedRepository = {
      fetchLikedFeedIds: jest.fn().mockResolvedValue([1, 2]),
      likeFeedItem: jest.fn().mockResolvedValue({ ok: true }),
      unlikeFeedItem: jest.fn().mockResolvedValue({ ok: true })
    };

    await expect(fetchLikedFeedIds(feedRepository)).resolves.toEqual([1, 2]);
    await expect(likeFeedItem(feedRepository, 7)).resolves.toEqual({ ok: true });
    await expect(unlikeFeedItem(feedRepository, 7)).resolves.toEqual({ ok: true });

    expect(feedRepository.fetchLikedFeedIds).toHaveBeenCalledTimes(1);
    expect(feedRepository.likeFeedItem).toHaveBeenCalledWith(7);
    expect(feedRepository.unlikeFeedItem).toHaveBeenCalledWith(7);
  });

  it('delegates try-on and media use-cases to repository methods', async () => {
    const tryOnRepository = {
      runTryOn: jest.fn().mockResolvedValue({ sessionId: 15 }),
      getTryOnSession: jest.fn().mockResolvedValue({ id: 15, status: 'queued' }),
      subscribeToTryOnSession: jest.fn().mockReturnValue({ close: jest.fn() })
    };
    const mediaRepository = {
      uploadMedia: jest.fn().mockResolvedValue({ id: 22 })
    };
    const handlers = { onMessage: jest.fn() };
    const payload = { modelImage: 'a', clothImage: 'b' };

    await expect(startTryOnSession(tryOnRepository, payload)).resolves.toEqual({ sessionId: 15 });
    await expect(getTryOnSession(tryOnRepository, 15)).resolves.toEqual({ id: 15, status: 'queued' });
    await expect(uploadMedia(mediaRepository, new Blob(['x']))).resolves.toEqual({ id: 22 });
    expect(subscribeToTryOnSession(tryOnRepository, 15, handlers)).toEqual({ close: expect.any(Function) });

    expect(tryOnRepository.runTryOn).toHaveBeenCalledWith(payload);
    expect(tryOnRepository.getTryOnSession).toHaveBeenCalledWith(15);
    expect(tryOnRepository.subscribeToTryOnSession).toHaveBeenCalledWith(15, handlers);
    expect(mediaRepository.uploadMedia).toHaveBeenCalledTimes(1);
  });
});
