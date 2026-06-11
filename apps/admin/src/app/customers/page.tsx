import type { Metadata } from "next";
import { Search } from "lucide-react";

import { CustomerCreateForm } from "@/components/customers/customer-create-form";
import {
  CustomerSearchForm,
  type CustomerSearchField,
} from "@/components/customers/customer-search-form";
import { CustomerResults } from "@/components/customers/customer-results";
import { DuplicateDetectionForm } from "@/components/customers/duplicate-detection-form";
import { ErrorMessage } from "@/components/ui/error-message";
import type {
  CustomerSearchCriteria,
  CustomerSearchResult,
} from "@/lib/api/customer-types";
import { searchCustomers } from "@/lib/api/customers";
import { toApiErrorDetail } from "@/lib/api/errors";
import type { ApiErrorDetail } from "@/lib/api/types";

export const metadata: Metadata = {
  title: "Clientes",
};

export const dynamic = "force-dynamic";

const allowedFields: CustomerSearchField[] = [
  "phone",
  "name",
  "alias",
  "address",
  "reference",
];

function singleValue(value: string | string[] | undefined): string {
  return Array.isArray(value) ? (value[0] ?? "") : (value ?? "");
}

function searchField(value: string): CustomerSearchField {
  return allowedFields.includes(value as CustomerSearchField)
    ? (value as CustomerSearchField)
    : "name";
}

export default async function CustomersPage({
  searchParams,
}: {
  searchParams: Promise<{
    field?: string | string[];
    query?: string | string[];
  }>;
}) {
  const params = await searchParams;
  const field = searchField(singleValue(params.field));
  const query = singleValue(params.query).trim();

  let results: CustomerSearchResult[] | null = null;
  let error: ApiErrorDetail | null = null;

  if (query) {
    try {
      const criteria: CustomerSearchCriteria = { [field]: query };
      results = await searchCustomers(criteria);
    } catch (caughtError) {
      error = toApiErrorDetail(caughtError);
    }
  }

  return (
    <>
      <section className="page-heading">
        <div>
          <p className="eyebrow">Modulo administrativo</p>
          <h1>Clientes</h1>
          <p className="page-description">
            Busca clientes, registra nuevos perfiles y revisa posibles duplicados.
          </p>
        </div>
        <span className="status-badge status-badge-success">
          <span className="status-badge-dot" aria-hidden="true" />
          Modulo funcional
        </span>
      </section>

      <section className="panel">
        <header className="panel-header">
          <div>
            <h2>Buscar clientes</h2>
            <p className="panel-description">La consulta se ejecuta solo al presionar Buscar.</p>
          </div>
          <Search aria-hidden="true" size={18} />
        </header>
        <div className="panel-body">
          <CustomerSearchForm field={field} query={query} />
          {error ? <ErrorMessage error={error} /> : null}
          {!error ? <CustomerResults query={query} results={results} /> : null}
        </div>
      </section>

      <section className="section-block">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Registro seguro</p>
            <h2>Crear o comparar clientes</h2>
          </div>
          <span className="section-note">El backend conserva la decision final</span>
        </div>
        <div className="customer-tool-grid">
          <section className="panel panel-form">
            <CustomerCreateForm />
          </section>
          <section className="panel panel-form">
            <DuplicateDetectionForm />
          </section>
        </div>
      </section>
    </>
  );
}
