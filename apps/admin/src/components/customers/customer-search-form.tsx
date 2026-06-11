import Link from "next/link";
import { Search } from "lucide-react";

export type CustomerSearchField =
  | "phone"
  | "name"
  | "alias"
  | "address"
  | "reference";

const fields: Array<{ value: CustomerSearchField; label: string }> = [
  { value: "name", label: "Nombre" },
  { value: "phone", label: "Telefono" },
  { value: "alias", label: "Alias" },
  { value: "address", label: "Direccion" },
  { value: "reference", label: "Referencia" },
];

export function CustomerSearchForm({
  field,
  query,
}: {
  field: CustomerSearchField;
  query: string;
}) {
  return (
    <form action="/customers" className="search-form" method="get">
      <label className="field field-compact">
        <span>Buscar por</span>
        <select defaultValue={field} name="field">
          {fields.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
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
        <Link className="button button-secondary" href="/customers">
          Limpiar
        </Link>
      ) : null}
    </form>
  );
}
