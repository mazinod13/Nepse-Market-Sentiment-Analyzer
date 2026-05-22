export function OverviewCard({ title, value, subtitle, actionLabel, onAction }) {
  return (
    <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <p className="text-sm font-medium text-slate-500">{title}</p>
        {actionLabel && (
          <button
            onClick={onAction}
            className="rounded-xl bg-slate-900 px-3 py-1.5 text-xs font-semibold text-white hover:bg-slate-700 transition"
          >
            {actionLabel}
          </button>
        )}
      </div>
      <h2 className="mt-4 text-4xl font-bold tracking-tight text-slate-900">{value}</h2>
      <p className="mt-2 text-sm text-slate-500">{subtitle}</p>
    </div>
  );
}