"use client";

import { LogIn } from "lucide-react";
import { useActionState } from "react";

import { loginAction, type LoginActionResult } from "@/app/login/actions";
import { ActionMessage } from "@/components/ui/action-message";
import type { ActionState } from "@/lib/action-state";

const initialState: ActionState<LoginActionResult> = {
  status: "idle",
  message: "",
};

export function LoginForm({ nextPath }: { nextPath: string }) {
  const [state, formAction, pending] = useActionState(loginAction, initialState);

  return (
    <form action={formAction} className="login-form">
      <input name="next" type="hidden" value={nextPath} />

      <label className="field" htmlFor="username">
        <span>Usuario</span>
        <input
          autoComplete="username"
          id="username"
          name="username"
          placeholder="admin"
          required
          type="text"
        />
      </label>

      <label className="field" htmlFor="password">
        <span>Contrasena</span>
        <input
          autoComplete="current-password"
          id="password"
          name="password"
          required
          type="password"
        />
      </label>

      <ActionMessage state={state} />

      <button className="button button-primary login-button" disabled={pending} type="submit">
        <LogIn aria-hidden="true" size={17} />
        {pending ? "Verificando" : "Ingresar"}
      </button>
    </form>
  );
}
