"use client";

import { Plus, Trash2 } from "lucide-react";
import { useState } from "react";

import type { Product } from "@/lib/api/product-types";

interface ItemRow {
  id: number;
}

export function OrderItemsEditor({ products }: { products: Product[] }) {
  const [rows, setRows] = useState<ItemRow[]>([{ id: 1 }]);
  const [nextId, setNextId] = useState(2);

  function addRow() {
    setRows((current) => [...current, { id: nextId }]);
    setNextId((current) => current + 1);
  }

  function removeRow(id: number) {
    setRows((current) => current.filter((row) => row.id !== id));
  }

  return (
    <div className="order-items-editor">
      <div className="order-items-heading">
        <div>
          <h3>Productos</h3>
          <p>El precio unitario es opcional; vacio usa el precio actual.</p>
        </div>
        <button className="button button-secondary" onClick={addRow} type="button">
          <Plus aria-hidden="true" size={16} />
          Agregar item
        </button>
      </div>

      <div className="order-item-rows">
        {rows.map((row, index) => (
          <div className="order-item-row" key={row.id}>
            <label className="field order-product-field">
              <span>Producto {index + 1} *</span>
              <select defaultValue="" name="product_id" required>
                <option disabled value="">
                  Selecciona un producto activo
                </option>
                {products.map((product) => (
                  <option key={product.id} value={product.id}>
                    {product.name} ({product.sku}) - ${product.price}
                  </option>
                ))}
              </select>
            </label>
            <label className="field">
              <span>Cantidad *</span>
              <input min="0.01" name="quantity" required step="0.01" type="number" />
            </label>
            <label className="field">
              <span>Precio unitario</span>
              <input min="0" name="unit_price" step="0.01" type="number" />
            </label>
            <button
              aria-label={`Eliminar producto ${index + 1}`}
              className="button button-secondary icon-button"
              disabled={rows.length === 1}
              onClick={() => removeRow(row.id)}
              title="Eliminar item"
              type="button"
            >
              <Trash2 aria-hidden="true" size={16} />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
