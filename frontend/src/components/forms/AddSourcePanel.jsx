import { useState } from "react";
import { Panel, Input, PrimaryButton } from "../ui";

const INITIAL = {
  source_id: "",
  source_name: "",
  source_type: "news_website",
  website: "",
  language_code: "en",
  reliability_score: 0.8,
  is_active: true,
};

export function AddSourcePanel({ onSubmit }) {
  const [form, setForm] = useState(INITIAL);

  function handleSubmit(e) {
    e.preventDefault();
    onSubmit({
      ...form,
      source_id: form.source_id.toLowerCase(),
      reliability_score: Number(form.reliability_score),
    });
    setForm(INITIAL);
  }

  const set = (key) => (value) => setForm((f) => ({ ...f, [key]: value }));

  return (
    <Panel title="Add Source">
      <form onSubmit={handleSubmit} className="space-y-3">
        <Input label="Source ID"   value={form.source_id}         onChange={set("source_id")}         placeholder="bizmandu"           required />
        <Input label="Source Name" value={form.source_name}       onChange={set("source_name")}       placeholder="Bizmandu"           required />
        <Input label="Website"     value={form.website}           onChange={set("website")}           placeholder="https://bizmandu.com" />
        <Input
          label="Reliability"
          type="number"
          step="0.01"
          min="0"
          max="1"
          value={form.reliability_score}
          onChange={set("reliability_score")}
        />
        <PrimaryButton type="submit">Add Source</PrimaryButton>
      </form>
    </Panel>
  );
}