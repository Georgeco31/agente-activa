import { SearchX } from "lucide-react";
import Link from "next/link";

export default function NotFound() {
  return (
    <section className="panel placeholder">
      <div className="placeholder-inner">
        <span className="placeholder-icon">
          <SearchX aria-hidden="true" size={24} />
        </span>
        <h1>Pagina no encontrada</h1>
        <p>La ruta solicitada no existe dentro del panel administrativo.</p>
        <div className="not-found-actions">
          <Link className="button button-primary" href="/">
            Ir al resumen
          </Link>
        </div>
      </div>
    </section>
  );
}
