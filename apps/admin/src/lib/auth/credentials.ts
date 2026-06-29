import "server-only";

import { createHash, timingSafeEqual } from "node:crypto";

import { verifyScryptPasswordHash } from "@/lib/auth/password";
import { AuthConfigurationError } from "@/lib/auth/session-token";

function requiredAdminEnv(name: "ADMIN_USERNAME" | "ADMIN_PASSWORD_HASH"): string {
  const value = process.env[name]?.trim();
  if (!value || value.includes("replace-with")) {
    throw new AuthConfigurationError(`${name} is required.`);
  }
  return value;
}

function safeStringEqual(left: string, right: string): boolean {
  const leftDigest = createHash("sha256").update(left).digest();
  const rightDigest = createHash("sha256").update(right).digest();
  return timingSafeEqual(leftDigest, rightDigest);
}

export async function verifyAdminCredentials(
  username: string,
  password: string,
): Promise<boolean> {
  const expectedUsername = requiredAdminEnv("ADMIN_USERNAME");
  const expectedPasswordHash = requiredAdminEnv("ADMIN_PASSWORD_HASH");

  const validUsername = safeStringEqual(username.trim(), expectedUsername);
  const validPassword = await verifyScryptPasswordHash(password, expectedPasswordHash);

  return validUsername && validPassword;
}
