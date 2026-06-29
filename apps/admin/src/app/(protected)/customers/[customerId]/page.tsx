import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";

import { CustomerContactForms } from "@/components/customers/customer-contact-forms";
import { CustomerDetailCard } from "@/components/customers/customer-detail-card";
import { ErrorMessage } from "@/components/ui/error-message";
import type { Customer } from "@/lib/api/customer-types";
import { getCustomer } from "@/lib/api/customers";
import { toApiErrorDetail } from "@/lib/api/errors";
import type { ApiErrorDetail } from "@/lib/api/types";

export const metadata: Metadata = {
  title: "Detalle de cliente",
};

export const dynamic = "force-dynamic";

async function loadCustomer(
  customerId: string,
): Promise<{ customer: Customer; error: null } | { customer: null; error: ApiErrorDetail }> {
  try {
    return {
      customer: await getCustomer(customerId),
      error: null,
    };
  } catch (error) {
    return {
      customer: null,
      error: toApiErrorDetail(error),
    };
  }
}

export default async function CustomerDetailPage({
  params,
}: {
  params: Promise<{ customerId: string }>;
}) {
  const { customerId } = await params;
  const result = await loadCustomer(customerId);

  if (result.customer) {
    return (
      <>
        <section className="page-heading">
          <div>
            <Link className="back-link" href="/customers">
              <ArrowLeft aria-hidden="true" size={15} />
              Volver a clientes
            </Link>
            <h1>Detalle de cliente</h1>
            <p className="page-description">
              Consulta y asocia informacion utilizando los servicios reales del backend.
            </p>
          </div>
        </section>

        <CustomerDetailCard customer={result.customer} />
        <CustomerContactForms customerId={result.customer.id} />
      </>
    );
  }

  return (
    <>
      <section className="page-heading">
        <div>
          <Link className="back-link" href="/customers">
            <ArrowLeft aria-hidden="true" size={15} />
            Volver a clientes
          </Link>
          <h1>No fue posible cargar el cliente</h1>
        </div>
      </section>
      <ErrorMessage error={result.error} />
    </>
  );
}
