import { describe, expect, it } from 'vitest';
import { addDays, dateRange, daysBetween, dowOf, fromDayNum, isSunday, toDayNum } from '../scripts/dates.js';

describe('dates', () => {
  it('round-trips through day numbers', () => {
    for (const d of ['2026-01-01', '2026-02-28', '2026-03-08', '2026-08-22', '2026-12-31']) {
      expect(fromDayNum(toDayNum(d))).toBe(d);
    }
  });

  it('adds days across month, year and DST boundaries', () => {
    expect(addDays('2026-08-22', -7)).toBe('2026-08-15');
    expect(addDays('2026-08-22', 1)).toBe('2026-08-23');
    expect(addDays('2026-03-07', 1)).toBe('2026-03-08'); // US DST spring forward
    expect(addDays('2026-11-01', 1)).toBe('2026-11-02'); // US DST fall back
    expect(addDays('2026-12-31', 1)).toBe('2027-01-01');
    expect(addDays('2026-01-01', -1)).toBe('2025-12-31');
  });

  it('measures gaps and weekdays', () => {
    expect(daysBetween('2026-08-15', '2026-08-22')).toBe(7);
    expect(daysBetween('2026-08-22', '2026-08-15')).toBe(-7);
    expect(dowOf('2026-08-22')).toBe(6); // Saturday
    expect(dowOf('2026-08-23')).toBe(0); // Sunday
    expect(isSunday('2026-08-23')).toBe(true);
    expect(isSunday('2026-08-22')).toBe(false);
  });

  it('builds inclusive ranges', () => {
    expect(dateRange('2026-08-20', '2026-08-22')).toEqual(['2026-08-20', '2026-08-21', '2026-08-22']);
  });

  it('rejects malformed dates', () => {
    expect(() => toDayNum('22-08-2026')).toThrow(/bad date/);
  });
});
