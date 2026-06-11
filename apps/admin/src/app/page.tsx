import Link from "next/link";
import {
  ArrowRight,
  Boxes,
  ClipboardList,
  Database,
  Server,
  UsersRound,
} from "lucide-react";

export default function Home() {
  const modules = [
    {
      title: "Clientes",
      description: "Consulta y administracion de clientes, telefonos, alias y direcciones.",
      href: "/customers",
      icon: UsersRound,
      status: "Modulo funcional",
    },
    {
      title: "Productos",
      description: "Catalogo operativo, precios y disponibilidad de productos.",
      href: "/products",
      icon: Boxes,
      status: "Modulo funcional",
    },
    {
      title: "Pedidos",
      description: "Registro, consulta y seguimiento de estados de pedidos.",
      href: "/orders",
      icon: ClipboardList,
      status: "Modulo funcional",
    },
  ];

  return (
    <>
      <section className="page-heading">
        <div>
          <p className="eyebrow">Panel administrativo</p>
          <h1>Resumen operativo</h1>
          <p className="page-description">
            Base inicial del panel para gestionar la operacion desde un solo lugar.
          </p>
        </div>
        <Link className="button button-primary" href="/health">
          Ver estado de API
          <ArrowRight aria-hidden="true" size={17} />
        </Link>
      </section>

      <section className="metric-grid" aria-label="Estado de la plataforma">
        <article className="metric-card">
          <span className="metric-icon">
            <Server aria-hidden="true" size={19} />
          </span>
          <div>
            <p>Backend</p>
            <strong>FastAPI</strong>
          </div>
        </article>
        <article className="metric-card">
          <span className="metric-icon">
            <Database aria-hidden="true" size={19} />
          </span>
          <div>
            <p>Datos</p>
            <strong>PostgreSQL</strong>
          </div>
        </article>
        <article className="metric-card">
          <span className="metric-icon">
            <ClipboardList aria-hidden="true" size={19} />
          </span>
          <div>
            <p>Alcance actual</p>
            <strong>Panel base listo</strong>
          </div>
        </article>
      </section>

      <section className="section-block">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Modulos</p>
            <h2>Areas de trabajo</h2>
          </div>
          <span className="section-note">Clientes, productos y pedidos operativos</span>
        </div>
        <div className="module-grid">
          {modules.map((module) => {
            const Icon = module.icon;
            return (
              <Link className="module-card" href={module.href} key={module.title}>
                <div className="module-card-top">
                  <span className="module-icon">
                    <Icon aria-hidden="true" size={21} />
                  </span>
                  <span className="status-chip">{module.status}</span>
                </div>
                <div>
                  <h3>{module.title}</h3>
                  <p>{module.description}</p>
                </div>
                <span className="module-link">
                  Abrir modulo
                  <ArrowRight aria-hidden="true" size={16} />
                </span>
              </Link>
            );
          })}
        </div>
      </section>
    </>
  );
}
