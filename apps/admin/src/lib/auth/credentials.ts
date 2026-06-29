import "server-only";

import { createHash, timingSafeEqual } from "node:crypto";

import { getAdminPasswordHash, getAdminUsername } from "@/lib/admin-env";
import { verifyScryptPasswordHash } from "@/lib/auth/password";

function safeStringEqual(left: string, right: string): boolean {
  const leftDigest = createHash("sha256").update(left).digest();
  const rightDigest = createHash("sha256").update(right).digest();
  return timingSafeEqual(leftDigest, rightDigest);
}

export async function verifyAdminCredentials(
  username: string,
  password: string,
): Promise<boolean> {
  const expectedUsername = getAdminUsername();
  const expectedPasswordHash = getAdminPasswordHash();

  const validUsername = safeStringEqual(username.trim(), expectedUsername);
  const validPassword = await verifyScryptPasswordHash(password, expectedPasswordHash);

  return validUsername && validPassword;
}
