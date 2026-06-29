import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, LockKeyhole } from "lucide-react";

import { OrderCancelForm } from "@/components/orders/order-cancel-form";
import { OrderDetailCard } from "@/components/orders/order-detail-card";
import { OrderStatusForm } from "@/components/orders/order-status-form";
import { ErrorMessage } from "@/components/ui/error-message";
import { toApiErrorDetail } from "@/lib/api/errors";
import type { Order } from "@/lib/api/order-types";
import { getOrder } from "@/lib/api/orders";
import type { ApiErrorDetail } from "@/lib/api/types";

export const metadata: Metadata = {
  title: "Detalle de pedido",
};

export const dynamic = "force-dynamic";

async function loadOrder(
  orderId: string,
): Promise<{ order: Order; error: null } | { order: null; error: ApiErrorDetail }> {
  try {
    return {
      order: await getOrder(orderId),
      error: null,
    };
  } catch (error) {
    return {
      order: null,
      error: toApiErrorDetail(error),
    };
  }
}

export default async function OrderDetailPage({
  params,
}: {
  params: Promise<{ orderId: string }>;
}) {
  const { orderId } = await params;
  const result = await loadOrder(orderId);

  if (!result.order) {
    return (
      <>
        <section className="page-heading">
          <div>
            <Link className="back-link" href="/orders">
              <ArrowLeft aria-hidden="true" size={15} />
              Volver a pedidos
            </Link>
            <h1>No fue posible cargar el pedido</h1>
          </div>
        </section>
        <ErrorMessage error={result.error} />
      </>
    );
  }

  return (
    <>
      <section className="page-heading">
        <div>
          <Link className="back-link" href="/orders">
            <ArrowLeft aria-hidden="true" size={15} />
            Volver a pedidos
          </Link>
          <h1>Detalle de pedido</h1>
          <p className="page-description">
            Informacion operativa, productos y acciones disponibles.
          </p>
        </div>
      </section>

      <OrderDetailCard order={result.order} />

      <section className="section-block">
        <div className="section-heading">
          <div>
          <p className="eyebrow">Administracion</p>
            <h2>Estado del pedido</h2>
          </div>
          <span className="section-note">FastAPI conserva la decision final</span>
        </div>
        {result.order.status.is_final ? (
          <section className="panel finalized-order-panel">
            <LockKeyhole aria-hidden="true" size={21} />
            <div>
              <h3>Pedido finalizado</h3>
              <p>Este pedido ya no admite cambios de estado ni cancelacion.</p>
            </div>
          </section>
        ) : (
          <div className="order-action-grid">
            <OrderStatusForm order={result.order} />
            <OrderCancelForm order={result.order} />
          </div>
        )}
      </section>
    </>
  );
}
