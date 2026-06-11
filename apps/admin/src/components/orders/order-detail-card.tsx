import {
  CalendarClock,
  CircleDollarSign,
  ClipboardList,
  MapPin,
  Phone,
  UserRound,
} from "lucide-react";

import type { Order } from "@/lib/api/order-types";

function formatDate(value: string | null): string {
  if (!value) {
    return "Sin fecha";
  }

  return new Intl.DateTimeFormat("es-EC", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

export function OrderDetailCard({ order }: { order: Order }) {
  return (
    <div className="order-detail-layout">
      <section className="panel order-summary">
        <header className="panel-header">
          <div>
            <p className="order-number">{order.order_number}</p>
            <h2>Informacion para despacho</h2>
          </div>
          <span
            className={`status-badge ${
              order.status.is_final ? "status-badge-neutral" : "status-badge-success"
            }`}
          >
            <span className="status-badge-dot" aria-hidden="true" />
            {order.status.name}
          </span>
        </header>
        <div className="panel-body dispatch-grid">
          <div className="dispatch-item">
            <UserRound aria-hidden="true" size={18} />
            <span>Cliente</span>
            <strong>{order.customer.display_name}</strong>
          </div>
          <div className="dispatch-item">
            <Phone aria-hidden="true" size={18} />
            <span>Telefono principal</span>
            <strong>{order.customer.primary_phone ?? "Sin telefono principal"}</strong>
          </div>
          <div className="dispatch-item dispatch-item-wide">
            <MapPin aria-hidden="true" size={18} />
            <span>Direccion</span>
            <strong>{order.address.address}</strong>
            <small>{order.address.reference ?? "Sin referencia"}</small>
          </div>
          <div className="dispatch-item">
            <CalendarClock aria-hidden="true" size={18} />
            <span>Creado</span>
            <strong>{formatDate(order.created_at)}</strong>
          </div>
          <div className="dispatch-item">
            <CircleDollarSign aria-hidden="true" size={18} />
            <span>Total</span>
            <strong className="order-total">${order.total}</strong>
          </div>
        </div>
      </section>

      <section className="panel order-items-panel">
        <header className="panel-header">
          <div>
            <h2>Productos del pedido</h2>
            <p className="panel-description">{order.items.length} items registrados</p>
          </div>
          <ClipboardList aria-hidden="true" size={18} />
        </header>
        <div className="panel-body order-detail-items">
          {order.items.map((item) => (
            <article className="order-detail-item" key={item.id}>
              <div>
                <strong>{item.product_name_snapshot}</strong>
                <span>Cantidad: {item.quantity}</span>
              </div>
              <div className="order-item-price">
                <span>${item.unit_price} c/u</span>
                <strong>${item.line_total}</strong>
              </div>
            </article>
          ))}
        </div>
        <footer className="order-totals">
          <div>
            <span>Subtotal</span>
            <strong>${order.subtotal}</strong>
          </div>
          <div>
            <span>Entrega</span>
            <strong>${order.delivery_fee}</strong>
          </div>
          <div className="order-grand-total">
            <span>Total</span>
            <strong>${order.total}</strong>
          </div>
        </footer>
      </section>

      <section className="panel order-technical-panel">
        <header className="panel-header">
          <h2>Informacion adicional</h2>
        </header>
        <div className="panel-body technical-grid">
          <div>
            <span>Notas</span>
            <strong>{order.notes ?? "Sin notas"}</strong>
          </div>
          <div>
            <span>Canal</span>
            <strong>{order.source_channel}</strong>
          </div>
          <div>
            <span>Confirmado</span>
            <strong>{formatDate(order.confirmed_at)}</strong>
          </div>
          <div>
            <span>Cliente ID</span>
            <strong className="technical-value">{order.customer_id}</strong>
          </div>
          <div>
            <span>Direccion ID</span>
            <strong className="technical-value">{order.address_id}</strong>
          </div>
          <div>
            <span>Ruta ID</span>
            <strong className="technical-value">
              {order.delivery_route_id ?? "Sin ruta asignada"}
            </strong>
          </div>
        </div>
      </section>
    </div>
  );
}
