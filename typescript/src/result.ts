/**
 * A small `Result<T, E>` union for expected failures.
 *
 * Python callers get exceptions; TypeScript callers repeatedly hand-roll a
 * `{ ok, value }` shape. This is that shape, with the handful of combinators
 * every copy re-implemented.
 */

export interface Ok<T> {
  readonly ok: true;
  readonly value: T;
}

export interface Err<E> {
  readonly ok: false;
  readonly error: E;
}

export type Result<T, E = Error> = Ok<T> | Err<E>;

/** Wrap a success value. */
export function ok<T>(value: T): Ok<T> {
  return { ok: true, value };
}

/** Wrap a failure value. */
export function err<E>(error: E): Err<E> {
  return { ok: false, error };
}

/** Narrow a `Result` to its success branch. */
export function isOk<T, E>(result: Result<T, E>): result is Ok<T> {
  return result.ok;
}

/** Narrow a `Result` to its failure branch. */
export function isErr<T, E>(result: Result<T, E>): result is Err<E> {
  return !result.ok;
}

/**
 * Return the value, or throw the error.
 *
 * Non-`Error` failures are wrapped so callers can always rely on an `Error`.
 */
export function unwrap<T, E>(result: Result<T, E>): T {
  if (result.ok) {
    return result.value;
  }
  throw result.error instanceof Error
    ? result.error
    : new Error(String(result.error));
}

/** Return the value, or `fallback` when the result is an error. */
export function unwrapOr<T, E>(result: Result<T, E>, fallback: T): T {
  return result.ok ? result.value : fallback;
}

/** Transform a success value, leaving an error untouched. */
export function mapResult<T, U, E>(
  result: Result<T, E>,
  transform: (value: T) => U
): Result<U, E> {
  return result.ok ? ok(transform(result.value)) : result;
}

/** Run `fn`, capturing a thrown value as an `Err` instead of propagating. */
export function toResult<T>(fn: () => T): Result<T, unknown> {
  try {
    return ok(fn());
  } catch (error) {
    return err(error);
  }
}

/** Run an async `fn`, capturing a rejection as an `Err`. */
export async function toResultAsync<T>(
  fn: () => Promise<T>
): Promise<Result<T, unknown>> {
  try {
    return ok(await fn());
  } catch (error) {
    return err(error);
  }
}
