import type { Metadata } from "next";
import Link from "next/link";
import { ClipboardList, Plus } from "lucide-react";

import { OrderFilterForm } from "@/components/orders/order-filter-form";
import { OrderList } from "@/components/orders/order-list";
import { ErrorMessage } from "@/components/ui/error-message";
import { toApiErrorDetail } from "@/lib/api/errors";
import type { Order } from "@/lib/api/order-types";
import { listOrders } from "@/lib/api/orders";
import type { ApiErrorDetail } from "@/lib/api/types";

export const metadata: Metadata = {
  title: "Pedidos",
};

export const dynamic = "force-dynamic";

function singleValue(value: string | string[] | undefined): string {
  return Array.isArray(value) ? (value[0] ?? "") : (value ?? "");
}

export default async function OrdersPage({
  searchParams,
}: {
  searchParams: Promise<{
    customer_id?: string | string[];
    status_code?: string | string[];
  }>;
}) {
  const params = await searchParams;
  const customerId = singleValue(params.customer_id).trim();
  const statusCode = singleValue(params.status_code).trim();

  let orders: Order[] = [];
  let error: ApiErrorDetail | null = null;

  try {
    orders = await listOrders({
      customer_id: customerId || undefined,
      status_code: statusCode || undefined,
    });
  } catch (caughtError) {
    error = toApiErrorDetail(caughtError);
  }

  return (
    <>
      <section className="page-heading">
        <div>
          <p className="eyebrow">Modulo administrativo</p>
          <h1>Pedidos</h1>
          <p className="page-description">
            Consulta informacion util para despacho y administra el ciclo del pedido.
          </p>
        </div>
        <Link className="button button-primary" href="/orders/new">
          <Plus aria-hidden="true" size={16} />
          Crear pedido
        </Link>
      </section>

      <section className="panel">
        <header className="panel-header">
          <div>
            <h2>Listado operativo</h2>
            <p className="panel-description">
              Una sola consulta server-side por render, con datos enriquecidos.
            </p>
          </div>
          <ClipboardList aria-hidden="true" size={18} />
        </header>
        <div className="panel-body">
          <OrderFilterForm customerId={customerId} statusCode={statusCode} />
          {error ? <ErrorMessage error={error} /> : <OrderList orders={orders} />}
        </div>
      </section>
    </>
  );
}
