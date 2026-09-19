/**
 * Typed environment access.
 *
 * `process` is read defensively so this module is safe to import in a browser
 * bundle. `readPublicEnv` enforces the §5.3 rule that only `VITE_`-prefixed
 * variables may reach the client, turning a leaked secret into a startup error
 * rather than a shipped one.
 */

export class EnvError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "EnvError";
  }
}

const FALSEY = new Set(["", "0", "false", "no", "off"]);

function environment(): Record<string, string | undefined> {
  const scope = globalThis as {
    process?: { env?: Record<string, string | undefined> };
  };
  return scope.process?.env ?? {};
}

export interface ReadEnvOptions {
  /** Throw `EnvError` when the variable is unset or empty. */
  required?: boolean;
  /** Value used when the variable is unset or empty. */
  defaultValue?: string;
}

/** Read a string environment variable, with optional requirement/default. */
export function readEnv(name: string, options: ReadEnvOptions = {}): string {
  const raw = environment()[name];
  if (raw === undefined || raw === "") {
    if (options.required) {
      throw new EnvError(`Missing required environment variable: ${name}`);
    }
    return options.defaultValue ?? "";
  }
  return raw;
}

/** Read an environment variable that is safe to expose to the client. */
export function readPublicEnv(
  name: string,
  options: ReadEnvOptions = {}
): string {
  if (!name.startsWith("VITE_")) {
    throw new EnvError(
      `Client-exposed variables must be prefixed VITE_: ${name}`
    );
  }
  return readEnv(name, options);
}

/** Read a boolean flag, treating "", 0, false, no and off as false. */
export function readBooleanEnv(
  name: string,
  options: { defaultValue?: boolean } = {}
): boolean {
  const raw = environment()[name];
  if (raw === undefined) {
    return options.defaultValue ?? false;
  }
  return !FALSEY.has(raw.trim().toLowerCase());
}

/** Read a numeric variable, failing loudly on a non-numeric value. */
export function readNumberEnv(
  name: string,
  options: { required?: boolean; defaultValue?: number } = {}
): number {
  const raw = environment()[name];
  if (raw === undefined || raw === "") {
    if (options.defaultValue !== undefined) {
      return options.defaultValue;
    }
    if (options.required) {
      throw new EnvError(`Missing required environment variable: ${name}`);
    }
    return 0;
  }
  const parsed = Number(raw);
  if (Number.isNaN(parsed)) {
    throw new EnvError(`Environment variable ${name} is not a number: ${raw}`);
  }
  return parsed;
}
