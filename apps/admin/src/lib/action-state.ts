import type { ApiErrorDetail } from "@/lib/api/types";

export type ActionState<T = undefined> =
  | {
      status: "idle";
      message: "";
      data?: never;
      error?: never;
    }
  | {
      status: "success";
      message: string;
      data: T;
      error?: never;
    }
  | {
      status: "error";
      message: string;
      data?: never;
      error: ApiErrorDetail;
    };
