import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";

import { ProductDeactivateForm } from "@/components/products/product-deactivate-form";
import { ProductDetailCard } from "@/components/products/product-detail-card";
import { ProductUpdateForm } from "@/components/products/product-update-form";
import { ErrorMessage } from "@/components/ui/error-message";
import { toApiErrorDetail } from "@/lib/api/errors";
import type { Product } from "@/lib/api/product-types";
import { getProduct } from "@/lib/api/products";
import type { ApiErrorDetail } from "@/lib/api/types";

export const metadata: Metadata = {
  title: "Detalle de producto",
};

export const dynamic = "force-dynamic";

async function loadProduct(
  productId: string,
): Promise<{ product: Product; error: null } | { product: null; error: ApiErrorDetail }> {
  try {
    return {
      product: await getProduct(productId),
      error: null,
    };
  } catch (error) {
    return {
      product: null,
      error: toApiErrorDetail(error),
    };
  }
}

export default async function ProductDetailPage({
  params,
}: {
  params: Promise<{ productId: string }>;
}) {
  const { productId } = await params;
  const result = await loadProduct(productId);

  if (result.product) {
    return (
      <>
        <section className="page-heading">
          <div>
            <Link className="back-link" href="/products">
              <ArrowLeft aria-hidden="true" size={15} />
              Volver a productos
            </Link>
            <h1>Detalle de producto</h1>
            <p className="page-description">
              Consulta, actualiza o desactiva el producto mediante FastAPI.
            </p>
          </div>
        </section>

        <ProductDetailCard product={result.product} />
        <section className="section-block">
          <div className="section-heading">
            <div>
              <p className="eyebrow">Administracion</p>
              <h2>Editar disponibilidad y datos</h2>
            </div>
            <span className="section-note">No se realiza borrado fisico</span>
          </div>
          <div className="product-action-grid">
            <ProductUpdateForm product={result.product} />
            <ProductDeactivateForm product={result.product} />
          </div>
        </section>
      </>
    );
  }

  return (
    <>
      <section className="page-heading">
        <div>
          <Link className="back-link" href="/products">
            <ArrowLeft aria-hidden="true" size={15} />
            Volver a productos
          </Link>
          <h1>No fue posible cargar el producto</h1>
        </div>
      </section>
      <ErrorMessage error={result.error} />
    </>
  );
}
