import Link from "next/link";
import { CalendarDays, Filter } from "lucide-react";

export function DashboardPeriodFilter({
  selectedDate,
  period,
}: {
  selectedDate: string;
  period: string;
}) {
  return (
    <form className="dashboard-period-filter" method="get">
      <label className="field">
        <span>Resumen diario</span>
        <input defaultValue={selectedDate} name="date" type="date" />
      </label>
      <label className="field">
        <span>Mes de ventas</span>
        <input defaultValue={period} name="period" type="month" />
      </label>
      <button className="button button-primary" type="submit">
        <Filter aria-hidden="true" size={15} />
        Aplicar periodo
      </button>
      <Link className="button button-secondary" href="/">
        <CalendarDays aria-hidden="true" size={15} />
        Hoy
      </Link>
    </form>
  );
}
