import "server-only";

import { apiBaseUrl } from "@/lib/config";
import { ApiClientError, parseApiError } from "@/lib/api/errors";

const REQUEST_TIMEOUT_MS = 5_000;

export async function apiFetch<T>(
  path: string,
  init: RequestInit = {},
): Promise<T> {
  try {
    const response = await fetch(`${apiBaseUrl}${path}`, {
      ...init,
      cache: "no-store",
      headers: {
        Accept: "application/json",
        ...init.headers,
      },
      signal: init.signal ?? AbortSignal.timeout(REQUEST_TIMEOUT_MS),
    });

    const payload: unknown = await response.json();

    if (!response.ok) {
      const error = parseApiError(payload);
      throw new ApiClientError(
        response.status,
        error.code,
        error.message,
        error.details,
      );
    }

    return payload as T;
  } catch (error) {
    if (error instanceof ApiClientError) {
      throw error;
    }

    throw new ApiClientError(
      503,
      "API_UNAVAILABLE",
      "No fue posible conectar con la API.",
    );
  }
}
