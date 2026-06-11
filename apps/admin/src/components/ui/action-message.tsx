import type { CustomerActionState } from "@/lib/api/customer-types";

import { ErrorMessage } from "@/components/ui/error-message";

export function ActionMessage({
  state,
}: {
  state: CustomerActionState<unknown>;
}) {
  if (state.status === "idle") {
    return null;
  }

  if (state.status === "error") {
    return <ErrorMessage error={state.error} />;
  }

  return (
    <div className="action-message action-message-success" role="status">
      <strong>{state.message}</strong>
    </div>
  );
}
