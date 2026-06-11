import { UsersRound } from "lucide-react";

import { ModulePlaceholder } from "@/components/module-placeholder";

export default function CustomersPage() {
  return (
    <ModulePlaceholder
      description="Espacio preparado para administrar clientes, telefonos, alias y direcciones."
      icon={UsersRound}
      title="Clientes"
    />
  );
}
