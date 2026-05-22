export function Panel({ title, children, className = "" }) {
  return (
    <div className={`rounded-3xl border border-slate-200 bg-white p-5 shadow-sm ${className}`}>
      {title && (
        <h2 className="mb-4 text-base font-semibold tracking-tight text-slate-900">
          {title}
        </h2>
      )}
      {children}
    </div>
  );
}