import { Boxes } from "lucide-react";

import { ModulePlaceholder } from "@/components/module-placeholder";

export default function ProductsPage() {
  return (
    <ModulePlaceholder
      description="Espacio preparado para administrar catalogo, precios y disponibilidad."
      icon={Boxes}
      title="Productos"
    />
  );
}
