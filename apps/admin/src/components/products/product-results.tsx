import Link from "next/link";
import { Boxes, SearchX } from "lucide-react";

import { EmptyState } from "@/components/ui/empty-state";
import type { Product } from "@/lib/api/product-types";

export function ProductResults({
  products,
  query,
}: {
  products: Product[];
  query: string;
}) {
  if (products.length === 0) {
    return (
      <EmptyState
        description={
          query
            ? `No encontramos productos para "${query}".`
            : "No hay productos disponibles para este filtro."
        }
        icon={query ? SearchX : Boxes}
        title={query ? "Sin resultados" : "Sin productos"}
      />
    );
  }

  return (
    <div className="product-list">
      {products.map((product) => (
        <Link className="product-item" href={`/products/${product.id}`} key={product.id}>
          <div className="product-item-main">
            <span className="product-sku">{product.sku}</span>
            <strong>{product.name}</strong>
            <span>
              {product.unit} - ${product.price}
            </span>
          </div>
          <span
            className={`status-badge ${
              product.is_active ? "status-badge-success" : "status-badge-neutral"
            }`}
          >
            <span className="status-badge-dot" aria-hidden="true" />
            {product.is_active ? "Activo" : "Inactivo"}
          </span>
        </Link>
      ))}
    </div>
  );
}
