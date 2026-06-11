"use client";

import { AlertTriangle } from "lucide-react";

export default function ErrorPage({ reset }: { reset: () => void }) {
  return (
    <section className="panel placeholder">
      <div className="placeholder-inner">
        <span className="placeholder-icon">
          <AlertTriangle aria-hidden="true" size={24} />
        </span>
        <h1>No fue posible cargar esta vista</h1>
        <p>
          Ocurrio un error inesperado en el panel. No se muestran detalles internos
          por seguridad.
        </p>
        <button className="button button-primary" onClick={reset} type="button">
          Intentar nuevamente
        </button>
      </div>
    </section>
  );
}
