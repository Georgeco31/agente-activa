"use client";

import { ScanSearch } from "lucide-react";
import { useActionState } from "react";

import { detectDuplicatesAction } from "@/app/customers/actions";
import { DuplicateCandidates } from "@/components/customers/duplicate-candidates";
import { ActionMessage } from "@/components/ui/action-message";
import type { ActionState } from "@/lib/action-state";
import type {
  DuplicateDetectionResult,
} from "@/lib/api/customer-types";

const initialState: ActionState<DuplicateDetectionResult[]> = {
  status: "idle",
  message: "",
};

export function DuplicateDetectionForm() {
  const [state, formAction, pending] = useActionState(
    detectDuplicatesAction,
    initialState,
  );

  return (
    <form action={formAction} className="stack-form">
      <div className="form-heading">
        <span className="form-heading-icon">
          <ScanSearch aria-hidden="true" size={19} />
        </span>
        <div>
          <h3>Detectar duplicados</h3>
          <p>Compara varios datos sin crear un cliente.</p>
        </div>
      </div>

      <div className="form-grid">
        <label className="field">
          <span>Nombre</span>
          <input name="name" />
        </label>
        <label className="field">
          <span>Telefono</span>
          <input name="phone" />
        </label>
        <label className="field">
          <span>Alias</span>
          <input name="alias" />
        </label>
        <label className="field">
          <span>Direccion</span>
          <input name="address" />
        </label>
      </div>
      <label className="field">
        <span>Referencia</span>
        <input name="reference" />
      </label>

      <ActionMessage state={state} />
      {state.status === "success" ? (
        <DuplicateCandidates candidates={state.data} />
      ) : null}

      <button className="button button-secondary" disabled={pending} type="submit">
        {pending ? "Comparando..." : "Buscar coincidencias"}
      </button>
    </form>
  );
}
