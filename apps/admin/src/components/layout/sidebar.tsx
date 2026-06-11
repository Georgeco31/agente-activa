"use client";

import {
  Boxes,
  ClipboardList,
  Droplets,
  Gauge,
  HeartPulse,
  UsersRound,
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

const navigation = [
  { label: "Resumen", href: "/", icon: Gauge },
  { label: "Clientes", href: "/customers", icon: UsersRound },
  { label: "Productos", href: "/products", icon: Boxes },
  { label: "Pedidos", href: "/orders", icon: ClipboardList },
  { label: "Estado API", href: "/health", icon: HeartPulse },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="sidebar">
      <Link className="brand" href="/">
        <span className="brand-mark">
          <Droplets aria-hidden="true" size={20} />
        </span>
        <span className="brand-copy">
          <strong>Agente Activa</strong>
          <span>Panel administrativo</span>
        </span>
      </Link>

      <p className="nav-label">Navegacion</p>
      <nav aria-label="Navegacion principal">
        <ul className="nav-list">
          {navigation.map((item) => {
            const Icon = item.icon;
            const isActive =
              item.href === "/" ? pathname === item.href : pathname.startsWith(item.href);

            return (
              <li key={item.href}>
                <Link
                  aria-current={isActive ? "page" : undefined}
                  className={`nav-link${isActive ? " nav-link-active" : ""}`}
                  href={item.href}
                  title={item.label}
                >
                  <Icon aria-hidden="true" size={18} />
                  <span>{item.label}</span>
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      <p className="sidebar-footer">
        Bloque 6C
        <br />
        Clientes funcional
      </p>
    </aside>
  );
}
