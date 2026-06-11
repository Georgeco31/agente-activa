import type { ApiErrorDetail } from "@/lib/api/types";
import { getFriendlyErrorMessage } from "@/lib/api/errors";

interface ValidationItem {
  field?: string;
  message?: string;
}

function validationItems(error: ApiErrorDetail): ValidationItem[] {
  const errors = error.details.errors;
  return Array.isArray(errors) ? (errors as ValidationItem[]) : [];
}

export function ErrorMessage({ error }: { error: ApiErrorDetail }) {
  const items = validationItems(error);

  return (
    <div className="action-message action-message-error" role="alert">
      <div>
        <strong>{getFriendlyErrorMessage(error)}</strong>
        <span className="error-code">{error.code}</span>
      </div>
      {items.length > 0 ? (
        <ul className="validation-list">
          {items.map((item, index) => (
            <li key={`${item.field ?? "field"}-${index}`}>
              {item.message ?? "Valor no valido."}
            </li>
          ))}
        </ul>
      ) : null}
    </div>
  );
}
