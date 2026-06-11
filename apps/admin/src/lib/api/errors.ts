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

export function toApiErrorDetail(error: unknown): ApiErrorDetail {
  if (error instanceof ApiClientError) {
    return {
      code: error.code,
      message: error.message,
      details: error.details,
    };
  }

  return {
    code: "INTERNAL_CLIENT_ERROR",
    message: "No fue posible completar la solicitud.",
    details: {},
  };
}

const FRIENDLY_MESSAGES: Record<string, string> = {
  API_UNAVAILABLE: "No fue posible conectar con la API. Verifica que el backend este activo.",
  BUSINESS_RULE_ERROR: "La solicitud no cumple una regla del negocio.",
  CUSTOMER_DUPLICATE_CANDIDATE_FOUND:
    "Se encontraron posibles clientes duplicados. Revisa los candidatos antes de continuar.",
  CUSTOMER_NOT_FOUND: "El cliente solicitado no existe.",
  CUSTOMER_PHONE_ALREADY_EXISTS: "Ese telefono ya esta registrado para otro cliente.",
  INTERNAL_CLIENT_ERROR: "Ocurrio un error inesperado en el panel.",
  INTERNAL_SERVER_ERROR: "La API encontro un error inesperado.",
  DELIVERY_ROUTE_NOT_FOUND: "La ruta de reparto indicada no existe.",
  ORDER_ADDRESS_NOT_BELONG_TO_CUSTOMER:
    "La direccion seleccionada no pertenece al cliente.",
  ORDER_ADDRESS_NOT_FOUND: "La direccion seleccionada no existe.",
  ORDER_ALREADY_FINALIZED: "El pedido ya esta finalizado y no admite cambios.",
  ORDER_INVALID_ITEMS: "El pedido debe incluir al menos un producto valido.",
  ORDER_INVALID_PRICE: "Uno de los precios del pedido no es valido.",
  ORDER_INVALID_QUANTITY: "Una de las cantidades del pedido no es valida.",
  ORDER_NOT_FOUND: "El pedido solicitado no existe.",
  ORDER_PRODUCT_INACTIVE: "Uno de los productos seleccionados esta inactivo.",
  ORDER_PRODUCT_NOT_FOUND: "Uno de los productos seleccionados no existe.",
  ORDER_STATUS_NOT_FOUND: "El estado de pedido seleccionado no existe.",
  PRODUCT_INVALID_PRICE: "El precio del producto no es valido.",
  PRODUCT_NOT_FOUND: "El producto solicitado no existe.",
  PRODUCT_SKU_ALREADY_EXISTS: "Ese SKU ya esta registrado para otro producto.",
  VALIDATION_ERROR: "Revisa los datos ingresados e intenta nuevamente.",
};

export function getFriendlyErrorMessage(error: ApiErrorDetail): string {
  return FRIENDLY_MESSAGES[error.code] ?? error.message;
}
