import { getFeedPosts } from './getFeedPosts';

describe('getFeedPosts use-case', () => {
  it('delegates to repository', async () => {
    const repo = {
      getFeedPosts: jest.fn().mockResolvedValue([{ id: 1 }])
    };
    const posts = await getFeedPosts(repo);
    expect(repo.getFeedPosts).toHaveBeenCalledTimes(1);
    expect(posts).toEqual([{ id: 1 }]);
  });
});

