import type { LucideIcon } from "lucide-react";

export function EmptyState({
  icon: Icon,
  title,
  description,
}: {
  icon: LucideIcon;
  title: string;
  description: string;
}) {
  return (
    <div className="empty-state">
      <span className="empty-state-icon">
        <Icon aria-hidden="true" size={22} />
      </span>
      <strong>{title}</strong>
      <p>{description}</p>
    </div>
  );
}
