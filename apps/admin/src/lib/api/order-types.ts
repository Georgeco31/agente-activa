export type OrderStatusCode =
  | "pendiente"
  | "asignado"
  | "en_camino"
  | "entregado"
  | "no_entregado"
  | "cancelado";

export const ORDER_STATUS_OPTIONS: Array<{
  code: OrderStatusCode;
  label: string;
  isFinal: boolean;
}> = [
  { code: "pendiente", label: "Pendiente", isFinal: false },
  { code: "asignado", label: "Asignado", isFinal: false },
  { code: "en_camino", label: "En camino", isFinal: false },
  { code: "entregado", label: "Entregado", isFinal: true },
  { code: "no_entregado", label: "No entregado", isFinal: true },
  { code: "cancelado", label: "Cancelado", isFinal: true },
];

export interface OrderStatus {
  id: string;
  code: string;
  name: string;
  is_final: boolean;
}

export interface OrderCustomer {
  id: string;
  display_name: string;
  primary_phone: string | null;
}

export interface OrderAddress {
  id: string;
  address: string;
  reference: string | null;
}

export interface OrderItem {
  id: string;
  product_id: string;
  product_name_snapshot: string;
  quantity: string;
  unit_price: string;
  line_total: string;
}

export interface Order {
  id: string;
  order_number: string;
  customer_id: string;
  address_id: string;
  customer: OrderCustomer;
  address: OrderAddress;
  status: OrderStatus;
  delivery_route_id: string | null;
  notes: string | null;
  source_channel: string;
  subtotal: string;
  delivery_fee: string;
  total: string;
  confirmed_at: string | null;
  created_at: string;
  items: OrderItem[];
}

export interface OrderItemCreateInput {
  product_id: string;
  quantity: string;
  unit_price?: string | null;
}

export interface OrderCreateInput {
  customer_id: string;
  address_id: string;
  items: OrderItemCreateInput[];
  notes?: string | null;
  delivery_route_id?: string | null;
}

export interface OrderStatusUpdateInput {
  status_code: string;
}

export interface OrderListParams {
  customer_id?: string;
  status_code?: string;
}
