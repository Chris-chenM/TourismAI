/* API 层：POST /api/plan 与 SSE 流式请求 */

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


// ── SSE 流式请求 ──

export interface StreamCallbacks {
  onPhase: (phase: string, message: string, progress: number) => void;
  onResult: (result: PlanResponse) => void;
  onError: (error: string) => void;
}

export function streamPlanTrip(
  req: PlanRequest,
  callbacks: StreamCallbacks
): AbortController {
  const controller = new AbortController();

  (async () => {
    try {
      const res = await fetch("/api/plan/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(req),
        signal: controller.signal,
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        callbacks.onError(err.detail || "规划失败，请检查后端是否启动");
        return;
      }

      const reader = res.body?.getReader();
      if (!reader) {
        callbacks.onError("浏览器不支持流式读取");
        return;
      }

      const decoder = new TextDecoder();
      let buffer = "";
      let currentEvent = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        // 最后一段可能不完整，留到下次
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (line.startsWith("event: ")) {
            currentEvent = line.slice(7).trim();
          } else if (line.startsWith("data: ")) {
            const dataStr = line.slice(6);
            try {
              const data = JSON.parse(dataStr);
              if (currentEvent === "phase") {
                callbacks.onPhase(data.phase, data.message, data.progress);
              } else if (currentEvent === "result") {
                callbacks.onResult(data as PlanResponse);
              } else if (currentEvent === "error") {
                callbacks.onError(data.message || "未知错误");
              }
            } catch {
              // 忽略解析失败的行
            }
            currentEvent = "";
          }
        }
      }
    } catch (err: any) {
      if (err.name !== "AbortError") {
        callbacks.onError(err.message || "网络请求失败");
      }
    }
  })();

  return controller;
}
