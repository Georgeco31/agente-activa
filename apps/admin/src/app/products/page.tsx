import type { Metadata } from "next";
import { Boxes } from "lucide-react";

import { ProductCreateForm } from "@/components/products/product-create-form";
import {
  ProductSearchForm,
  type ProductSearchField,
} from "@/components/products/product-search-form";
import { ProductResults } from "@/components/products/product-results";
import { ErrorMessage } from "@/components/ui/error-message";
import { toApiErrorDetail } from "@/lib/api/errors";
import type { Product } from "@/lib/api/product-types";
import { listProducts, searchProducts } from "@/lib/api/products";
import type { ApiErrorDetail } from "@/lib/api/types";

export const metadata: Metadata = {
  title: "Productos",
};

export const dynamic = "force-dynamic";

function singleValue(value: string | string[] | undefined): string {
  return Array.isArray(value) ? (value[0] ?? "") : (value ?? "");
}

function searchField(value: string): ProductSearchField {
  return value === "sku" ? "sku" : "name";
}

export default async function ProductsPage({
  searchParams,
}: {
  searchParams: Promise<{
    field?: string | string[];
    query?: string | string[];
    active_only?: string | string[];
  }>;
}) {
  const params = await searchParams;
  const field = searchField(singleValue(params.field));
  const query = singleValue(params.query).trim();
  const activeOnly = singleValue(params.active_only) === "true";

  let products: Product[] = [];
  let error: ApiErrorDetail | null = null;

  try {
    products = query
      ? await searchProducts({ [field]: query })
      : await listProducts(activeOnly);
  } catch (caughtError) {
    error = toApiErrorDetail(caughtError);
  }

  return (
    <>
      <section className="page-heading">
        <div>
          <p className="eyebrow">Modulo administrativo</p>
          <h1>Productos</h1>
          <p className="page-description">
            Consulta el catalogo, registra productos y administra su disponibilidad.
          </p>
        </div>
        <span className="status-badge status-badge-success">
          <span className="status-badge-dot" aria-hidden="true" />
          Modulo funcional
        </span>
      </section>

      <section className="panel">
        <header className="panel-header">
          <div>
            <h2>{query ? "Resultados de busqueda" : "Catalogo de productos"}</h2>
            <p className="panel-description">
              La busqueda se ejecuta unicamente al enviar el formulario.
            </p>
          </div>
          <Boxes aria-hidden="true" size={18} />
        </header>
        <div className="panel-body">
          <ProductSearchForm activeOnly={activeOnly} field={field} query={query} />
          {error ? <ErrorMessage error={error} /> : null}
          {!error ? <ProductResults products={products} query={query} /> : null}
        </div>
      </section>

      <section className="section-block">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Catalogo</p>
            <h2>Registrar producto</h2>
          </div>
          <span className="section-note">FastAPI conserva la validacion final</span>
        </div>
        <section className="panel panel-form product-create-panel">
          <ProductCreateForm />
        </section>
      </section>
    </>
  );
}
