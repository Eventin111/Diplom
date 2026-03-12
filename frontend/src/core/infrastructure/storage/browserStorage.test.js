import { createBrowserStorage } from './browserStorage';

describe('browserStorage', () => {
  it('delegates to provided storage', () => {
    const memory = {
      state: {},
      getItem(key) {
        return this.state[key] ?? null;
      },
      setItem(key, value) {
        this.state[key] = value;
      },
      removeItem(key) {
        delete this.state[key];
      }
    };

    const storage = createBrowserStorage(memory);
    storage.setItem('x', '1');
    expect(storage.getItem('x')).toBe('1');
    storage.removeItem('x');
    expect(storage.getItem('x')).toBeNull();
  });
});

