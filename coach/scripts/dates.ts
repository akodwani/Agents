/**
 * Every date in COACH is a plain `YYYY-MM-DD` string. All arithmetic goes
 * through UTC-noon Date objects so DST never shifts a day boundary.
 */
export type ISODate = string;

const MS_DAY = 86_400_000;

export function assertISO(d: string): ISODate {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(d)) throw new Error(`bad date: ${d}`);
  return d;
}

/** Days since the epoch for an ISO date (UTC noon anchored). */
export function toDayNum(d: ISODate): number {
  assertISO(d);
  const [y, m, day] = d.split('-').map(Number);
  return Math.floor(Date.UTC(y, m - 1, day, 12) / MS_DAY);
}

export function fromDayNum(n: number): ISODate {
  const dt = new Date(n * MS_DAY);
  return dt.toISOString().slice(0, 10);
}

export function addDays(d: ISODate, n: number): ISODate {
  return fromDayNum(toDayNum(d) + n);
}

/** b - a, in days. Positive when b is later. */
export function daysBetween(a: ISODate, b: ISODate): number {
  return toDayNum(b) - toDayNum(a);
}

/** 0 = Sunday … 6 = Saturday. */
export function dowOf(d: ISODate): number {
  assertISO(d);
  const [y, m, day] = d.split('-').map(Number);
  return new Date(Date.UTC(y, m - 1, day, 12)).getUTCDay();
}

/** Inclusive list of dates from `from` to `to`. */
export function dateRange(from: ISODate, to: ISODate): ISODate[] {
  const out: ISODate[] = [];
  for (let n = toDayNum(from); n <= toDayNum(to); n++) out.push(fromDayNum(n));
  return out;
}

/** Local calendar date of a Date object (the machine's timezone). */
export function localISODate(now: Date = new Date()): ISODate {
  const y = now.getFullYear();
  const m = String(now.getMonth() + 1).padStart(2, '0');
  const d = String(now.getDate()).padStart(2, '0');
  return `${y}-${m}-${d}`;
}

/** Fractional local hour, e.g. 14.5 for 14:30. Used by R7's 14:00 gate. */
export function localHour(now: Date = new Date()): number {
  return now.getHours() + now.getMinutes() / 60;
}

export function isSunday(d: ISODate): boolean {
  return dowOf(d) === 0;
}
