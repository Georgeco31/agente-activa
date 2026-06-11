"use server";

import { revalidatePath } from "next/cache";

import type { ActionState } from "@/lib/action-state";
import { toApiErrorDetail } from "@/lib/api/errors";
import type { Order, OrderCreateInput, OrderItemCreateInput } from "@/lib/api/order-types";
import { cancelOrder, createOrder, updateOrderStatus } from "@/lib/api/orders";

function textValue(formData: FormData, key: string): string {
  const value = formData.get(key);
  return typeof value === "string" ? value.trim() : "";
}

function checkboxValue(formData: FormData, key: string): boolean {
  return formData.get(key) === "on";
}

function entryText(value: FormDataEntryValue | undefined): string {
  return typeof value === "string" ? value.trim() : "";
}

function validationError<T>(field: string, message: string): ActionState<T> {
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

function orderItems(formData: FormData): OrderItemCreateInput[] | ActionState<Order> {
  const productIds = formData.getAll("product_id");
  const quantities = formData.getAll("quantity");
  const unitPrices = formData.getAll("unit_price");

  if (productIds.length === 0) {
    return validationError("items", "Agrega al menos un producto al pedido.");
  }

  const items: OrderItemCreateInput[] = [];
  for (let index = 0; index < productIds.length; index += 1) {
    const productId = entryText(productIds[index]);
    const quantity = entryText(quantities[index]);
    const unitPrice = entryText(unitPrices[index]);

    if (!productId) {
      return validationError("items.product_id", "Selecciona un producto en cada fila.");
    }
    if (!quantity || Number(quantity) <= 0) {
      return validationError("items.quantity", "Cada cantidad debe ser mayor que cero.");
    }
    if (unitPrice && Number(unitPrice) < 0) {
      return validationError("items.unit_price", "El precio unitario no puede ser negativo.");
    }

    items.push({
      product_id: productId,
      quantity,
      ...(unitPrice ? { unit_price: unitPrice } : {}),
    });
  }

  return items;
}

export async function createOrderAction(
  _previousState: ActionState<Order>,
  formData: FormData,
): Promise<ActionState<Order>> {
  const customerId = textValue(formData, "customer_id");
  const addressId = textValue(formData, "address_id");

  if (!customerId) {
    return validationError("customer_id", "Selecciona un cliente.");
  }
  if (!addressId) {
    return validationError("address_id", "Selecciona una direccion.");
  }

  const items = orderItems(formData);
  if (!Array.isArray(items)) {
    return items;
  }

  const input: OrderCreateInput = {
    customer_id: customerId,
    address_id: addressId,
    items,
    notes: textValue(formData, "notes") || undefined,
    delivery_route_id: textValue(formData, "delivery_route_id") || undefined,
  };

  try {
    const order = await createOrder(input);
    revalidatePath("/orders");
    return {
      status: "success",
      message: "Pedido creado correctamente.",
      data: order,
    };
  } catch (error) {
    return apiErrorState(error);
  }
}

export async function updateOrderStatusAction(
  orderId: string,
  _previousState: ActionState<Order>,
  formData: FormData,
): Promise<ActionState<Order>> {
  const statusCode = textValue(formData, "status_code");
  if (!statusCode) {
    return validationError("status_code", "Selecciona un estado.");
  }

  try {
    const order = await updateOrderStatus(orderId, { status_code: statusCode });
    revalidatePath("/orders");
    revalidatePath(`/orders/${orderId}`);
    return {
      status: "success",
      message: "Estado actualizado correctamente.",
      data: order,
    };
  } catch (error) {
    return apiErrorState(error);
  }
}

export async function cancelOrderAction(
  orderId: string,
  _previousState: ActionState<Order>,
  formData: FormData,
): Promise<ActionState<Order>> {
  if (!checkboxValue(formData, "confirm_cancel")) {
    return validationError("confirm_cancel", "Confirma que deseas cancelar el pedido.");
  }

  try {
    const order = await cancelOrder(orderId);
    revalidatePath("/orders");
    revalidatePath(`/orders/${orderId}`);
    return {
      status: "success",
      message: "Pedido cancelado correctamente.",
      data: order,
    };
  } catch (error) {
    return apiErrorState(error);
  }
}
