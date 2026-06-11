import type { LucideIcon } from "lucide-react";
import Link from "next/link";

export function ModulePlaceholder({
  icon: Icon,
  title,
  description,
}: {
  icon: LucideIcon;
  title: string;
  description: string;
}) {
  return (
    <>
      <section className="page-heading">
        <div>
          <p className="eyebrow">Modulo administrativo</p>
          <h1>{title}</h1>
          <p className="page-description">{description}</p>
        </div>
        <span className="status-badge status-badge-neutral">
          <span className="status-badge-dot" aria-hidden="true" />
          Preparado
        </span>
      </section>

      <section className="panel placeholder">
        <div className="placeholder-inner">
          <span className="placeholder-icon">
            <Icon aria-hidden="true" size={24} />
          </span>
          <h2>Estructura lista para crecer</h2>
          <p>
            Esta ruta ya forma parte del panel. Sus flujos administrativos se
            implementaran en los siguientes bloques sin duplicar reglas del backend.
          </p>
          <Link className="button button-secondary" href="/">
            Volver al resumen
          </Link>
        </div>
      </section>
    </>
  );
}
