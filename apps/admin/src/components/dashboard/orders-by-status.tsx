import { ListChecks } from "lucide-react";

import type { DashboardStatusCount } from "@/lib/api/dashboard-types";

export function OrdersByStatus({ statuses }: { statuses: DashboardStatusCount[] }) {
  const total = statuses.reduce((sum, status) => sum + status.count, 0);

  return (
    <section className="panel">
      <header className="panel-header">
        <div>
          <h2>Pedidos por estado</h2>
          <p className="panel-description">Distribucion del dia seleccionado</p>
        </div>
        <ListChecks aria-hidden="true" size={18} />
      </header>
      <div className="panel-body dashboard-status-list">
        {statuses.map((status) => {
          const percentage = total > 0 ? Math.round((status.count / total) * 100) : 0;
          return (
            <div className="dashboard-status-item" key={status.code}>
              <div>
                <span>{status.name}</span>
                <strong>{status.count}</strong>
              </div>
              <div className="dashboard-status-track">
                <span style={{ width: `${percentage}%` }} />
              </div>
              <small>{percentage}% del dia</small>
            </div>
          );
        })}
      </div>
    </section>
  );
}
