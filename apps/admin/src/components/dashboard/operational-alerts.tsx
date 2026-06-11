import Link from "next/link";
import { BellRing, CheckCircle2 } from "lucide-react";

import type { DashboardAlert } from "@/lib/api/dashboard-types";

export function OperationalAlerts({ alerts }: { alerts: DashboardAlert[] }) {
  return (
    <section className="panel">
      <header className="panel-header">
        <div>
          <h2>Alertas operativas</h2>
          <p className="panel-description">Atencion requerida durante el dia</p>
        </div>
        <BellRing aria-hidden="true" size={18} />
      </header>
      {alerts.length === 0 ? (
        <div className="dashboard-alerts-empty">
          <CheckCircle2 aria-hidden="true" size={21} />
          <div>
            <strong>Operacion al dia</strong>
            <p>No hay alertas para el periodo seleccionado.</p>
          </div>
        </div>
      ) : (
        <div className="dashboard-alert-list">
          {alerts.map((alert) => (
            <Link
              className={`dashboard-alert dashboard-alert-${alert.severity}`}
              href={`/orders?status_code=${alert.status_code}`}
              key={alert.code}
            >
              <div>
                <strong>{alert.label}</strong>
                <span>Revisar listado operativo</span>
              </div>
              <b>{alert.count}</b>
            </Link>
          ))}
        </div>
      )}
    </section>
  );
}
