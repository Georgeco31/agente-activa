"use server";

import { revalidatePath } from "next/cache";

import type { ActionState } from "@/lib/action-state";
import type {
  AddAddressInput,
  AddAliasInput,
  AddPhoneInput,
  Customer,
  CustomerAddress,
  CustomerAlias,
  CustomerCreateInput,
  CustomerPhone,
  DuplicateDetectionInput,
  DuplicateDetectionResult,
} from "@/lib/api/customer-types";
import {
  addCustomerAddress,
  addCustomerAlias,
  addCustomerPhone,
  createCustomer,
  detectDuplicateCustomers,
} from "@/lib/api/customers";
import { toApiErrorDetail } from "@/lib/api/errors";
import { requireActionSession } from "@/lib/auth/action-guard";

function optionalText(formData: FormData, key: string): string | undefined {
  const value = formData.get(key);
  if (typeof value !== "string") {
    return undefined;
  }

  const trimmed = value.trim();
  return trimmed || undefined;
}

function checkboxValue(formData: FormData, key: string): boolean {
  return formData.get(key) === "on";
}

function validationError<T>(
  field: string,
  message: string,
): ActionState<T> {
  return {
    status: "error",
    message,
    error: {
      code: "VALIDATION_ERROR",
      message,
      details: {
        errors: [{ field, message, type: "required" }],
      },
    },
  };
}

function apiErrorState<T>(error: unknown): ActionState<T> {
  const detail = toApiErrorDetail(error);
  return {
    status: "error",
    message: detail.message,
    error: detail,
  };
}

export async function createCustomerAction(
  _previousState: ActionState<Customer>,
  formData: FormData,
): Promise<ActionState<Customer>> {
  const authError = await requireActionSession<Customer>();
  if (authError) {
    return authError;
  }

  const displayName = optionalText(formData, "display_name");
  if (!displayName) {
    return validationError("display_name", "El nombre es obligatorio.");
  }

  const input: CustomerCreateInput = {
    display_name: displayName,
    phone: optionalText(formData, "phone"),
    alias: optionalText(formData, "alias"),
    address: optionalText(formData, "address"),
    reference: optionalText(formData, "reference"),
  };

  try {
    const result = await createCustomer(input);
    if (!result.customer) {
      return validationError("display_name", result.message);
    }

    revalidatePath("/customers");
    return {
      status: "success",
      message: "Cliente creado correctamente.",
      data: result.customer,
    };
  } catch (error) {
    return apiErrorState(error);
  }
}

export async function detectDuplicatesAction(
  _previousState: ActionState<DuplicateDetectionResult[]>,
  formData: FormData,
): Promise<ActionState<DuplicateDetectionResult[]>> {
  const authError = await requireActionSession<DuplicateDetectionResult[]>();
  if (authError) {
    return authError;
  }

  const input: DuplicateDetectionInput = {
    name: optionalText(formData, "name"),
    phone: optionalText(formData, "phone"),
    alias: optionalText(formData, "alias"),
    address: optionalText(formData, "address"),
    reference: optionalText(formData, "reference"),
  };

  if (!Object.values(input).some(Boolean)) {
    return validationError("duplicate_detection", "Ingresa al menos un criterio.");
  }

  try {
    const candidates = await detectDuplicateCustomers(input);
    return {
      status: "success",
      message:
        candidates.length > 0
          ? "Se encontraron posibles coincidencias."
          : "No se encontraron coincidencias.",
      data: candidates,
    };
  } catch (error) {
    return apiErrorState(error);
  }
}

export async function addPhoneAction(
  customerId: string,
  _previousState: ActionState<CustomerPhone>,
  formData: FormData,
): Promise<ActionState<CustomerPhone>> {
  const authError = await requireActionSession<CustomerPhone>();
  if (authError) {
    return authError;
  }

  const phone = optionalText(formData, "phone");
  if (!phone) {
    return validationError("phone", "El telefono es obligatorio.");
  }

  const input: AddPhoneInput = {
    phone,
    label: optionalText(formData, "label"),
    is_primary: checkboxValue(formData, "is_primary"),
    is_whatsapp: checkboxValue(formData, "is_whatsapp"),
  };

  try {
    const result = await addCustomerPhone(customerId, input);
    revalidatePath(`/customers/${customerId}`);
    return {
      status: "success",
      message: "Telefono agregado correctamente.",
      data: result,
    };
  } catch (error) {
    return apiErrorState(error);
  }
}

export async function addAliasAction(
  customerId: string,
  _previousState: ActionState<CustomerAlias>,
  formData: FormData,
): Promise<ActionState<CustomerAlias>> {
  const authError = await requireActionSession<CustomerAlias>();
  if (authError) {
    return authError;
  }

  const alias = optionalText(formData, "alias");
  if (!alias) {
    return validationError("alias", "El alias es obligatorio.");
  }

  const input: AddAliasInput = {
    alias,
    source: "manual",
  };

  try {
    const result = await addCustomerAlias(customerId, input);
    revalidatePath(`/customers/${customerId}`);
    return {
      status: "success",
      message: "Alias agregado correctamente.",
      data: result,
    };
  } catch (error) {
    return apiErrorState(error);
  }
}

export async function addAddressAction(
  customerId: string,
  _previousState: ActionState<CustomerAddress>,
  formData: FormData,
): Promise<ActionState<CustomerAddress>> {
  const authError = await requireActionSession<CustomerAddress>();
  if (authError) {
    return authError;
  }

  const address = optionalText(formData, "address");
  if (!address) {
    return validationError("address", "La direccion es obligatoria.");
  }

  const input: AddAddressInput = {
    address,
    reference: optionalText(formData, "reference"),
    label: optionalText(formData, "label"),
    city: optionalText(formData, "city"),
    neighborhood: optionalText(formData, "neighborhood"),
    notes: optionalText(formData, "notes"),
    is_primary: checkboxValue(formData, "is_primary"),
  };

  try {
    const result = await addCustomerAddress(customerId, input);
    revalidatePath(`/customers/${customerId}`);
    return {
      status: "success",
      message: "Direccion agregada correctamente.",
      data: result,
    };
  } catch (error) {
    return apiErrorState(error);
  }
}
