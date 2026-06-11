import Link from "next/link";
import { Search, UserRoundSearch } from "lucide-react";

import { EmptyState } from "@/components/ui/empty-state";
import type { CustomerSearchResult } from "@/lib/api/customer-types";

export function CustomerResults({
  query,
  results,
}: {
  query: string;
  results: CustomerSearchResult[] | null;
}) {
  if (results === null) {
    return (
      <EmptyState
        description="La API solo se consultara cuando envies el formulario de busqueda."
        icon={Search}
        title="Busca un cliente"
      />
    );
  }

  if (results.length === 0) {
    return (
      <EmptyState
        description={`No encontramos clientes para "${query}".`}
        icon={UserRoundSearch}
        title="Sin resultados"
      />
    );
  }

  return (
    <div className="result-list">
      {results.map((customer) => (
        <Link
          className="result-item"
          href={`/customers/${customer.id}`}
          key={customer.id}
        >
          <div>
            <strong>{customer.display_name}</strong>
            <span>{customer.customer_type ?? "Cliente sin tipo asignado"}</span>
          </div>
          <span className="status-badge status-badge-success">
            <span className="status-badge-dot" aria-hidden="true" />
            {customer.status}
          </span>
        </Link>
      ))}
    </div>
  );
}
