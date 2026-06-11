"use client";

import Link from "next/link";
import { ClipboardPlus, MapPin, UserRound } from "lucide-react";
import { useActionState } from "react";

import { createOrderAction } from "@/app/orders/actions";
import { OrderItemsEditor } from "@/components/orders/order-items-editor";
import { ActionMessage } from "@/components/ui/action-message";
import type { ActionState } from "@/lib/action-state";
import type { Customer } from "@/lib/api/customer-types";
import type { Order } from "@/lib/api/order-types";
import type { Product } from "@/lib/api/product-types";

const initialState: ActionState<Order> = {
  status: "idle",
  message: "",
};

export function OrderCreateForm({
  customer,
  products,
}: {
  customer: Customer;
  products: Product[];
}) {
  const [state, formAction, pending] = useActionState(createOrderAction, initialState);

  return (
    <form action={formAction} className="panel stack-form order-create-form">
      <input name="customer_id" type="hidden" value={customer.id} />

      <div className="form-heading">
        <span className="form-heading-icon">
          <ClipboardPlus aria-hidden="true" size={18} />
        </span>
        <div>
          <h3>Preparar pedido</h3>
          <p>FastAPI validara cliente, direccion, productos, cantidades y precios.</p>
        </div>
      </div>

      <div className="selected-customer">
        <span className="module-icon">
          <UserRound aria-hidden="true" size={18} />
        </span>
        <div>
          <span>Cliente seleccionado</span>
          <strong>{customer.display_name}</strong>
          <small>{customer.phones.find((phone) => phone.is_primary)?.phone_e164 ?? "Sin telefono principal"}</small>
        </div>
        <Link className="button button-secondary" href="/orders/new">
          Cambiar cliente
        </Link>
      </div>

      <label className="field">
        <span>Direccion de entrega *</span>
        <select defaultValue="" name="address_id" required>
          <option disabled value="">
            Selecciona una direccion real del cliente
          </option>
          {customer.addresses.map((address) => (
            <option key={address.id} value={address.id}>
              {address.address_text}
              {address.reference ? ` - ${address.reference}` : ""}
            </option>
          ))}
        </select>
      </label>

      <div className="selected-address-note">
        <MapPin aria-hidden="true" size={16} />
        La direccion sera validada nuevamente por el backend.
      </div>

      <OrderItemsEditor products={products} />

      <div className="form-grid">
        <label className="field">
          <span>Notas</span>
          <textarea name="notes" />
        </label>
        <label className="field">
          <span>Ruta de reparto ID (opcional)</span>
          <input name="delivery_route_id" placeholder="UUID tecnico, si aplica" />
        </label>
      </div>

      <ActionMessage state={state} />
      {state.status === "success" ? (
        <Link className="button button-secondary" href={`/orders/${state.data.id}`}>
          Ver pedido creado
        </Link>
      ) : null}
      <button className="button button-primary" disabled={pending} type="submit">
        {pending ? "Creando pedido..." : "Crear pedido"}
      </button>
    </form>
  );
}
