"use client";

import { PackageOpen } from "lucide-react";
import { useActionState } from "react";

import { updateProductAction } from "@/app/products/actions";
import { ActionMessage } from "@/components/ui/action-message";
import type { ActionState } from "@/lib/action-state";
import type { Product } from "@/lib/api/product-types";

const initialState: ActionState<Product> = {
  status: "idle",
  message: "",
};

export function ProductUpdateForm({ product }: { product: Product }) {
  const [state, formAction, pending] = useActionState(
    updateProductAction.bind(null, product.id),
    initialState,
  );

  return (
    <form action={formAction} className="panel stack-form">
      <div className="form-heading">
        <span className="form-heading-icon">
          <PackageOpen aria-hidden="true" size={18} />
        </span>
        <div>
          <h3>Editar producto</h3>
          <p>Actualiza los campos aceptados por FastAPI.</p>
        </div>
      </div>

      <div className="form-grid">
        <label className="field">
          <span>SKU *</span>
          <input defaultValue={product.sku} maxLength={80} name="sku" required />
        </label>
        <label className="field">
          <span>Nombre *</span>
          <input defaultValue={product.name} maxLength={255} name="name" required />
        </label>
        <label className="field">
          <span>Unidad *</span>
          <input defaultValue={product.unit} maxLength={50} name="unit" required />
        </label>
        <label className="field">
          <span>Precio *</span>
          <input
            defaultValue={product.price}
            min="0"
            name="price"
            required
            step="0.01"
            type="number"
          />
        </label>
      </div>
      <label className="field">
        <span>Descripcion</span>
        <textarea defaultValue={product.description ?? ""} name="description" />
      </label>
      <div className="checkbox-row">
        <label>
          <input defaultChecked={product.is_active} name="is_active" type="checkbox" />
          Producto activo
        </label>
      </div>

      <ActionMessage state={state} />
      <button className="button button-primary" disabled={pending} type="submit">
        {pending ? "Guardando..." : "Guardar cambios"}
      </button>
    </form>
  );
}
