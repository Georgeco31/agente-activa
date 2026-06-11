import "server-only";

const DEFAULT_API_BASE_URL = "http://localhost:8000";

export const apiBaseUrl = (
  process.env.API_BASE_URL?.trim() || DEFAULT_API_BASE_URL
).replace(/\/+$/, "");
