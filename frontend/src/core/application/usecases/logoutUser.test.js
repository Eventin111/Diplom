import { logoutUser } from './logoutUser';

describe('logoutUser use-case', () => {
  it('calls repository.logout', async () => {
    const repository = { logout: jest.fn() };
    const result = await logoutUser(repository);

    expect(repository.logout).toHaveBeenCalledTimes(1);
    expect(result).toBe(true);
  });
});

