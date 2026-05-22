export function Input({
  label,
  value,
  onChange,
  placeholder,
  type = "text",
  step,
  min,
  max,
  required = false,
}) {
  return (
    <label className="block">
      <span className="mb-1 block text-xs font-medium text-slate-500">{label}</span>
      <input
        type={type}
        step={step}
        min={min}
        max={max}
        value={value}
        required={required}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm outline-none transition focus:border-slate-400 focus:ring-2 focus:ring-slate-100"
      />
    </label>
  );
}