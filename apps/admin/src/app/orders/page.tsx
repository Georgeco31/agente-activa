import { ClipboardList } from "lucide-react";

import { ModulePlaceholder } from "@/components/module-placeholder";

export default function OrdersPage() {
  return (
    <ModulePlaceholder
      description="Espacio preparado para registrar pedidos y seguir sus estados."
      icon={ClipboardList}
      title="Pedidos"
    />
  );
}
