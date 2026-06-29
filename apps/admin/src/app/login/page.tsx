import type { Metadata } from "next";
import { ShieldCheck } from "lucide-react";
import { redirect } from "next/navigation";

import { LoginForm } from "@/components/auth/login-form";
import { getCurrentSession } from "@/lib/auth/session";
import { safeNextPath } from "@/lib/auth/redirects";

export const metadata: Metadata = {
  title: "Ingreso administrativo",
};

function singleValue(value: string | string[] | undefined): string {
  return Array.isArray(value) ? (value[0] ?? "") : (value ?? "");
}

export default async function LoginPage({
  searchParams,
}: {
  searchParams: Promise<{ next?: string | string[] }>;
}) {
  const session = await getCurrentSession();
  if (session) {
    redirect("/");
  }

  const params = await searchParams;
  const nextPath = safeNextPath(singleValue(params.next));

  return (
    <main className="login-page">
      <section className="login-panel" aria-labelledby="login-title">
        <div className="login-brand">
          <span className="login-brand-mark">
            <ShieldCheck aria-hidden="true" size={24} />
          </span>
          <div>
            <p className="eyebrow">Panel protegido</p>
            <h1 id="login-title">Agente Activa</h1>
            <p className="page-description">
              Ingresa con las credenciales administrativas configuradas para este entorno.
            </p>
          </div>
        </div>

        <LoginForm nextPath={nextPath} />
      </section>
    </main>
  );
}
