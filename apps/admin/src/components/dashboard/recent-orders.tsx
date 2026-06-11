import Link from "next/link";
import { ArrowUpRight, ClipboardList } from "lucide-react";

import type { DashboardRecentOrder } from "@/lib/api/dashboard-types";

function formatDate(value: string): string {
  return new Intl.DateTimeFormat("es-EC", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

export function RecentOrders({ orders }: { orders: DashboardRecentOrder[] }) {
  return (
    <section className="panel dashboard-recent-panel">
      <header className="panel-header">
        <div>
          <h2>Ultimos pedidos</h2>
          <p className="panel-description">Informacion inmediata para despacho</p>
        </div>
        <Link className="module-link" href="/orders">
          Ver todos
          <ArrowUpRight aria-hidden="true" size={15} />
        </Link>
      </header>
      {orders.length === 0 ? (
        <div className="empty-state">
          <span className="empty-state-icon">
            <ClipboardList aria-hidden="true" size={19} />
          </span>
          <strong>Sin pedidos recientes</strong>
          <p>Los pedidos nuevos apareceran aqui con sus datos de despacho.</p>
        </div>
      ) : (
        <div className="dashboard-recent-orders">
          {orders.map((order) => (
            <Link href={`/orders/${order.id}`} key={order.id}>
              <div className="dashboard-recent-heading">
                <div>
                  <span className="order-number">{order.order_number}</span>
                  <strong>{order.customer.display_name}</strong>
                  <small>{order.customer.primary_phone ?? "Sin telefono principal"}</small>
                </div>
                <span className="status-badge status-badge-neutral">{order.status.name}</span>
              </div>
              <div className="dashboard-recent-footer">
                <span>
                  <strong>{order.address.address}</strong>
                  <small>{order.address.reference ?? "Sin referencia"}</small>
                </span>
                <span>
                  <strong>${order.total}</strong>
                  <small>{formatDate(order.created_at)}</small>
                </span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </section>
  );
}
