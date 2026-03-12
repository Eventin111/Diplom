import { formatDate, formatDateTime } from './formatDate';

describe('formatDate utils', () => {
  it('returns empty string for invalid dates', () => {
    expect(formatDate('')).toBe('');
    expect(formatDate('invalid')).toBe('');
    expect(formatDateTime(null)).toBe('');
  });

  it('formats date and date-time', () => {
    const value = '2026-03-01T12:30:00.000Z';
    expect(formatDate(value)).toMatch(/\d{2}\.\d{2}\.\d{4}/);
    expect(formatDateTime(value)).toContain('2026');
  });
});

