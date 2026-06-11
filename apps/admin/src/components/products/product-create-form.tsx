"use client";

import Link from "next/link";
import { PackagePlus } from "lucide-react";
import { useActionState } from "react";

import { createProductAction } from "@/app/products/actions";
import { ActionMessage } from "@/components/ui/action-message";
import type { ActionState } from "@/lib/action-state";
import type { Product } from "@/lib/api/product-types";

const initialState: ActionState<Product> = {
  status: "idle",
  message: "",
};

export function ProductCreateForm() {
  const [state, formAction, pending] = useActionState(
    createProductAction,
    initialState,
  );

  return (
    <form action={formAction} className="stack-form">
      <div className="form-heading">
        <span className="form-heading-icon">
          <PackagePlus aria-hidden="true" size={19} />
        </span>
        <div>
          <h3>Registrar producto</h3>
          <p>FastAPI validara SKU, precio y datos requeridos.</p>
        </div>
      </div>

      <div className="form-grid">
        <label className="field">
          <span>SKU *</span>
          <input maxLength={80} name="sku" required />
        </label>
        <label className="field">
          <span>Nombre *</span>
          <input maxLength={255} name="name" required />
        </label>
        <label className="field">
          <span>Unidad *</span>
          <input maxLength={50} name="unit" placeholder="botellon, unidad..." required />
        </label>
        <label className="field">
          <span>Precio *</span>
          <input min="0" name="price" required step="0.01" type="number" />
        </label>
      </div>
      <label className="field">
        <span>Descripcion</span>
        <textarea name="description" />
      </label>
      <div className="checkbox-row">
        <label>
          <input defaultChecked name="is_active" type="checkbox" />
          Producto activo
        </label>
      </div>

      <ActionMessage state={state} />
      {state.status === "success" ? (
        <Link className="button button-secondary" href={`/products/${state.data.id}`}>
          Ver producto creado
        </Link>
      ) : null}

      <button className="button button-primary" disabled={pending} type="submit">
        {pending ? "Registrando..." : "Registrar producto"}
      </button>
    </form>
  );
}
