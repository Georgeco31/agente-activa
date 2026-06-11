"use client";

import Link from "next/link";
import { UserPlus } from "lucide-react";
import { useActionState } from "react";

import { createCustomerAction } from "@/app/customers/actions";
import { DuplicateCandidates } from "@/components/customers/duplicate-candidates";
import { ActionMessage } from "@/components/ui/action-message";
import type { ActionState } from "@/lib/action-state";
import type {
  Customer,
  DuplicateDetectionResult,
} from "@/lib/api/customer-types";

const initialState: ActionState<Customer> = {
  status: "idle",
  message: "",
};

function duplicateCandidates(
  state: ActionState<Customer>,
): DuplicateDetectionResult[] {
  if (state.status !== "error") {
    return [];
  }

  const candidates = state.error.details.duplicate_candidates;
  return Array.isArray(candidates)
    ? (candidates as DuplicateDetectionResult[])
    : [];
}

export function CustomerCreateForm() {
  const [state, formAction, pending] = useActionState(
    createCustomerAction,
    initialState,
  );
  const candidates = duplicateCandidates(state);

  return (
    <form action={formAction} className="stack-form">
      <div className="form-heading">
        <span className="form-heading-icon">
          <UserPlus aria-hidden="true" size={19} />
        </span>
        <div>
          <h3>Registrar cliente</h3>
          <p>FastAPI validara duplicados y normalizara los datos.</p>
        </div>
      </div>

      <label className="field">
        <span>Nombre *</span>
        <input name="display_name" required />
      </label>
      <div className="form-grid">
        <label className="field">
          <span>Telefono</span>
          <input name="phone" placeholder="0999627968" />
        </label>
        <label className="field">
          <span>Alias</span>
          <input name="alias" />
        </label>
      </div>
      <label className="field">
        <span>Direccion</span>
        <input name="address" />
      </label>
      <label className="field">
        <span>Referencia</span>
        <input name="reference" />
      </label>

      <ActionMessage state={state} />
      <DuplicateCandidates candidates={candidates} />

      {state.status === "success" ? (
        <Link className="button button-secondary" href={`/customers/${state.data.id}`}>
          Ver cliente creado
        </Link>
      ) : null}

      <button className="button button-primary" disabled={pending} type="submit">
        {pending ? "Registrando..." : "Registrar cliente"}
      </button>
    </form>
  );
}
