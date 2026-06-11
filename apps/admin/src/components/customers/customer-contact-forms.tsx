"use client";

import { AtSign, MapPin, Phone } from "lucide-react";
import { useActionState } from "react";

import {
  addAddressAction,
  addAliasAction,
  addPhoneAction,
} from "@/app/customers/actions";
import { ActionMessage } from "@/components/ui/action-message";
import type { ActionState } from "@/lib/action-state";
import type {
  CustomerAddress,
  CustomerAlias,
  CustomerPhone,
} from "@/lib/api/customer-types";

const initialPhoneState: ActionState<CustomerPhone> = {
  status: "idle",
  message: "",
};
const initialAliasState: ActionState<CustomerAlias> = {
  status: "idle",
  message: "",
};
const initialAddressState: ActionState<CustomerAddress> = {
  status: "idle",
  message: "",
};

export function CustomerContactForms({ customerId }: { customerId: string }) {
  const [phoneState, phoneFormAction, phonePending] = useActionState(
    addPhoneAction.bind(null, customerId),
    initialPhoneState,
  );
  const [aliasState, aliasFormAction, aliasPending] = useActionState(
    addAliasAction.bind(null, customerId),
    initialAliasState,
  );
  const [addressState, addressFormAction, addressPending] = useActionState(
    addAddressAction.bind(null, customerId),
    initialAddressState,
  );

  return (
    <section className="section-block">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Asociar datos</p>
          <h2>Agregar informacion al cliente</h2>
        </div>
        <span className="section-note">Cada cambio se valida en FastAPI</span>
      </div>

      <div className="contact-form-grid">
        <form action={phoneFormAction} className="panel stack-form">
          <div className="form-heading">
            <span className="form-heading-icon">
              <Phone aria-hidden="true" size={18} />
            </span>
            <div>
              <h3>Nuevo telefono</h3>
              <p>Se normalizara a E.164.</p>
            </div>
          </div>
          <label className="field">
            <span>Telefono *</span>
            <input name="phone" required />
          </label>
          <label className="field">
            <span>Etiqueta</span>
            <input name="label" placeholder="trabajo, personal..." />
          </label>
          <div className="checkbox-row">
            <label>
              <input name="is_primary" type="checkbox" />
              Principal
            </label>
            <label>
              <input defaultChecked name="is_whatsapp" type="checkbox" />
              WhatsApp
            </label>
          </div>
          <ActionMessage state={phoneState} />
          <button className="button button-primary" disabled={phonePending} type="submit">
            {phonePending ? "Agregando..." : "Agregar telefono"}
          </button>
        </form>

        <form action={aliasFormAction} className="panel stack-form">
          <div className="form-heading">
            <span className="form-heading-icon">
              <AtSign aria-hidden="true" size={18} />
            </span>
            <div>
              <h3>Nuevo alias</h3>
              <p>Facilita futuras busquedas.</p>
            </div>
          </div>
          <label className="field">
            <span>Alias *</span>
            <input name="alias" required />
          </label>
          <ActionMessage state={aliasState} />
          <button className="button button-primary" disabled={aliasPending} type="submit">
            {aliasPending ? "Agregando..." : "Agregar alias"}
          </button>
        </form>

        <form action={addressFormAction} className="panel stack-form contact-form-wide">
          <div className="form-heading">
            <span className="form-heading-icon">
              <MapPin aria-hidden="true" size={18} />
            </span>
            <div>
              <h3>Nueva direccion</h3>
              <p>Incluye referencias utiles para reparto.</p>
            </div>
          </div>
          <div className="form-grid">
            <label className="field">
              <span>Direccion *</span>
              <input name="address" required />
            </label>
            <label className="field">
              <span>Referencia</span>
              <input name="reference" />
            </label>
            <label className="field">
              <span>Etiqueta</span>
              <input name="label" placeholder="casa, oficina..." />
            </label>
            <label className="field">
              <span>Ciudad</span>
              <input name="city" />
            </label>
            <label className="field">
              <span>Barrio</span>
              <input name="neighborhood" />
            </label>
            <label className="field">
              <span>Observaciones</span>
              <input name="notes" />
            </label>
          </div>
          <div className="checkbox-row">
            <label>
              <input name="is_primary" type="checkbox" />
              Direccion principal
            </label>
          </div>
          <ActionMessage state={addressState} />
          <button className="button button-primary" disabled={addressPending} type="submit">
            {addressPending ? "Agregando..." : "Agregar direccion"}
          </button>
        </form>
      </div>
    </section>
  );
}
