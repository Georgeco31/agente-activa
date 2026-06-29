const PLACEHOLDER_MARKER = "replace-with";
const MIN_AUTH_SECRET_LENGTH = 32;
const SCRYPT_PARTS = 6;
const BASE64URL_PATTERN = /^[A-Za-z0-9_-]+$/;

type AdminEnvName =
  | "API_BASE_URL"
  | "ADMIN_USERNAME"
  | "ADMIN_PASSWORD_HASH"
  | "AUTH_SECRET";

export class AdminConfigurationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "AdminConfigurationError";
  }
}

function requiredEnv(name: AdminEnvName): string {
  const value = process.env[name]?.trim();
  if (!value) {
    throw new AdminConfigurationError(`${name} is required.`);
  }
  if (value.includes(PLACEHOLDER_MARKER)) {
    throw new AdminConfigurationError(`${name} must be configured and cannot be a placeholder.`);
  }
  return value;
}

function parsePositiveInteger(value: string): number | null {
  const parsed = Number(value);
  return Number.isInteger(parsed) && parsed > 0 ? parsed : null;
}

export function validateScryptPasswordHash(hash: string): void {
  const parts = hash.split("$");
  const [scheme, nValue, rValue, pValue, salt, digest] = parts;

  if (
    parts.length !== SCRYPT_PARTS ||
    scheme !== "scrypt" ||
    !parsePositiveInteger(nValue) ||
    !parsePositiveInteger(rValue) ||
    !parsePositiveInteger(pValue) ||
    !salt ||
    !digest ||
    !BASE64URL_PATTERN.test(salt) ||
    !BASE64URL_PATTERN.test(digest)
  ) {
    throw new AdminConfigurationError(
      "ADMIN_PASSWORD_HASH must use format scrypt$N$r$p$salt-base64url$hash-base64url.",
    );
  }
}

export function getAdminApiBaseUrl(): string {
  const rawUrl = requiredEnv("API_BASE_URL");

  try {
    const parsedUrl = new URL(rawUrl);
    if (parsedUrl.protocol !== "http:" && parsedUrl.protocol !== "https:") {
      throw new AdminConfigurationError("API_BASE_URL must use http or https.");
    }
    return rawUrl.replace(/\/+$/, "");
  } catch (error) {
    if (error instanceof AdminConfigurationError) {
      throw error;
    }
    throw new AdminConfigurationError("API_BASE_URL must be a valid URL.");
  }
}

export function getAdminUsername(): string {
  const username = requiredEnv("ADMIN_USERNAME");
  if (username.length < 3) {
    throw new AdminConfigurationError("ADMIN_USERNAME must be at least 3 characters.");
  }
  return username;
}

export function getAdminPasswordHash(): string {
  const passwordHash = requiredEnv("ADMIN_PASSWORD_HASH");
  validateScryptPasswordHash(passwordHash);
  return passwordHash;
}

export function getAuthSecret(): string {
  const secret = requiredEnv("AUTH_SECRET");
  if (secret.length < MIN_AUTH_SECRET_LENGTH) {
    throw new AdminConfigurationError(
      `AUTH_SECRET must be at least ${MIN_AUTH_SECRET_LENGTH} characters.`,
    );
  }
  return secret;
}
