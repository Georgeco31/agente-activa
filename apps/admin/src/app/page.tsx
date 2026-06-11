import type { Metadata } from "next";
import {
  Ban,
  CheckCircle2,
  CircleDollarSign,
  Clock3,
  PackageCheck,
  Route,
  ShoppingCart,
} from "lucide-react";

import { DashboardPeriodFilter } from "@/components/dashboard/dashboard-period-filter";
import { MonthlySalesChart } from "@/components/dashboard/monthly-sales-chart";
import { OperationalAlerts } from "@/components/dashboard/operational-alerts";
import { OrdersByStatus } from "@/components/dashboard/orders-by-status";
import { RecentOrders } from "@/components/dashboard/recent-orders";
import { SummaryCard } from "@/components/dashboard/summary-card";
import { ErrorMessage } from "@/components/ui/error-message";
import { getDashboardOverview } from "@/lib/api/dashboard";
import type { DashboardOverview } from "@/lib/api/dashboard-types";
import { toApiErrorDetail } from "@/lib/api/errors";
import type { ApiErrorDetail } from "@/lib/api/types";

export const metadata: Metadata = {
  title: "Dashboard operativo",
};

export const dynamic = "force-dynamic";

function singleValue(value: string | string[] | undefined): string {
  return Array.isArray(value) ? (value[0] ?? "") : (value ?? "");
}

function validPeriod(value: string): { year: number; month: number } | null {
  const match = /^(\d{4})-(\d{2})$/.exec(value);
  if (!match) {
    return null;
  }
  const year = Number(match[1]);
  const month = Number(match[2]);
  return month >= 1 && month <= 12 ? { year, month } : null;
}

function formatMoney(value: string): string {
  return new Intl.NumberFormat("es-EC", {
    style: "currency",
    currency: "USD",
  }).format(Number(value));
}

function formatSelectedDate(value: string): string {
  return new Intl.DateTimeFormat("es-EC", { dateStyle: "full", timeZone: "UTC" }).format(
    new Date(`${value}T00:00:00Z`),
  );
}

function formatMonth(year: number, month: number): string {
  return new Intl.DateTimeFormat("es-EC", {
    month: "long",
    year: "numeric",
    timeZone: "UTC",
  }).format(new Date(Date.UTC(year, month - 1, 1)));
}

function operationMessage(overview: DashboardOverview): string {
  if (overview.summary.pending_orders > 0) {
    return `${overview.summary.pending_orders} pedidos pendientes requieren seguimiento.`;
  }
  if (overview.summary.en_route_orders > 0) {
    return `${overview.summary.en_route_orders} pedidos estan en camino.`;
  }
  return "La operacion no tiene pedidos pendientes para la fecha seleccionada.";
}

export default async function DashboardPage({
  searchParams,
}: {
  searchParams: Promise<{
    date?: string | string[];
    period?: string | string[];
  }>;
}) {
  const params = await searchParams;
  const selectedDate = singleValue(params.date).trim();
  const selectedPeriod = singleValue(params.period).trim();
  const period = validPeriod(selectedPeriod);

  let overview: DashboardOverview | null = null;
  let error: ApiErrorDetail | null = null;

  try {
    overview = await getDashboardOverview({
      date: selectedDate || undefined,
      year: period?.year,
      month: period?.month,
    });
  } catch (caughtError) {
    error = toApiErrorDetail(caughtError);
  }

  if (!overview) {
    return (
      <>
        <section className="page-heading">
          <div>
            <p className="eyebrow">Operacion administrativa</p>
            <h1>Dashboard operativo</h1>
            <p className="page-description">
              Una sola consulta server-side concentra el estado del negocio.
            </p>
          </div>
        </section>
        {error ? <ErrorMessage error={error} /> : null}
      </>
    );
  }

  const periodValue = `${overview.year}-${String(overview.month).padStart(2, "0")}`;
  const monthLabel = formatMonth(overview.year, overview.month);

  return (
    <>
      <section className="page-heading dashboard-heading">
        <div>
          <p className="eyebrow">Operacion administrativa</p>
          <h1>Dashboard operativo</h1>
          <p className="page-description">
            {formatSelectedDate(overview.selected_date)}. {operationMessage(overview)}
          </p>
        </div>
        <div className="dashboard-context">
          <span>Base operativa</span>
          <strong>
            {overview.summary.total_customers} clientes · {overview.summary.active_products} productos
          </strong>
        </div>
      </section>

      <DashboardPeriodFilter selectedDate={overview.selected_date} period={periodValue} />

      <section className="dashboard-summary-grid" aria-label="Resumen operativo">
        <SummaryCard
          icon={ShoppingCart}
          label="Pedidos del dia"
          supportingText="Todos los estados"
          value={String(overview.summary.orders_today)}
        />
        <SummaryCard
          icon={Clock3}
          label="Pendientes"
          supportingText="Requieren atencion"
          tone="warning"
          value={String(overview.summary.pending_orders)}
        />
        <SummaryCard
          icon={Route}
          label="En camino"
          supportingText="Despachos activos"
          value={String(overview.summary.en_route_orders)}
        />
        <SummaryCard
          icon={CheckCircle2}
          label="Entregados"
          supportingText="Ventas realizadas"
          tone="success"
          value={String(overview.summary.delivered_orders)}
        />
        <SummaryCard
          icon={Ban}
          label="Cancelados"
          supportingText="No cuentan como venta"
          tone="neutral"
          value={String(overview.summary.cancelled_orders)}
        />
        <SummaryCard
          icon={CircleDollarSign}
          label="Ventas del dia"
          supportingText="Solo entregados"
          tone="success"
          value={formatMoney(overview.summary.sales_total_today)}
        />
        <SummaryCard
          icon={PackageCheck}
          label="Ventas del mes"
          supportingText={monthLabel}
          tone="blue"
          value={formatMoney(overview.summary.sales_total_month)}
        />
      </section>

      <section className="dashboard-main-grid">
        <MonthlySalesChart monthLabel={monthLabel} sales={overview.monthly_sales} />
        <OperationalAlerts alerts={overview.alerts} />
        <OrdersByStatus statuses={overview.orders_by_status} />
        <RecentOrders orders={overview.recent_orders} />
      </section>

      <p className="dashboard-sales-note">
        Las ventas se calculan con pedidos cuyo estado actual es entregado y cuya fecha de
        creacion pertenece al periodo seleccionado. Todavia no existe una fecha de entrega
        historica.
      </p>
    </>
  );
}
