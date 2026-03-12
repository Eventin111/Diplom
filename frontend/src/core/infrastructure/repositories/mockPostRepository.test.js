import { createMockPostRepository } from './mockPostRepository';

describe('mockPostRepository', () => {
  it('returns mocked feed posts', async () => {
    const repository = createMockPostRepository({
      config: {
        mockDelayMs: 0
      }
    });

    const posts = await repository.getFeedPosts();
    expect(Array.isArray(posts)).toBe(true);
    expect(posts.length).toBeGreaterThan(0);
  });

  it('works with default config dependency', async () => {
    const repository = createMockPostRepository();
    const posts = await repository.getFeedPosts();
    expect(posts[0]).toHaveProperty('id');
  });
});
