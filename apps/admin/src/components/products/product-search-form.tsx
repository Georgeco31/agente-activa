import Link from "next/link";
import { Search } from "lucide-react";

export type ProductSearchField = "name" | "sku";

export function ProductSearchForm({
  activeOnly,
  field,
  query,
}: {
  activeOnly: boolean;
  field: ProductSearchField;
  query: string;
}) {
  return (
    <>
      <form action="/products" className="search-form" method="get">
        <label className="field field-compact">
          <span>Buscar por</span>
          <select defaultValue={field} name="field">
            <option value="name">Nombre</option>
            <option value="sku">SKU</option>
          </select>
        </label>
        <label className="field search-query-field">
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
          <Link className="button button-secondary" href="/products">
            Limpiar
          </Link>
        ) : null}
      </form>
      {!query ? (
        <div className="filter-row" aria-label="Filtros de listado">
          <span>Mostrar:</span>
          <Link
            className={!activeOnly ? "filter-link filter-link-active" : "filter-link"}
            href="/products"
          >
            Todos
          </Link>
          <Link
            className={activeOnly ? "filter-link filter-link-active" : "filter-link"}
            href="/products?active_only=true"
          >
            Solo activos
          </Link>
        </div>
      ) : null}
    </>
  );
}
