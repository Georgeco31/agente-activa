import type { ApiErrorDetail, ApiErrorResponse } from "@/lib/api/types";

const FALLBACK_ERROR: ApiErrorDetail = {
  code: "API_REQUEST_FAILED",
  message: "La API no pudo procesar la solicitud.",
  details: {},
};

export class ApiClientError extends Error {
  constructor(
    public readonly status: number,
    public readonly code: string,
    message: string,
    public readonly details: Record<string, unknown> = {},
  ) {
    super(message);
    this.name = "ApiClientError";
  }
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function isApiErrorResponse(value: unknown): value is ApiErrorResponse {
  if (!isRecord(value) || !isRecord(value.error)) {
    return false;
  }

  return (
    typeof value.error.code === "string" &&
    typeof value.error.message === "string" &&
    isRecord(value.error.details)
  );
}

export function parseApiError(payload: unknown): ApiErrorDetail {
  return isApiErrorResponse(payload) ? payload.error : FALLBACK_ERROR;
}
