import "server-only";

import { apiFetch } from "@/lib/api/http";
import type {
  DashboardOverview,
  DashboardOverviewParams,
} from "@/lib/api/dashboard-types";

export function getDashboardOverview(
  params: DashboardOverviewParams = {},
): Promise<DashboardOverview> {
  const query = new URLSearchParams();

  if (params.date) {
    query.set("date", params.date);
  }
  if (params.year) {
    query.set("year", String(params.year));
  }
  if (params.month) {
    query.set("month", String(params.month));
  }

  const suffix = query.size > 0 ? `?${query.toString()}` : "";
  return apiFetch<DashboardOverview>(`/api/v1/dashboard/overview${suffix}`);
}
