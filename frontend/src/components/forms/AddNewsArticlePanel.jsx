import { useState } from "react";
import { Panel, Input, TextArea, Select, PrimaryButton } from "../ui";

const INITIAL = {
  source_id: "",
  original_url: "",
  title: "",
  summary: "",
  content: "",
  language_code: "en",
  author: "",
  image_url: "",
  tags: "",
  status: "draft",
};

export function AddNewsArticlePanel({ sources, onSubmit }) {
  const [form, setForm] = useState(INITIAL);

  function handleSubmit(e) {
    e.preventDefault();
    onSubmit({
      source_id:    form.source_id || null,
      original_url: form.original_url || null,
      title:        form.title,
      summary:      form.summary || null,
      content:      form.content || null,
      language_code: form.language_code || null,
      published_at: new Date().toISOString(),
      author:       form.author || null,
      image_url:    form.image_url || null,
      tags:         form.tags ? form.tags.split(",").map((t) => t.trim()) : [],
      raw_data:     { created_from_dashboard: true },
      status:       form.status,
    });
    setForm(INITIAL);
  }

  const set = (key) => (value) => setForm((f) => ({ ...f, [key]: value }));

  return (
    <Panel title="Add News Article">
      <form onSubmit={handleSubmit} className="grid gap-4 lg:grid-cols-2">
        <Input
          label="Title"
          value={form.title}
          onChange={set("title")}
          placeholder="NABIL announces dividend"
          required
        />

        <Select
          label="Source"
          value={form.source_id}
          onChange={set("source_id")}
          options={sources.map((s) => ({ value: s.source_id, label: s.source_name }))}
        />

        <Input
          label="Original URL"
          value={form.original_url}
          onChange={set("original_url")}
          placeholder="https://example.com/news"
        />

        <Input
          label="Tags (comma-separated)"
          value={form.tags}
          onChange={set("tags")}
          placeholder="dividend, bank, NABIL"
        />

        <TextArea
          label="Summary"
          value={form.summary}
          onChange={set("summary")}
          placeholder="Short summary"
        />

        <TextArea
          label="Content"
          value={form.content}
          onChange={set("content")}
          placeholder="Full or partial article content"
        />

        <div className="lg:col-span-2">
          <PrimaryButton type="submit">Add News Article</PrimaryButton>
        </div>
      </form>
    </Panel>
  );
}