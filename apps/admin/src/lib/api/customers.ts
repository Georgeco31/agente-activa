import "server-only";

import type {
  AddAddressInput,
  AddAliasInput,
  AddPhoneInput,
  Customer,
  CustomerAddress,
  CustomerAlias,
  CustomerCreateInput,
  CustomerPhone,
  CustomerRegistrationResponse,
  CustomerSearchCriteria,
  CustomerSearchResult,
  DuplicateDetectionInput,
  DuplicateDetectionResult,
} from "@/lib/api/customer-types";
import { apiFetch } from "@/lib/api/http";

const CUSTOMERS_PATH = "/api/v1/customers";

function jsonRequest(method: "POST", body: unknown): RequestInit {
  return {
    method,
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  };
}

export function createCustomer(
  input: CustomerCreateInput,
): Promise<CustomerRegistrationResponse> {
  return apiFetch<CustomerRegistrationResponse>(
    CUSTOMERS_PATH,
    jsonRequest("POST", input),
  );
}

export function getCustomer(customerId: string): Promise<Customer> {
  return apiFetch<Customer>(`${CUSTOMERS_PATH}/${customerId}`);
}

export function searchCustomers(
  criteria: CustomerSearchCriteria,
): Promise<CustomerSearchResult[]> {
  const params = new URLSearchParams();

  Object.entries(criteria).forEach(([key, value]) => {
    if (value) {
      params.set(key, value);
    }
  });

  return apiFetch<CustomerSearchResult[]>(
    `${CUSTOMERS_PATH}/search?${params.toString()}`,
  );
}

export function detectDuplicateCustomers(
  input: DuplicateDetectionInput,
): Promise<DuplicateDetectionResult[]> {
  return apiFetch<DuplicateDetectionResult[]>(
    `${CUSTOMERS_PATH}/detect-duplicates`,
    jsonRequest("POST", input),
  );
}

export function addCustomerPhone(
  customerId: string,
  input: AddPhoneInput,
): Promise<CustomerPhone> {
  return apiFetch<CustomerPhone>(
    `${CUSTOMERS_PATH}/${customerId}/phones`,
    jsonRequest("POST", input),
  );
}

export function addCustomerAlias(
  customerId: string,
  input: AddAliasInput,
): Promise<CustomerAlias> {
  return apiFetch<CustomerAlias>(
    `${CUSTOMERS_PATH}/${customerId}/aliases`,
    jsonRequest("POST", input),
  );
}

export function addCustomerAddress(
  customerId: string,
  input: AddAddressInput,
): Promise<CustomerAddress> {
  return apiFetch<CustomerAddress>(
    `${CUSTOMERS_PATH}/${customerId}/addresses`,
    jsonRequest("POST", input),
  );
}
