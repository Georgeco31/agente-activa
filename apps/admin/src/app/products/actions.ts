"use server";

import { revalidatePath } from "next/cache";

import type { ActionState } from "@/lib/action-state";
import { toApiErrorDetail } from "@/lib/api/errors";
import type {
  Product,
  ProductCreateInput,
  ProductDeactivateResult,
  ProductUpdateInput,
} from "@/lib/api/product-types";
import {
  createProduct,
  deactivateProduct,
  updateProduct,
} from "@/lib/api/products";

function textValue(formData: FormData, key: string): string {
  const value = formData.get(key);
  return typeof value === "string" ? value.trim() : "";
}

function optionalText(formData: FormData, key: string): string | undefined {
  return textValue(formData, key) || undefined;
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

function requiredProductFields(
  formData: FormData,
): { sku: string; name: string; unit: string; price: string } | ActionState<Product> {
  const sku = textValue(formData, "sku");
  const name = textValue(formData, "name");
  const unit = textValue(formData, "unit");
  const price = textValue(formData, "price");

  if (!sku) {
    return validationError("sku", "El SKU es obligatorio.");
  }
  if (!name) {
    return validationError("name", "El nombre es obligatorio.");
  }
  if (!unit) {
    return validationError("unit", "La unidad es obligatoria.");
  }
  if (!price) {
    return validationError("price", "El precio es obligatorio.");
  }

  return { sku, name, unit, price };
}

export async function createProductAction(
  _previousState: ActionState<Product>,
  formData: FormData,
): Promise<ActionState<Product>> {
  const required = requiredProductFields(formData);
  if ("status" in required) {
    return required;
  }

  const input: ProductCreateInput = {
    ...required,
    description: optionalText(formData, "description"),
    is_active: checkboxValue(formData, "is_active"),
  };

  try {
    const product = await createProduct(input);
    revalidatePath("/products");
    return {
      status: "success",
      message: "Producto creado correctamente.",
      data: product,
    };
  } catch (error) {
    return apiErrorState(error);
  }
}

export async function updateProductAction(
  productId: string,
  _previousState: ActionState<Product>,
  formData: FormData,
): Promise<ActionState<Product>> {
  const required = requiredProductFields(formData);
  if ("status" in required) {
    return required;
  }

  const input: ProductUpdateInput = {
    ...required,
    description: textValue(formData, "description") || null,
    is_active: checkboxValue(formData, "is_active"),
  };

  try {
    const product = await updateProduct(productId, input);
    revalidatePath("/products");
    revalidatePath(`/products/${productId}`);
    return {
      status: "success",
      message: "Producto actualizado correctamente.",
      data: product,
    };
  } catch (error) {
    return apiErrorState(error);
  }
}

export async function deactivateProductAction(
  productId: string,
  _previousState: ActionState<ProductDeactivateResult>,
  formData: FormData,
): Promise<ActionState<ProductDeactivateResult>> {
  if (!checkboxValue(formData, "confirm_deactivate")) {
    return validationError(
      "confirm_deactivate",
      "Confirma que deseas desactivar el producto.",
    );
  }

  try {
    const product = await deactivateProduct(productId);
    revalidatePath("/products");
    revalidatePath(`/products/${productId}`);
    return {
      status: "success",
      message: "Producto desactivado correctamente.",
      data: product,
    };
  } catch (error) {
    return apiErrorState(error);
  }
}
