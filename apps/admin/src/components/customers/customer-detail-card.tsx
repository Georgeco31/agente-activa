import { AtSign, MapPin, Phone, UserRound } from "lucide-react";

import { EmptyState } from "@/components/ui/empty-state";
import type { Customer } from "@/lib/api/customer-types";

export function CustomerDetailCard({ customer }: { customer: Customer }) {
  return (
    <div className="customer-detail-grid">
      <section className="panel customer-summary">
        <header className="panel-header">
          <div>
            <p className="eyebrow">Cliente</p>
            <h2>{customer.display_name}</h2>
          </div>
          <span className="status-badge status-badge-success">
            <span className="status-badge-dot" aria-hidden="true" />
            {customer.status}
          </span>
        </header>
        <div className="panel-body summary-data">
          <div>
            <span>Nombre normalizado</span>
            <strong>{customer.normalized_name}</strong>
          </div>
          <div>
            <span>Tipo</span>
            <strong>{customer.customer_type ?? "Sin tipo asignado"}</strong>
          </div>
          <div>
            <span>ID</span>
            <strong className="technical-value">{customer.id}</strong>
          </div>
        </div>
      </section>

      <section className="data-section">
        <div className="data-section-heading">
          <span className="module-icon">
            <Phone aria-hidden="true" size={18} />
          </span>
          <div>
            <h2>Telefonos</h2>
            <p>{customer.phones.length} asociados</p>
          </div>
        </div>
        {customer.phones.length > 0 ? (
          <div className="data-list">
            {customer.phones.map((phone) => (
              <article className="data-item" key={phone.id}>
                <div>
                  <strong>{phone.phone_e164}</strong>
                  <span>{phone.label ?? "Sin etiqueta"}</span>
                </div>
                <div className="tag-row">
                  {phone.is_primary ? <span className="mini-tag">Principal</span> : null}
                  {phone.is_whatsapp ? <span className="mini-tag">WhatsApp</span> : null}
                </div>
              </article>
            ))}
          </div>
        ) : (
          <EmptyState
            description="Este cliente todavia no tiene telefonos asociados."
            icon={Phone}
            title="Sin telefonos"
          />
        )}
      </section>

      <section className="data-section">
        <div className="data-section-heading">
          <span className="module-icon">
            <AtSign aria-hidden="true" size={18} />
          </span>
          <div>
            <h2>Alias</h2>
            <p>{customer.aliases.length} asociados</p>
          </div>
        </div>
        {customer.aliases.length > 0 ? (
          <div className="data-list">
            {customer.aliases.map((alias) => (
              <article className="data-item" key={alias.id}>
                <div>
                  <strong>{alias.alias}</strong>
                  <span>Origen: {alias.source}</span>
                </div>
              </article>
            ))}
          </div>
        ) : (
          <EmptyState
            description="Este cliente todavia no tiene alias asociados."
            icon={UserRound}
            title="Sin alias"
          />
        )}
      </section>

      <section className="data-section data-section-wide">
        <div className="data-section-heading">
          <span className="module-icon">
            <MapPin aria-hidden="true" size={18} />
          </span>
          <div>
            <h2>Direcciones</h2>
            <p>{customer.addresses.length} asociadas</p>
          </div>
        </div>
        {customer.addresses.length > 0 ? (
          <div className="data-list">
            {customer.addresses.map((address) => (
              <article className="data-item data-item-address" key={address.id}>
                <div>
                  <strong>{address.address_text}</strong>
                  <span>{address.reference ?? "Sin referencia"}</span>
                  {address.city || address.neighborhood ? (
                    <small>
                      {[address.neighborhood, address.city].filter(Boolean).join(", ")}
                    </small>
                  ) : null}
                </div>
                {address.is_primary ? <span className="mini-tag">Principal</span> : null}
              </article>
            ))}
          </div>
        ) : (
          <EmptyState
            description="Este cliente todavia no tiene direcciones asociadas."
            icon={MapPin}
            title="Sin direcciones"
          />
        )}
      </section>
    </div>
  );
}
