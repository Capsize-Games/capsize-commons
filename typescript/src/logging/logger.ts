/**
 * Structured logging matching CAPSIZE_PROJECT_STANDARDS.md §14.
 *
 * The emitted JSON carries `timestamp`, `level`, `logger` and `message`; extra
 * caller data is nested under `fields` so it can never overwrite a base field,
 * exactly as the Python `JsonFormatter` does.
 */

export type LogLevel = "debug" | "info" | "warn" | "error";

const LEVEL_ORDER: Record<LogLevel, number> = {
  debug: 10,
  info: 20,
  warn: 30,
  error: 40
};

export type LogFields = Record<string, unknown>;

export interface LoggerOptions {
  /** Logger name, e.g. the service or module. */
  name: string;
  /** Minimum level to emit. Defaults to `"info"`. */
  level?: LogLevel;
  /** Emit one JSON object per line. Defaults to `false`. */
  json?: boolean;
  /** Where lines go. Defaults to `console.log` (stdout, per §14). */
  sink?: (line: string) => void;
}

export interface Logger {
  readonly name: string;
  readonly level: LogLevel;
  debug(message: string, fields?: LogFields): void;
  info(message: string, fields?: LogFields): void;
  warn(message: string, fields?: LogFields): void;
  error(message: string, fields?: LogFields): void;
  /** Derive a logger whose name is `<parent>.<child>`. */
  child(name: string): Logger;
}

/** Create a logger. No global state is created or read. */
export function createLogger(options: LoggerOptions): Logger {
  const level = options.level ?? "info";
  const json = options.json ?? false;
  const sink = options.sink ?? ((line: string) => console.log(line));
  const threshold = LEVEL_ORDER[level];

  const emit = (
    recordLevel: LogLevel,
    message: string,
    fields?: LogFields
  ): void => {
    if (LEVEL_ORDER[recordLevel] < threshold) {
      return;
    }
    const timestamp = new Date().toISOString();
    if (json) {
      sink(
        JSON.stringify({
          timestamp,
          level: recordLevel.toUpperCase(),
          logger: options.name,
          message,
          ...(fields === undefined ? {} : { fields })
        })
      );
      return;
    }
    const suffix = fields === undefined ? "" : ` ${JSON.stringify(fields)}`;
    sink(
      `${timestamp} ${recordLevel.toUpperCase()} ${options.name} ` +
        `${message}${suffix}`
    );
  };

  return {
    name: options.name,
    level,
    debug: (message, fields) => emit("debug", message, fields),
    info: (message, fields) => emit("info", message, fields),
    warn: (message, fields) => emit("warn", message, fields),
    error: (message, fields) => emit("error", message, fields),
    child: (childName) =>
      createLogger({ ...options, name: `${options.name}.${childName}` })
  };
}
