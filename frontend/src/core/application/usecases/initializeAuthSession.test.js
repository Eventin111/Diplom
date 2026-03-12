import { initializeAuthSession } from './initializeAuthSession';

describe('initializeAuthSession use-case', () => {
  it('delegates call to repository', async () => {
    const repository = {
      initializeSession: jest.fn().mockReturnValue({ token: 'x', user: { id: 1 } })
    };

    const result = await initializeAuthSession(repository);
    expect(repository.initializeSession).toHaveBeenCalledTimes(1);
    expect(result.user.id).toBe(1);
  });
});

