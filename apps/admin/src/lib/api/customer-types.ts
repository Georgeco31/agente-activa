import type { ApiErrorDetail } from "@/lib/api/types";

export interface CustomerPhone {
  id: string;
  customer_id: string;
  phone_e164: string;
  normalized_phone: string;
  raw_phone: string | null;
  label: string | null;
  is_primary: boolean;
  is_whatsapp: boolean;
}

export interface CustomerAlias {
  id: string;
  customer_id: string;
  alias: string;
  normalized_alias: string;
  source: string;
}

export interface CustomerAddress {
  id: string;
  customer_id: string;
  address_text: string;
  normalized_address: string;
  reference: string | null;
  normalized_reference: string | null;
  label: string | null;
  city: string | null;
  neighborhood: string | null;
  is_primary: boolean;
  notes: string | null;
}

export interface CustomerSearchResult {
  id: string;
  display_name: string;
  normalized_name: string;
  customer_type: string | null;
  status: string;
}

export interface Customer extends CustomerSearchResult {
  phones: CustomerPhone[];
  aliases: CustomerAlias[];
  addresses: CustomerAddress[];
}

export interface DuplicateDetectionResult {
  customer_id: string;
  display_name: string;
  reasons: string[];
  score: number;
  confidence: string;
}

export interface CustomerCreateInput {
  display_name: string;
  phone?: string;
  alias?: string;
  address?: string;
  reference?: string;
  customer_type?: string;
  notes?: string;
}

export interface CustomerRegistrationResponse {
  created: boolean;
  customer: Customer | null;
  duplicate_candidates: DuplicateDetectionResult[];
  message: string;
}

export interface CustomerSearchCriteria {
  phone?: string;
  name?: string;
  alias?: string;
  address?: string;
  reference?: string;
}

export type DuplicateDetectionInput = CustomerSearchCriteria;

export interface AddPhoneInput {
  phone: string;
  label?: string;
  is_primary?: boolean;
  is_whatsapp?: boolean;
}

export interface AddAliasInput {
  alias: string;
  source?: string;
}

export interface AddAddressInput {
  address: string;
  reference?: string;
  label?: string;
  city?: string;
  neighborhood?: string;
  is_primary?: boolean;
  notes?: string;
}

export type CustomerActionState<T = undefined> =
  | {
      status: "idle";
      message: "";
      data?: never;
      error?: never;
    }
  | {
      status: "success";
      message: string;
      data: T;
      error?: never;
    }
  | {
      status: "error";
      message: string;
      data?: never;
      error: ApiErrorDetail;
    };
