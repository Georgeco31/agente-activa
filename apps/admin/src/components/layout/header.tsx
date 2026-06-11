export function Header() {
  return (
    <header className="topbar">
      <div>
        <p className="topbar-title">Operacion administrativa</p>
        <p className="topbar-context">Venta y reparto de agua</p>
      </div>
      <span className="environment-badge">
        <span className="environment-dot" aria-hidden="true" />
        Entorno local
      </span>
    </header>
  );
}
