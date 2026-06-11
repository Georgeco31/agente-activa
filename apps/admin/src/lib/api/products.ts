import "server-only";

import type {
  Product,
  ProductCreateInput,
  ProductDeactivateResult,
  ProductSearchCriteria,
  ProductSearchResult,
  ProductUpdateInput,
} from "@/lib/api/product-types";
import { apiFetch } from "@/lib/api/http";

const PRODUCTS_PATH = "/api/v1/products";

function jsonRequest(method: "POST" | "PATCH", body?: unknown): RequestInit {
  return {
    method,
    headers: body === undefined ? undefined : { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  };
}

export function createProduct(input: ProductCreateInput): Promise<Product> {
  return apiFetch<Product>(PRODUCTS_PATH, jsonRequest("POST", input));
}

export function listProducts(activeOnly = false): Promise<Product[]> {
  const params = new URLSearchParams({ active_only: String(activeOnly) });
  return apiFetch<Product[]>(`${PRODUCTS_PATH}?${params.toString()}`);
}

export function getProduct(productId: string): Promise<Product> {
  return apiFetch<Product>(`${PRODUCTS_PATH}/${productId}`);
}

export function searchProducts(
  criteria: ProductSearchCriteria,
): Promise<ProductSearchResult[]> {
  const params = new URLSearchParams();

  Object.entries(criteria).forEach(([key, value]) => {
    if (value) {
      params.set(key, value);
    }
  });

  return apiFetch<ProductSearchResult[]>(
    `${PRODUCTS_PATH}/search?${params.toString()}`,
  );
}

export function updateProduct(
  productId: string,
  input: ProductUpdateInput,
): Promise<Product> {
  return apiFetch<Product>(
    `${PRODUCTS_PATH}/${productId}`,
    jsonRequest("PATCH", input),
  );
}

export function deactivateProduct(
  productId: string,
): Promise<ProductDeactivateResult> {
  return apiFetch<ProductDeactivateResult>(
    `${PRODUCTS_PATH}/${productId}/deactivate`,
    jsonRequest("PATCH"),
  );
}
