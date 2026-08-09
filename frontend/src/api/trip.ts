/* API 层：POST /api/plan */

import { useMutation } from "@tanstack/react-query";
import type { PlanResponse } from "../types/trip";

export interface PlanRequest {
  destination: string;
  days: number;
  budget: number;
  interests: string;
}

async function planTrip(req: PlanRequest): Promise<PlanResponse> {
  const res = await fetch("/api/plan", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "规划失败，请检查后端是否启动");
  }
  return res.json();
}

export function usePlanTrip() {
  return useMutation({ mutationFn: planTrip });
}
