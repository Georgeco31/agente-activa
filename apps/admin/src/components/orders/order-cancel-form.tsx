"use client";

import { Ban } from "lucide-react";
import { useActionState } from "react";

import { cancelOrderAction } from "@/app/orders/actions";
import { ActionMessage } from "@/components/ui/action-message";
import type { ActionState } from "@/lib/action-state";
import type { Order } from "@/lib/api/order-types";

const initialState: ActionState<Order> = {
  status: "idle",
  message: "",
};

export function OrderCancelForm({ order }: { order: Order }) {
  const [state, formAction, pending] = useActionState(
    cancelOrderAction.bind(null, order.id),
    initialState,
  );

  if (state.status === "success" && state.data.status.is_final) {
    return (
      <section className="panel deactivate-panel">
        <div className="form-heading">
          <span className="form-heading-icon">
            <Ban aria-hidden="true" size={18} />
          </span>
          <div>
            <h3>Pedido cancelado</h3>
            <p>El pedido permanece registrado y ya no admite cambios.</p>
          </div>
        </div>
      </section>
    );
  }

  return (
    <form action={formAction} className="panel stack-form danger-zone">
      <div className="form-heading">
        <span className="form-heading-icon">
          <Ban aria-hidden="true" size={18} />
        </span>
        <div>
          <h3>Cancelar pedido</h3>
          <p>La cancelacion conserva el pedido y utiliza el endpoint especifico.</p>
        </div>
      </div>
      <div className="checkbox-row">
        <label>
          <input name="confirm_cancel" type="checkbox" />
          Confirmo que deseo cancelar este pedido
        </label>
      </div>
      <ActionMessage state={state} />
      <button className="button button-danger" disabled={pending} type="submit">
        {pending ? "Cancelando..." : "Cancelar pedido"}
      </button>
    </form>
  );
}
