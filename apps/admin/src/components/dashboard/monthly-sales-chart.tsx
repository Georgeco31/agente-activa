import { BarChart3 } from "lucide-react";

import type { DashboardDailySales } from "@/lib/api/dashboard-types";

function formatMoney(value: string): string {
  return new Intl.NumberFormat("es-EC", {
    style: "currency",
    currency: "USD",
  }).format(Number(value));
}

export function MonthlySalesChart({
  sales,
  monthLabel,
}: {
  sales: DashboardDailySales[];
  monthLabel: string;
}) {
  const maxSales = Math.max(...sales.map((day) => Number(day.sales_total)), 0);

  return (
    <section className="panel dashboard-chart-panel">
      <header className="panel-header">
        <div>
          <h2>Ventas entregadas por dia</h2>
          <p className="panel-description">{monthLabel}</p>
        </div>
        <BarChart3 aria-hidden="true" size={18} />
      </header>
      <div className="panel-body">
        <div
          aria-label={`Grafico de ventas entregadas durante ${monthLabel}`}
          className="monthly-sales-chart"
          role="img"
        >
          <div className="monthly-sales-bars">
            {sales.map((day) => {
              const amount = Number(day.sales_total);
              const height = maxSales > 0 ? Math.max((amount / maxSales) * 100, 3) : 3;
              return (
                <div className="monthly-sales-column" key={day.date}>
                  <div className="monthly-sales-track">
                    <span
                      className={`monthly-sales-bar${amount === 0 ? " monthly-sales-bar-zero" : ""}`}
                      style={{ height: `${height}%` }}
                      title={`${day.date}: ${formatMoney(day.sales_total)}, ${day.delivered_orders_count} pedidos`}
                    />
                  </div>
                  <span>{day.day === 1 || day.day % 5 === 0 ? day.day : ""}</span>
                </div>
              );
            })}
          </div>
          <div className="monthly-sales-legend">
            <span>
              <i aria-hidden="true" />
              Solo pedidos entregados
            </span>
            <strong>Maximo diario: {formatMoney(String(maxSales))}</strong>
          </div>
        </div>
      </div>
    </section>
  );
}
