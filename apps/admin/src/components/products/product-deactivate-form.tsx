"use client";

import { ArchiveX } from "lucide-react";
import { useActionState } from "react";

import { deactivateProductAction } from "@/app/products/actions";
import { ActionMessage } from "@/components/ui/action-message";
import type { ActionState } from "@/lib/action-state";
import type { Product, ProductDeactivateResult } from "@/lib/api/product-types";

const initialState: ActionState<ProductDeactivateResult> = {
  status: "idle",
  message: "",
};

export function ProductDeactivateForm({ product }: { product: Product }) {
  const [state, formAction, pending] = useActionState(
    deactivateProductAction.bind(null, product.id),
    initialState,
  );

  if (!product.is_active || (state.status === "success" && !state.data.is_active)) {
    return (
      <section className="panel deactivate-panel">
        <div className="form-heading">
          <span className="form-heading-icon">
            <ArchiveX aria-hidden="true" size={18} />
          </span>
          <div>
            <h3>Producto inactivo</h3>
            <p>Este producto ya no aparece al filtrar solo activos.</p>
          </div>
        </div>
      </section>
    );
  }

  return (
    <form action={formAction} className="panel stack-form danger-zone">
      <div className="form-heading">
        <span className="form-heading-icon">
          <ArchiveX aria-hidden="true" size={18} />
        </span>
        <div>
          <h3>Desactivar producto</h3>
          <p>La desactivacion conserva el registro y su historial.</p>
        </div>
      </div>
      <div className="checkbox-row">
        <label>
          <input name="confirm_deactivate" type="checkbox" />
          Confirmo que deseo desactivar este producto
        </label>
      </div>
      <ActionMessage state={state} />
      <button className="button button-danger" disabled={pending} type="submit">
        {pending ? "Desactivando..." : "Desactivar producto"}
      </button>
    </form>
  );
}
