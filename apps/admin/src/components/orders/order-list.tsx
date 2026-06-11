import Link from "next/link";
import { ClipboardList } from "lucide-react";

import { EmptyState } from "@/components/ui/empty-state";
import type { Order } from "@/lib/api/order-types";

function formatDate(value: string): string {
  return new Intl.DateTimeFormat("es-EC", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

export function OrderList({ orders }: { orders: Order[] }) {
  if (orders.length === 0) {
    return (
      <EmptyState
        description="No hay pedidos disponibles para los filtros seleccionados."
        icon={ClipboardList}
        title="Sin pedidos"
      />
    );
  }

  return (
    <div className="order-list">
      {orders.map((order) => (
        <Link className="order-item" href={`/orders/${order.id}`} key={order.id}>
          <div className="order-item-heading">
            <div>
              <span className="order-number">{order.order_number}</span>
              <strong>{order.customer.display_name}</strong>
              <span>{order.customer.primary_phone ?? "Sin telefono principal"}</span>
            </div>
            <span
              className={`status-badge ${
                order.status.is_final ? "status-badge-neutral" : "status-badge-success"
              }`}
            >
              <span className="status-badge-dot" aria-hidden="true" />
              {order.status.name}
            </span>
          </div>
          <div className="order-dispatch-data">
            <div>
              <span>Direccion</span>
              <strong>{order.address.address}</strong>
              <small>{order.address.reference ?? "Sin referencia"}</small>
            </div>
            <div>
              <span>Total</span>
              <strong className="order-total">${order.total}</strong>
              <small>{formatDate(order.created_at)}</small>
            </div>
          </div>
        </Link>
      ))}
    </div>
  );
}
