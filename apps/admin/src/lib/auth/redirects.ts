const FALLBACK_PATH = "/";

export function safeNextPath(value: string | undefined): string {
  const candidate = value?.trim();
  if (!candidate) {
    return FALLBACK_PATH;
  }

  if (
    !candidate.startsWith("/") ||
    candidate.startsWith("//") ||
    candidate.startsWith("/_next") ||
    candidate.startsWith("/login") ||
    candidate.startsWith("/logout")
  ) {
    return FALLBACK_PATH;
  }

  return candidate;
}
