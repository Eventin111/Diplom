import { getNextIndex, getPreviousIndex } from './swipeService';

describe('swipeService', () => {
  it('calculates next index', () => {
    expect(getNextIndex(0, 3)).toBe(1);
    expect(getNextIndex(2, 3)).toBe(0);
  });

  it('calculates previous index', () => {
    expect(getPreviousIndex(1, 3)).toBe(0);
    expect(getPreviousIndex(0, 3)).toBe(2);
  });
});

