export function Empty({ text }) {
  return <p className="text-sm text-slate-400 italic">{text}</p>;
}

export function CompactList({ items, emptyText, renderItem }) {
  if (!items || items.length === 0) return <Empty text={emptyText} />;

  return (
    <div className="space-y-3">
      {items.map((item) => (
        <div
          key={item.id}
          className="rounded-2xl border border-slate-200 bg-white p-4"
        >
          {renderItem(item)}
        </div>
      ))}
    </div>
  );
}