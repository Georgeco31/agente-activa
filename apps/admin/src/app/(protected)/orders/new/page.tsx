import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, Boxes, Search } from "lucide-react";

import { OrderCreateForm } from "@/components/orders/order-create-form";
import {
  OrderCustomerSearch,
  type OrderCustomerSearchField,
} from "@/components/orders/order-customer-search";
import { EmptyState } from "@/components/ui/empty-state";
import { ErrorMessage } from "@/components/ui/error-message";
import type { Customer, CustomerSearchCriteria, CustomerSearchResult } from "@/lib/api/customer-types";
import { getCustomer, searchCustomers } from "@/lib/api/customers";
import { toApiErrorDetail } from "@/lib/api/errors";
import type { Product } from "@/lib/api/product-types";
import { listProducts } from "@/lib/api/products";
import type { ApiErrorDetail } from "@/lib/api/types";

export const metadata: Metadata = {
  title: "Crear pedido",
};

export const dynamic = "force-dynamic";

function singleValue(value: string | string[] | undefined): string {
  return Array.isArray(value) ? (value[0] ?? "") : (value ?? "");
}

function searchField(value: string): OrderCustomerSearchField {
  return value === "phone" || value === "alias" ? value : "name";
}

export default async function NewOrderPage({
  searchParams,
}: {
  searchParams: Promise<{
    field?: string | string[];
    query?: string | string[];
    customer_id?: string | string[];
  }>;
}) {
  const params = await searchParams;
  const field = searchField(singleValue(params.field));
  const query = singleValue(params.query).trim();
  const customerId = singleValue(params.customer_id).trim();

  let results: CustomerSearchResult[] | null = null;
  let searchError: ApiErrorDetail | null = null;
  let customer: Customer | null = null;
  let products: Product[] = [];
  let selectionError: ApiErrorDetail | null = null;

  if (query) {
    try {
      const criteria: CustomerSearchCriteria = { [field]: query };
      results = await searchCustomers(criteria);
    } catch (error) {
      searchError = toApiErrorDetail(error);
    }
  }

  if (customerId) {
    try {
      [customer, products] = await Promise.all([
        getCustomer(customerId),
        listProducts(true),
      ]);
    } catch (error) {
      selectionError = toApiErrorDetail(error);
    }
  }

  const canCreate =
    customer !== null && customer.addresses.length > 0 && products.length > 0;

  return (
    <>
      <section className="page-heading">
        <div>
          <Link className="back-link" href="/orders">
            <ArrowLeft aria-hidden="true" size={15} />
            Volver a pedidos
          </Link>
          <h1>Crear pedido</h1>
          <p className="page-description">
            Selecciona un cliente, una direccion real y productos activos.
          </p>
        </div>
      </section>

      {!customerId ? (
        <section className="panel">
          <header className="panel-header">
            <div>
              <h2>Buscar cliente</h2>
              <p className="panel-description">La busqueda se ejecuta solo al enviar.</p>
            </div>
            <Search aria-hidden="true" size={18} />
          </header>
          <div className="panel-body">
            <OrderCustomerSearch field={field} query={query} results={results} />
            {searchError ? <ErrorMessage error={searchError} /> : null}
          </div>
        </section>
      ) : null}

      {selectionError ? <ErrorMessage error={selectionError} /> : null}

      {customer && customer.addresses.length === 0 ? (
        <section className="panel">
          <EmptyState
            description="Agrega una direccion real al cliente antes de crear el pedido."
            icon={Search}
            title="Cliente sin direcciones"
          />
        </section>
      ) : null}

      {customer && products.length === 0 ? (
        <section className="panel">
          <EmptyState
            description="No existen productos activos disponibles para crear pedidos."
            icon={Boxes}
            title="Sin productos activos"
          />
        </section>
      ) : null}

      {canCreate && customer ? <OrderCreateForm customer={customer} products={products} /> : null}
    </>
  );
}
