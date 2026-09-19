/**
 * `fetch` helpers: JSON parsing, a timeout, and a typed error.
 *
 * Every project wrapped `fetch` slightly differently and none of the copies
 * combined a timeout with an abort signal correctly. This merges the caller's
 * signal into the timeout controller so either can cancel the request.
 */

export class HttpError extends Error {
  readonly status: number;
  readonly body: string;

  constructor(status: number, body: string) {
    super(`HTTP ${status}`);
    this.name = "HttpError";
    this.status = status;
    this.body = body;
  }
}

export interface FetchJsonOptions extends RequestInit {
  /** Abort the request after this many milliseconds. Defaults to 10000. */
  timeoutMs?: number;
}

/**
 * Fetch `url` and parse the response as JSON.
 *
 * Throws {@link HttpError} on a non-2xx response and lets the underlying
 * abort/timeout error propagate on cancellation.
 */
export async function fetchJson<T>(
  url: string,
  options: FetchJsonOptions = {}
): Promise<T> {
  const { timeoutMs = 10_000, signal, ...init } = options;
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  if (signal !== undefined && signal !== null) {
    if (signal.aborted) {
      controller.abort();
    } else {
      signal.addEventListener("abort", () => controller.abort(), {
        once: true
      });
    }
  }

  try {
    const response = await fetch(url, { ...init, signal: controller.signal });
    const text = await response.text();
    if (!response.ok) {
      throw new HttpError(response.status, text);
    }
    return (text === "" ? undefined : JSON.parse(text)) as T;
  } finally {
    clearTimeout(timer);
  }
}
