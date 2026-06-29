import { LogOut } from "lucide-react";

export function Header({ username }: { username: string }) {
  return (
    <header className="topbar">
      <div>
        <p className="topbar-title">Operacion administrativa</p>
        <p className="topbar-context">Venta y reparto de agua</p>
      </div>
      <div className="topbar-actions">
        <span className="environment-badge">
          <span className="environment-dot" aria-hidden="true" />
          {username}
        </span>
        <form action="/logout" method="post">
          <button className="button button-secondary topbar-logout" type="submit">
            <LogOut aria-hidden="true" size={16} />
            Salir
          </button>
        </form>
      </div>
    </header>
  );
}
