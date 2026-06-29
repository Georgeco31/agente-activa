"use server";

import { redirect } from "next/navigation";

import type { ActionState } from "@/lib/action-state";
import { verifyAdminCredentials } from "@/lib/auth/credentials";
import { safeNextPath } from "@/lib/auth/redirects";
import { AuthConfigurationError } from "@/lib/auth/session-token";
import { createSession } from "@/lib/auth/session";

export type LoginActionResult = {
  username: string;
};

function textValue(formData: FormData, key: string): string {
  const value = formData.get(key);
  return typeof value === "string" ? value.trim() : "";
}

function rawTextValue(formData: FormData, key: string): string {
  const value = formData.get(key);
  return typeof value === "string" ? value : "";
}

function errorState(message: string): ActionState<LoginActionResult> {
  return {
    status: "error",
    message,
    error: {
      code: "AUTHENTICATION_FAILED",
      message,
      details: {},
    },
  };
}

export async function loginAction(
  _previousState: ActionState<LoginActionResult>,
  formData: FormData,
): Promise<ActionState<LoginActionResult>> {
  const username = textValue(formData, "username");
  const password = rawTextValue(formData, "password");
  const nextPath = safeNextPath(textValue(formData, "next"));

  if (!username || !password) {
    return errorState("Ingresa usuario y contrasena.");
  }

  try {
    const validCredentials = await verifyAdminCredentials(username, password);
    if (!validCredentials) {
      return errorState("Credenciales invalidas.");
    }

    await createSession(username);
  } catch (error) {
    if (error instanceof AuthConfigurationError) {
      return errorState("La autenticacion del panel no esta configurada.");
    }
    return errorState("No fue posible iniciar sesion.");
  }

  redirect(nextPath);
}
