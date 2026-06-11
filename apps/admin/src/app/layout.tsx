import type { Metadata } from "next";

import { AdminShell } from "@/components/layout/admin-shell";

import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "Agente Activa",
    template: "%s | Agente Activa",
  },
  description: "Panel administrativo para la operacion de venta y reparto de agua.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es">
      <body>
        <AdminShell>{children}</AdminShell>
      </body>
    </html>
  );
}
