import type { Metadata } from "next";

import { RefreshButton } from "./refresh-button";
import { StatusBadge } from "@/components/status-badge";
import { getHealth } from "@/lib/api/health";

export const metadata: Metadata = {
  title: "Estado de API",
};

export const dynamic = "force-dynamic";

export default async function HealthPage() {
  const result = await getHealth();

  return (
    <>
      <section className="page-heading">
        <div>
          <p className="eyebrow">Diagnostico</p>
          <h1>Estado de la plataforma</h1>
          <p className="page-description">
            Consulta ejecutada desde el servidor de Next.js hacia FastAPI.
          </p>
        </div>
        <StatusBadge
          label={result.ok ? "Servicios disponibles" : "Conexion no disponible"}
          tone={result.ok ? "success" : "danger"}
        />
      </section>

      <section className="panel">
        <header className="panel-header">
          <h2>Healthcheck de FastAPI</h2>
          <RefreshButton />
        </header>
        <div className="panel-body">
          {result.ok ? (
            <div className="health-grid">
              <article className="health-item">
                <span className="health-item-label">API</span>
                <span className="health-item-value">{result.data.status}</span>
              </article>
              <article className="health-item">
                <span className="health-item-label">Base de datos</span>
                <span className="health-item-value">{result.data.database}</span>
              </article>
            </div>
          ) : (
            <div className="error-panel" role="alert">
              <strong>{result.error.code}</strong>
              <p>{result.error.message}</p>
              {Object.keys(result.error.details).length > 0 ? (
                <pre className="error-details">
                  {JSON.stringify(result.error.details, null, 2)}
                </pre>
              ) : null}
            </div>
          )}
        </div>
      </section>
    </>
  );
}
