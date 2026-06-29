"use client";

import { RefreshCw } from "lucide-react";
import { useRouter } from "next/navigation";
import { useTransition } from "react";

export function RefreshButton() {
  const router = useRouter();
  const [isPending, startTransition] = useTransition();

  function refresh() {
    startTransition(() => {
      router.refresh();
    });
  }

  return (
    <button
      className="button button-secondary"
      disabled={isPending}
      onClick={refresh}
      type="button"
    >
      <RefreshCw aria-hidden="true" size={16} />
      {isPending ? "Consultando..." : "Actualizar"}
    </button>
  );
}
