import "server-only";

import type { ActionState } from "@/lib/action-state";
import { getCurrentSession } from "@/lib/auth/session";

export async function requireActionSession<T>(): Promise<ActionState<T> | null> {
  const session = await getCurrentSession();
  if (session) {
    return null;
  }

  return {
    status: "error",
    message: "Inicia sesion para continuar.",
    error: {
      code: "AUTHENTICATION_REQUIRED",
      message: "Inicia sesion para continuar.",
      details: {},
    },
  };
}
