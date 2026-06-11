export function StatusBadge({
  label,
  tone = "neutral",
}: {
  label: string;
  tone?: "success" | "danger" | "neutral";
}) {
  return (
    <span className={`status-badge status-badge-${tone}`}>
      <span className="status-badge-dot" aria-hidden="true" />
      {label}
    </span>
  );
}
