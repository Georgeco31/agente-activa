import { scrypt, timingSafeEqual, type ScryptOptions } from "node:crypto";
import { promisify } from "node:util";

const scryptAsync = promisify(scrypt) as (
  password: string,
  salt: Buffer,
  keylen: number,
  options: ScryptOptions,
) => Promise<Buffer>;

const HASH_PREFIX = "scrypt";
const HASH_PARTS = 6;

type ParsedScryptHash = {
  n: number;
  r: number;
  p: number;
  salt: Buffer;
  digest: Buffer;
};

function parsePositiveInteger(value: string): number | null {
  const parsed = Number(value);
  return Number.isInteger(parsed) && parsed > 0 ? parsed : null;
}

function parseScryptHash(hash: string): ParsedScryptHash | null {
  const parts = hash.split("$");
  if (parts.length !== HASH_PARTS || parts[0] !== HASH_PREFIX) {
    return null;
  }

  const n = parsePositiveInteger(parts[1]);
  const r = parsePositiveInteger(parts[2]);
  const p = parsePositiveInteger(parts[3]);
  if (!n || !r || !p) {
    return null;
  }

  try {
    return {
      n,
      r,
      p,
      salt: Buffer.from(parts[4], "base64url"),
      digest: Buffer.from(parts[5], "base64url"),
    };
  } catch {
    return null;
  }
}

export async function verifyScryptPasswordHash(
  password: string,
  hash: string,
): Promise<boolean> {
  const parsed = parseScryptHash(hash);
  if (!parsed || parsed.digest.length === 0 || parsed.salt.length === 0) {
    return false;
  }

  try {
    const derivedKey = await scryptAsync(password, parsed.salt, parsed.digest.length, {
      N: parsed.n,
      r: parsed.r,
      p: parsed.p,
      maxmem: 128 * 1024 * 1024,
    });

    return timingSafeEqual(derivedKey, parsed.digest);
  } catch {
    return false;
  }
}
