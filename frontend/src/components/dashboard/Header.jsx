export function Header({ loading, onRefresh }) {
  return (
    <header className="sticky top-0 z-10 border-b border-slate-200 bg-white/90 backdrop-blur">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-slate-900">NEPSE Sentiment</h1>
          <p className="text-sm text-slate-500">Market intelligence dashboard</p>
        </div>
        <button
          onClick={onRefresh}
          className="rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm hover:bg-slate-50 transition"
        >
          {loading ? "Refreshing…" : "Refresh"}
        </button>
      </div>
    </header>
  );
}