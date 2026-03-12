import { appConfig, getConfig } from './appConfig';

describe('appConfig', () => {
  it('returns immutable configuration object', () => {
    expect(getConfig()).toBe(appConfig);
    expect(Object.isFrozen(appConfig)).toBe(true);
  });

  it('contains required auth storage keys', () => {
    expect(appConfig.authStorageKeys.token).toBe('swipelt_token');
    expect(appConfig.authStorageKeys.user).toBe('swipelt_user');
    expect(appConfig.authStorageKeys.registeredUsers).toBe('swipelt_registered_users');
  });
});

