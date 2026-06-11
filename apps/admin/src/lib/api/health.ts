import "server-only";

import { ApiClientError } from "@/lib/api/errors";
import { apiFetch } from "@/lib/api/http";
import type { ApiErrorDetail, HealthResponse } from "@/lib/api/types";

export type HealthResult =
  | { ok: true; data: HealthResponse }
  | { ok: false; error: ApiErrorDetail };

export async function getHealth(): Promise<HealthResult> {
  try {
    return {
      ok: true,
      data: await apiFetch<HealthResponse>("/api/v1/health"),
    };
  } catch (error) {
    if (error instanceof ApiClientError) {
      return {
        ok: false,
        error: {
          code: error.code,
          message: error.message,
          details: error.details,
        },
      };
    }

    return {
      ok: false,
      error: {
        code: "INTERNAL_CLIENT_ERROR",
        message: "No fue posible consultar el estado de la API.",
        details: {},
      },
    };
  }
}
