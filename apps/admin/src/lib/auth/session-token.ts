import { createHmac, timingSafeEqual } from "node:crypto";

export const SESSION_COOKIE_NAME = "agente_activa_session";
export const SESSION_MAX_AGE_SECONDS = 8 * 60 * 60;

export type AdminSessionPayload = {
  username: string;
  role: "admin";
  iat: number;
  exp: number;
};

export class AuthConfigurationError extends Error {
  constructor(message = "Authentication is not configured.") {
    super(message);
    this.name = "AuthConfigurationError";
  }
}

function getRequiredAuthSecret(): string {
  const secret = process.env.AUTH_SECRET?.trim();
  if (!secret || secret.includes("replace-with") || secret.length < 32) {
    throw new AuthConfigurationError("AUTH_SECRET is required.");
  }
  return secret;
}

function getVerificationSecret(): string | null {
  try {
    return getRequiredAuthSecret();
  } catch {
    return null;
  }
}

function encodeJson(payload: AdminSessionPayload): string {
  return Buffer.from(JSON.stringify(payload), "utf8").toString("base64url");
}

function decodeJson(value: string): unknown {
  return JSON.parse(Buffer.from(value, "base64url").toString("utf8"));
}

function signPayload(encodedPayload: string, secret: string): string {
  return createHmac("sha256", secret).update(encodedPayload).digest("base64url");
}

function safeEqual(left: string, right: string): boolean {
  const leftBuffer = Buffer.from(left, "utf8");
  const rightBuffer = Buffer.from(right, "utf8");
  if (leftBuffer.length !== rightBuffer.length) {
    return false;
  }
  return timingSafeEqual(leftBuffer, rightBuffer);
}

function isSessionPayload(payload: unknown): payload is AdminSessionPayload {
  if (!payload || typeof payload !== "object") {
    return false;
  }

  const candidate = payload as Record<string, unknown>;
  return (
    typeof candidate.username === "string" &&
    candidate.username.length > 0 &&
    candidate.role === "admin" &&
    typeof candidate.iat === "number" &&
    Number.isInteger(candidate.iat) &&
    typeof candidate.exp === "number" &&
    Number.isInteger(candidate.exp)
  );
}

export function createSessionToken(username: string): string {
  const secret = getRequiredAuthSecret();
  const now = Math.floor(Date.now() / 1000);
  const payload: AdminSessionPayload = {
    username,
    role: "admin",
    iat: now,
    exp: now + SESSION_MAX_AGE_SECONDS,
  };
  const encodedPayload = encodeJson(payload);
  return `${encodedPayload}.${signPayload(encodedPayload, secret)}`;
}

export function verifySessionToken(token: string | undefined): AdminSessionPayload | null {
  if (!token) {
    return null;
  }

  const secret = getVerificationSecret();
  if (!secret) {
    return null;
  }

  const parts = token.split(".");
  if (parts.length !== 2 || !parts[0] || !parts[1]) {
    return null;
  }

  const expectedSignature = signPayload(parts[0], secret);
  if (!safeEqual(parts[1], expectedSignature)) {
    return null;
  }

  try {
    const payload = decodeJson(parts[0]);
    if (!isSessionPayload(payload)) {
      return null;
    }

    const now = Math.floor(Date.now() / 1000);
    return payload.exp > now ? payload : null;
  } catch {
    return null;
  }
}

export function sessionCookieOptions() {
  return {
    httpOnly: true,
    sameSite: "lax" as const,
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: SESSION_MAX_AGE_SECONDS,
  };
}
