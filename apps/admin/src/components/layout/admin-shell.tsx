import type { ReactNode } from "react";

import { Header } from "@/components/layout/header";
import { Sidebar } from "@/components/layout/sidebar";

export function AdminShell({
  children,
  username,
}: {
  children: ReactNode;
  username: string;
}) {
  return (
    <div className="app-shell">
      <Sidebar />
      <div className="app-main">
        <Header username={username} />
        <main className="content">{children}</main>
      </div>
    </div>
  );
}
