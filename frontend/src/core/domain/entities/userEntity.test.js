import { createUserEntity, sanitizeUserEntity } from './userEntity';

describe('userEntity', () => {
  it('creates user entity with fallback avatar', () => {
    const user = createUserEntity({
      id: 1,
      email: 'user@mail.com',
      username: 'user'
    });

    expect(user.avatar).toContain('ui-avatars.com');
    expect(user.isGuest).toBe(false);
  });

  it('returns null for invalid sanitize payload', () => {
    expect(sanitizeUserEntity(null)).toBeNull();
    expect(sanitizeUserEntity({ email: 'mail@test.com' })).toBeNull();
  });

  it('sanitizes a valid user', () => {
    const user = sanitizeUserEntity({
      id: 2,
      email: 'a@a.com',
      username: 'anna'
    });

    expect(user.username).toBe('anna');
  });
});

