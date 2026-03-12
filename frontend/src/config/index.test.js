import { appConfig, getConfig } from './index';

describe('config index exports', () => {
  it('re-exports appConfig contract', () => {
    expect(getConfig()).toBe(appConfig);
  });
});

