import Link from "next/link";
import { Filter } from "lucide-react";

import { ORDER_STATUS_OPTIONS } from "@/lib/api/order-types";

export function OrderFilterForm({
  customerId,
  statusCode,
}: {
  customerId: string;
  statusCode: string;
}) {
  return (
    <form action="/orders" className="order-filter-form" method="get">
      <label className="field">
        <span>Cliente ID</span>
        <input
          defaultValue={customerId}
          name="customer_id"
          placeholder="UUID del cliente"
        />
      </label>
      <label className="field">
        <span>Estado</span>
        <select defaultValue={statusCode} name="status_code">
          <option value="">Todos los estados</option>
          {ORDER_STATUS_OPTIONS.map((status) => (
            <option key={status.code} value={status.code}>
              {status.label}
            </option>
          ))}
        </select>
      </label>
      <button className="button button-primary" type="submit">
        <Filter aria-hidden="true" size={16} />
        Aplicar filtros
      </button>
      {customerId || statusCode ? (
        <Link className="button button-secondary" href="/orders">
          Limpiar
        </Link>
      ) : null}
    </form>
  );
}
