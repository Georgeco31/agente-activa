import { Boxes, CalendarClock, CircleDollarSign, PackageCheck } from "lucide-react";

import type { Product } from "@/lib/api/product-types";

function formatDate(value: string): string {
  return new Intl.DateTimeFormat("es-EC", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

export function ProductDetailCard({ product }: { product: Product }) {
  return (
    <section className="panel product-detail-card">
      <header className="panel-header">
        <div>
          <p className="product-sku">{product.sku}</p>
          <h2>{product.name}</h2>
          <p className="panel-description">
            {product.description || "Sin descripcion registrada."}
          </p>
        </div>
        <span
          className={`status-badge ${
            product.is_active ? "status-badge-success" : "status-badge-neutral"
          }`}
        >
          <span className="status-badge-dot" aria-hidden="true" />
          {product.is_active ? "Activo" : "Inactivo"}
        </span>
      </header>

      <div className="panel-body product-meta-grid">
        <div className="product-meta-item">
          <CircleDollarSign aria-hidden="true" size={18} />
          <span>Precio</span>
          <strong className="product-price">${product.price}</strong>
        </div>
        <div className="product-meta-item">
          <PackageCheck aria-hidden="true" size={18} />
          <span>Unidad</span>
          <strong>{product.unit}</strong>
        </div>
        <div className="product-meta-item">
          <Boxes aria-hidden="true" size={18} />
          <span>Nombre normalizado</span>
          <strong>{product.normalized_name}</strong>
        </div>
        <div className="product-meta-item">
          <CalendarClock aria-hidden="true" size={18} />
          <span>Actualizado</span>
          <strong>{formatDate(product.updated_at)}</strong>
          <small>Creado: {formatDate(product.created_at)}</small>
        </div>
      </div>
    </section>
  );
}
