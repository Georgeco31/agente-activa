import type { OrderAddress, OrderCustomer, OrderStatus } from "@/lib/api/order-types";

export interface DashboardSummary {
  orders_today: number;
  pending_orders: number;
  assigned_orders: number;
  en_route_orders: number;
  delivered_orders: number;
  not_delivered_orders: number;
  cancelled_orders: number;
  sales_total_today: string;
  sales_total_month: string;
  active_products: number;
  total_customers: number;
}

export interface DashboardStatusCount {
  code: string;
  name: string;
  count: number;
}

export interface DashboardDailySales {
  day: number;
  date: string;
  sales_total: string;
  delivered_orders_count: number;
}

export interface DashboardRecentOrder {
  id: string;
  order_number: string;
  customer: OrderCustomer;
  address: OrderAddress;
  status: OrderStatus;
  total: string;
  created_at: string;
}

export interface DashboardAlert {
  code: string;
  label: string;
  count: number;
  severity: "info" | "warning" | "danger";
  status_code: string;
}

export interface DashboardOverview {
  selected_date: string;
  month: number;
  year: number;
  summary: DashboardSummary;
  orders_by_status: DashboardStatusCount[];
  monthly_sales: DashboardDailySales[];
  recent_orders: DashboardRecentOrder[];
  alerts: DashboardAlert[];
}

export interface DashboardOverviewParams {
  date?: string;
  year?: number;
  month?: number;
}
