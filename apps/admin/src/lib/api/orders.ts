import "server-only";

import { apiFetch } from "@/lib/api/http";
import type {
  Order,
  OrderCreateInput,
  OrderListParams,
  OrderStatusUpdateInput,
} from "@/lib/api/order-types";

const ORDERS_PATH = "/api/v1/orders";

function jsonRequest(method: "POST" | "PATCH", body?: unknown): RequestInit {
  return {
    method,
    headers: body === undefined ? undefined : { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  };
}

export function createOrder(input: OrderCreateInput): Promise<Order> {
  return apiFetch<Order>(ORDERS_PATH, jsonRequest("POST", input));
}

export function listOrders(params: OrderListParams = {}): Promise<Order[]> {
  const query = new URLSearchParams();

  if (params.customer_id) {
    query.set("customer_id", params.customer_id);
  }
  if (params.status_code) {
    query.set("status_code", params.status_code);
  }

  const suffix = query.size > 0 ? `?${query.toString()}` : "";
  return apiFetch<Order[]>(`${ORDERS_PATH}${suffix}`);
}

export function getOrder(orderId: string): Promise<Order> {
  return apiFetch<Order>(`${ORDERS_PATH}/${orderId}`);
}

export function updateOrderStatus(
  orderId: string,
  input: OrderStatusUpdateInput,
): Promise<Order> {
  return apiFetch<Order>(
    `${ORDERS_PATH}/${orderId}/status`,
    jsonRequest("PATCH", input),
  );
}

export function cancelOrder(orderId: string): Promise<Order> {
  return apiFetch<Order>(
    `${ORDERS_PATH}/${orderId}/cancel`,
    jsonRequest("PATCH"),
  );
}
