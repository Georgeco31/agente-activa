import type { LucideIcon } from "lucide-react";

export function SummaryCard({
  icon: Icon,
  label,
  value,
  supportingText,
  tone = "blue",
}: {
  icon: LucideIcon;
  label: string;
  value: string;
  supportingText: string;
  tone?: "blue" | "neutral" | "success" | "warning";
}) {
  return (
    <article className={`dashboard-summary-card dashboard-summary-card-${tone}`}>
      <span className="dashboard-summary-icon">
        <Icon aria-hidden="true" size={18} />
      </span>
      <div>
        <span>{label}</span>
        <strong>{value}</strong>
        <small>{supportingText}</small>
      </div>
    </article>
  );
}
