"use client";
import { useState, useEffect } from "react";
import { getHealth } from "@/lib/api";

export type StatusLevel = "online" | "offline" | "checking";

export interface SystemStatus {
  api: StatusLevel;
  message: string;
}

export function useSystemStatus() {
  const [status, setStatus] = useState<SystemStatus>({
    api: "checking",
    message: "Checking...",
  });

  useEffect(() => {
    let cancelled = false;

    async function check() {
      try {
        const health = await getHealth();
        if (!cancelled) {
          setStatus({
            api: health.status === "ok" ? "online" : "offline",
            message: health.message,
          });
        }
      } catch {
        if (!cancelled) {
          setStatus({ api: "offline", message: "Backend unreachable" });
        }
      }
    }

    check();
    const interval = setInterval(check, 30_000);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, []);

  return status;
}