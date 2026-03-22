interface StatusState {
  state: "ready" | "degraded" | "not_ready" | "unknown";
}

const stateClasses: Record<StatusState["state"], string> = {
  ready: "bg-emerald-500/15 text-emerald-700 dark:text-emerald-300",
  degraded: "bg-amber-500/15 text-amber-700 dark:text-amber-300",
  not_ready: "bg-rose-500/15 text-rose-700 dark:text-rose-300",
  unknown: "bg-slate-500/15 text-slate-700 dark:text-slate-300",
};

export function StatusBadge({ status }: { status: StatusState }) {
  return (
    <span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-medium ${stateClasses[status.state]}`}>
      {status.state.replace("_", " ")}
    </span>
  );
}
