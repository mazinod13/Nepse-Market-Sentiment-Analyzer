import { useState } from "react";
import { Panel, Input, PrimaryButton } from "../ui";

const INITIAL = {
  symbol: "",
  company_name: "",
  sector: "",
  instrument: "Equity",
  email: "",
  website: "",
  status: "active",
};

export function AddCompanyPanel({ onSubmit }) {
  const [form, setForm] = useState(INITIAL);

  function handleSubmit(e) {
    e.preventDefault();
    onSubmit({
      ...form,
      symbol: form.symbol.toUpperCase(),
      email: form.email || null,
      website: form.website || null,
    });
    setForm(INITIAL);
  }

  const set = (key) => (value) => setForm((f) => ({ ...f, [key]: value }));

  return (
    <Panel title="Add Company">
      <form onSubmit={handleSubmit} className="space-y-3">
        <Input label="Symbol"       value={form.symbol}       onChange={set("symbol")}       placeholder="NABIL"               required />
        <Input label="Company Name" value={form.company_name} onChange={set("company_name")} placeholder="Nabil Bank Limited"  required />
        <Input label="Sector"       value={form.sector}       onChange={set("sector")}       placeholder="Commercial Banks" />
        <Input label="Website"      value={form.website}      onChange={set("website")}      placeholder="https://example.com" />
        <PrimaryButton type="submit">Add Company</PrimaryButton>
      </form>
    </Panel>
  );
}