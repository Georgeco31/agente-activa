import type { ReactNode } from "react";

import { AdminShell } from "@/components/layout/admin-shell";
import { requireSession } from "@/lib/auth/session";

export default async function ProtectedLayout({ children }: { children: ReactNode }) {
  const session = await requireSession();

  return <AdminShell username={session.username}>{children}</AdminShell>;
}
