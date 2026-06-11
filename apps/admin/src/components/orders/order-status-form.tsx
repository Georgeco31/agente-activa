"use client";

import { RefreshCw } from "lucide-react";
import { useActionState } from "react";

import { updateOrderStatusAction } from "@/app/orders/actions";
import { ActionMessage } from "@/components/ui/action-message";
import type { ActionState } from "@/lib/action-state";
import type { Order } from "@/lib/api/order-types";
import { ORDER_STATUS_OPTIONS } from "@/lib/api/order-types";

const initialState: ActionState<Order> = {
  status: "idle",
  message: "",
};

export function OrderStatusForm({ order }: { order: Order }) {
  const [state, formAction, pending] = useActionState(
    updateOrderStatusAction.bind(null, order.id),
    initialState,
  );

  return (
    <form action={formAction} className="panel stack-form">
      <div className="form-heading">
        <span className="form-heading-icon">
          <RefreshCw aria-hidden="true" size={18} />
        </span>
        <div>
          <h3>Cambiar estado</h3>
          <p>FastAPI validara que el pedido todavia admita cambios.</p>
        </div>
      </div>
      <label className="field">
        <span>Nuevo estado</span>
        <select defaultValue={order.status.code} name="status_code" required>
          {ORDER_STATUS_OPTIONS.filter((status) => status.code !== "cancelado").map(
            (status) => (
              <option key={status.code} value={status.code}>
                {status.label}
              </option>
            ),
          )}
        </select>
      </label>
      <ActionMessage state={state} />
      <button className="button button-primary" disabled={pending} type="submit">
        {pending ? "Actualizando..." : "Actualizar estado"}
      </button>
    </form>
  );
}
