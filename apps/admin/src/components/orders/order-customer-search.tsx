import Link from "next/link";
import { Search, UserRoundSearch } from "lucide-react";

import { EmptyState } from "@/components/ui/empty-state";
import type { CustomerSearchResult } from "@/lib/api/customer-types";

export type OrderCustomerSearchField = "phone" | "name" | "alias";

export function OrderCustomerSearch({
  field,
  query,
  results,
}: {
  field: OrderCustomerSearchField;
  query: string;
  results: CustomerSearchResult[] | null;
}) {
  return (
    <>
      <form action="/orders/new" className="search-form" method="get">
        <label className="field">
          <span>Buscar cliente por</span>
          <select defaultValue={field} name="field">
            <option value="name">Nombre</option>
            <option value="phone">Telefono</option>
            <option value="alias">Alias</option>
          </select>
        </label>
        <label className="field">
          <span>Criterio</span>
          <input
            defaultValue={query}
            name="query"
            placeholder="Escribe un dato y presiona Buscar"
            required
            type="search"
          />
        </label>
        <button className="button button-primary" type="submit">
          <Search aria-hidden="true" size={16} />
          Buscar
        </button>
        {query ? (
          <Link className="button button-secondary" href="/orders/new">
            Limpiar
          </Link>
        ) : null}
      </form>

      {results === null ? (
        <EmptyState
          description="Busca y selecciona un cliente antes de preparar el pedido."
          icon={Search}
          title="Selecciona un cliente"
        />
      ) : null}
      {results?.length === 0 ? (
        <EmptyState
          description={`No encontramos clientes para "${query}".`}
          icon={UserRoundSearch}
          title="Sin resultados"
        />
      ) : null}
      {results && results.length > 0 ? (
        <div className="result-list">
          {results.map((customer) => (
            <Link
              className="result-item"
              href={`/orders/new?customer_id=${customer.id}`}
              key={customer.id}
            >
              <div>
                <strong>{customer.display_name}</strong>
                <span>{customer.customer_type ?? "Cliente sin tipo asignado"}</span>
              </div>
              <span className="button button-secondary">Seleccionar</span>
            </Link>
          ))}
        </div>
      ) : null}
    </>
  );
}
