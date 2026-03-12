import {
  buildAvatarUrl,
  isGuestEmail,
  isValidEmail,
  isValidPassword,
  isValidUsername
} from './authPolicy';

describe('authPolicy', () => {
  it('validates email format', () => {
    expect(isValidEmail('user@example.com')).toBe(true);
    expect(isValidEmail('invalid')).toBe(false);
    expect(isValidEmail()).toBe(false);
  });

  it('validates password length', () => {
    expect(isValidPassword('123456')).toBe(true);
    expect(isValidPassword('12345')).toBe(false);
    expect(isValidPassword(undefined, 1)).toBe(false);
  });

  it('validates username length', () => {
    expect(isValidUsername('alice')).toBe(true);
    expect(isValidUsername('ab')).toBe(false);
    expect(isValidUsername()).toBe(false);
  });

  it('detects guest email', () => {
    expect(isGuestEmail('guest@swipelt.com')).toBe(true);
    expect(isGuestEmail('user@mail.com')).toBe(false);
    expect(isGuestEmail(undefined)).toBe(false);
  });

  it('builds encoded avatar url', () => {
    const url = buildAvatarUrl('Тест Юзер');
    expect(url).toContain('ui-avatars.com');
    expect(url).toContain('%D0%A2%D0%B5%D1%81%D1%82');
  });
});
