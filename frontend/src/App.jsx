import { useEffect, useState } from "react";
import apiClient from "./api/client";

const initialCompanyForm = {
  symbol: "",
  company_name: "",
  sector: "",
  instrument: "Equity",
  email: "",
  website: "",
  status: "active",
};

const initialSourceForm = {
  source_id: "",
  source_name: "",
  source_type: "news_website",
  website: "",
  language_code: "en",
  reliability_score: 0.8,
  is_active: true,
};

const initialNewsForm = {
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

function App() {
  const [companies, setCompanies] = useState([]);
  const [sources, setSources] = useState([]);
  const [newsArticles, setNewsArticles] = useState([]);
  const [marketSentiment, setMarketSentiment] = useState(null);
  const [companySentiments, setCompanySentiments] = useState({});
  const [sentimentEvents, setSentimentEvents] = useState([]);
  const [articleMaps, setArticleMaps] = useState([]);

  const [companyForm, setCompanyForm] = useState(initialCompanyForm);
  const [sourceForm, setSourceForm] = useState(initialSourceForm);
  const [newsForm, setNewsForm] = useState(initialNewsForm);

  const [selectedArticleId, setSelectedArticleId] = useState("");
  const [selectedCompanySymbol, setSelectedCompanySymbol] = useState("");

  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const showSuccess = (text) => {
    setMessage(text);
    setError("");
  };

  const showError = (text) => {
    setError(text);
    setMessage("");
  };

  const fetchCompanySentiments = async (companyList) => {
    const sentimentMap = {};

    await Promise.all(
      companyList.map(async (company) => {
        try {
          const res = await apiClient.get(
            `/sentiment/company/${company.symbol}/latest`
          );
          sentimentMap[company.symbol] = res.data;
        } catch {
          sentimentMap[company.symbol] = null;
        }
      })
    );

    setCompanySentiments(sentimentMap);
  };

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError("");

      const [companiesRes, sourcesRes, newsRes, eventsRes, mapsRes] =
        await Promise.all([
          apiClient.get("/companies/"),
          apiClient.get("/sources/"),
          apiClient.get("/news/"),
          apiClient.get("/sentiment-events/"),
          apiClient.get("/article-company-maps/"),
        ]);

      setCompanies(companiesRes.data);
      setSources(sourcesRes.data);
      setNewsArticles(newsRes.data);
      setSentimentEvents(eventsRes.data);
      setArticleMaps(mapsRes.data);

      await fetchCompanySentiments(companiesRes.data);

      if (companiesRes.data.length > 0 && !selectedCompanySymbol) {
        setSelectedCompanySymbol(companiesRes.data[0].symbol);
      }

      if (newsRes.data.length > 0 && !selectedArticleId) {
        setSelectedArticleId(String(newsRes.data[0].id));
      }

      try {
        const marketRes = await apiClient.get("/sentiment/market/latest");
        setMarketSentiment(marketRes.data);
      } catch {
        setMarketSentiment(null);
      }
    } catch {
      showError("Could not load dashboard data. Make sure FastAPI is running.");
    } finally {
      setLoading(false);
    }
  };

  const createCompany = async (event) => {
    event.preventDefault();

    try {
      const payload = {
        ...companyForm,
        symbol: companyForm.symbol.toUpperCase(),
        email: companyForm.email || null,
        website: companyForm.website || null,
      };

      await apiClient.post("/companies/", payload);
      setCompanyForm(initialCompanyForm);
      showSuccess("Company added successfully.");
      await fetchDashboardData();
    } catch (err) {
      showError(err.response?.data?.detail || "Could not add company.");
    }
  };

  const createSource = async (event) => {
    event.preventDefault();

    try {
      const payload = {
        ...sourceForm,
        source_id: sourceForm.source_id.toLowerCase(),
        reliability_score: Number(sourceForm.reliability_score),
      };

      await apiClient.post("/sources/", payload);
      setSourceForm(initialSourceForm);
      showSuccess("Source added successfully.");
      await fetchDashboardData();
    } catch (err) {
      showError(err.response?.data?.detail || "Could not add source.");
    }
  };

  const createNewsArticle = async (event) => {
    event.preventDefault();

    try {
      const payload = {
        source_id: newsForm.source_id || null,
        original_url: newsForm.original_url || null,
        title: newsForm.title,
        summary: newsForm.summary || null,
        content: newsForm.content || null,
        language_code: newsForm.language_code || null,
        published_at: new Date().toISOString(),
        author: newsForm.author || null,
        image_url: newsForm.image_url || null,
        tags: newsForm.tags
          ? newsForm.tags.split(",").map((tag) => tag.trim())
          : [],
        raw_data: {
          created_from_dashboard: true,
        },
        status: newsForm.status,
      };

      await apiClient.post("/news/", payload);
      setNewsForm(initialNewsForm);
      showSuccess("News article added successfully.");
      await fetchDashboardData();
    } catch (err) {
      showError(err.response?.data?.detail || "Could not add news article.");
    }
  };

  const mapSelectedArticle = async () => {
    if (!selectedArticleId) {
      showError("Select an article first.");
      return;
    }

    try {
      await apiClient.post(`/article-company-maps/match/${selectedArticleId}`);
      showSuccess("Article-company mapping completed.");
      await fetchDashboardData();
    } catch (err) {
      showError(err.response?.data?.detail || "Could not map article.");
    }
  };

  const detectSelectedArticleSentiment = async () => {
    if (!selectedArticleId) {
      showError("Select an article first.");
      return;
    }

    try {
      await apiClient.post(`/sentiment-events/detect/${selectedArticleId}`);
      showSuccess("Sentiment events detected.");
      await fetchDashboardData();
    } catch (err) {
      showError(err.response?.data?.detail || "Could not detect sentiment.");
    }
  };

  const calculateSelectedCompanySentiment = async () => {
    if (!selectedCompanySymbol) {
      showError("Select a company first.");
      return;
    }

    try {
      await apiClient.post(
        `/sentiment/company/${selectedCompanySymbol}/calculate`
      );
      showSuccess("Company sentiment calculated.");
      await fetchDashboardData();
    } catch (err) {
      showError(
        err.response?.data?.detail || "Could not calculate company sentiment."
      );
    }
  };

  const calculateMarketSentiment = async () => {
    try {
      const res = await apiClient.post("/sentiment/market/calculate");
      setMarketSentiment(res.data);
      showSuccess("Market sentiment calculated.");
      await fetchDashboardData();
    } catch (err) {
      showError(
        err.response?.data?.detail || "Could not calculate market sentiment."
      );
    }
  };

  const getScoreBadgeClass = (score) => {
    if (score >= 80) return "bg-emerald-50 text-emerald-700 ring-emerald-200";
    if (score >= 60) return "bg-green-50 text-green-700 ring-green-200";
    if (score >= 40) return "bg-slate-50 text-slate-700 ring-slate-200";
    if (score >= 20) return "bg-orange-50 text-orange-700 ring-orange-200";
    return "bg-red-50 text-red-700 ring-red-200";
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="sticky top-0 z-10 border-b border-slate-200 bg-white/90 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <div>
            <h1 className="text-xl font-bold tracking-tight">NEPSE Sentiment</h1>
            <p className="text-sm text-slate-500">Market intelligence dashboard</p>
          </div>

          <button
            onClick={fetchDashboardData}
            className="rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm hover:bg-slate-50"
          >
            {loading ? "Refreshing..." : "Refresh"}
          </button>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-6 py-8">
        {message && (
          <div className="mb-6 rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
            {message}
          </div>
        )}

        {error && (
          <div className="mb-6 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
          </div>
        )}

        <section className="grid gap-5 md:grid-cols-4">
          <OverviewCard
            title="Market Sentiment"
            value={marketSentiment?.score ?? "—"}
            subtitle={marketSentiment?.label || "No market score yet"}
            actionLabel="Calculate"
            onAction={calculateMarketSentiment}
          />

          <OverviewCard title="Companies" value={companies.length} subtitle="Listed in database" />
          <OverviewCard title="Sources" value={sources.length} subtitle="News/data sources" />
          <OverviewCard title="News Articles" value={newsArticles.length} subtitle="Stored articles" />
        </section>

        <section className="mt-8 grid gap-6 xl:grid-cols-3">
          <Panel title="Add Company">
            <form onSubmit={createCompany} className="space-y-3">
              <Input label="Symbol" value={companyForm.symbol} onChange={(value) => setCompanyForm({ ...companyForm, symbol: value })} placeholder="NABIL" required />
              <Input label="Company Name" value={companyForm.company_name} onChange={(value) => setCompanyForm({ ...companyForm, company_name: value })} placeholder="Nabil Bank Limited" required />
              <Input label="Sector" value={companyForm.sector} onChange={(value) => setCompanyForm({ ...companyForm, sector: value })} placeholder="Commercial Banks" />
              <Input label="Website" value={companyForm.website} onChange={(value) => setCompanyForm({ ...companyForm, website: value })} placeholder="https://example.com" />
              <PrimaryButton type="submit">Add Company</PrimaryButton>
            </form>
          </Panel>

          <Panel title="Add Source">
            <form onSubmit={createSource} className="space-y-3">
              <Input label="Source ID" value={sourceForm.source_id} onChange={(value) => setSourceForm({ ...sourceForm, source_id: value })} placeholder="onlinekhabar" required />
              <Input label="Source Name" value={sourceForm.source_name} onChange={(value) => setSourceForm({ ...sourceForm, source_name: value })} placeholder="Onlinekhabar" required />
              <Input label="Website" value={sourceForm.website} onChange={(value) => setSourceForm({ ...sourceForm, website: value })} placeholder="https://www.onlinekhabar.com" />
              <Input label="Reliability" type="number" step="0.01" value={sourceForm.reliability_score} onChange={(value) => setSourceForm({ ...sourceForm, reliability_score: value })} />
              <PrimaryButton type="submit">Add Source</PrimaryButton>
            </form>
          </Panel>

          <Panel title="Workflow Actions">
            <div className="space-y-4">
              <Select
                label="Article"
                value={selectedArticleId}
                onChange={setSelectedArticleId}
                options={newsArticles.map((article) => ({
                  value: String(article.id),
                  label: `#${article.id} — ${article.title}`,
                }))}
              />

              <div className="grid grid-cols-2 gap-3">
                <SecondaryButton onClick={mapSelectedArticle}>Map Article</SecondaryButton>
                <SecondaryButton onClick={detectSelectedArticleSentiment}>Detect Event</SecondaryButton>
              </div>

              <Select
                label="Company"
                value={selectedCompanySymbol}
                onChange={setSelectedCompanySymbol}
                options={companies.map((company) => ({
                  value: company.symbol,
                  label: `${company.symbol} — ${company.company_name}`,
                }))}
              />

              <SecondaryButton onClick={calculateSelectedCompanySentiment}>
                Calculate Company Sentiment
              </SecondaryButton>

              <PrimaryButton onClick={calculateMarketSentiment}>
                Calculate Market Sentiment
              </PrimaryButton>
            </div>
          </Panel>
        </section>

        <section className="mt-6">
          <Panel title="Add News Article">
            <form onSubmit={createNewsArticle} className="grid gap-4 lg:grid-cols-2">
              <Input label="Title" value={newsForm.title} onChange={(value) => setNewsForm({ ...newsForm, title: value })} placeholder="NABIL announces dividend" required />

              <Select
                label="Source"
                value={newsForm.source_id}
                onChange={(value) => setNewsForm({ ...newsForm, source_id: value })}
                options={sources.map((source) => ({
                  value: source.source_id,
                  label: source.source_name,
                }))}
              />

              <Input label="Original URL" value={newsForm.original_url} onChange={(value) => setNewsForm({ ...newsForm, original_url: value })} placeholder="https://example.com/news" />
              <Input label="Tags" value={newsForm.tags} onChange={(value) => setNewsForm({ ...newsForm, tags: value })} placeholder="dividend, bank, NABIL" />

              <TextArea label="Summary" value={newsForm.summary} onChange={(value) => setNewsForm({ ...newsForm, summary: value })} placeholder="Short summary" />
              <TextArea label="Content" value={newsForm.content} onChange={(value) => setNewsForm({ ...newsForm, content: value })} placeholder="Full or partial article content" />

              <div className="lg:col-span-2">
                <PrimaryButton type="submit">Add News Article</PrimaryButton>
              </div>
            </form>
          </Panel>
        </section>

        <section className="mt-8 grid gap-6 xl:grid-cols-2">
          <Panel title="Company Sentiment">
            <div className="space-y-3">
              {companies.length === 0 ? (
                <Empty text="No companies found." />
              ) : (
                companies.map((company) => {
                  const sentiment = companySentiments[company.symbol];

                  return (
                    <div key={company.id} className="rounded-2xl border border-slate-200 bg-white p-4">
                      <div className="flex items-start justify-between gap-4">
                        <div>
                          <div className="flex items-center gap-2">
                            <h3 className="font-semibold">{company.symbol}</h3>
                            <span className="rounded-full bg-slate-100 px-2 py-1 text-xs text-slate-500">
                              {company.sector || "Unknown"}
                            </span>
                          </div>
                          <p className="mt-1 text-sm text-slate-600">{company.company_name}</p>
                        </div>

                        {sentiment ? (
                          <div className="text-right">
                            <span className={`inline-flex rounded-full px-3 py-1 text-sm font-bold ring-1 ${getScoreBadgeClass(sentiment.score)}`}>
                              {sentiment.score}
                            </span>
                            <p className="mt-2 max-w-40 text-xs text-slate-500">{sentiment.label}</p>
                          </div>
                        ) : (
                          <span className="rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-500">
                            No score
                          </span>
                        )}
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </Panel>

          <Panel title="Latest News">
            <div className="space-y-3">
              {newsArticles.length === 0 ? (
                <Empty text="No news articles found." />
              ) : (
                newsArticles.slice(0, 8).map((article) => (
                  <div key={article.id} className="rounded-2xl border border-slate-200 bg-white p-4">
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <h3 className="font-semibold">{article.title}</h3>
                        <p className="mt-1 text-sm text-slate-600">
                          {article.summary || "No summary available"}
                        </p>
                      </div>
                      <span className="shrink-0 rounded-full bg-slate-100 px-2 py-1 text-xs text-slate-500">
                        #{article.id}
                      </span>
                    </div>
                    <p className="mt-3 text-xs text-slate-400">
                      Source: {article.source_id || "unknown"}
                    </p>
                  </div>
                ))
              )}
            </div>
          </Panel>
        </section>

        <section className="mt-8 grid gap-6 xl:grid-cols-2">
          <Panel title="Detected Sentiment Events">
            <CompactList
              items={sentimentEvents.slice(0, 8)}
              emptyText="No sentiment events detected yet."
              renderItem={(event) => (
                <div>
                  <p className="font-medium">
                    Article #{event.article_id} — {event.event_type}
                  </p>
                  <p className="text-sm text-slate-500">
                    {event.sentiment} · impact {event.impact_score} · confidence {event.confidence}
                  </p>
                  <p className="mt-1 text-xs text-slate-400">{event.evidence}</p>
                </div>
              )}
            />
          </Panel>

          <Panel title="Article Company Mappings">
            <CompactList
              items={articleMaps.slice(0, 8)}
              emptyText="No article-company mappings yet."
              renderItem={(item) => (
                <div>
                  <p className="font-medium">
                    Article #{item.article_id} → {item.company_symbol}
                  </p>
                  <p className="text-sm text-slate-500">
                    {item.match_type} · confidence {item.confidence}
                  </p>
                </div>
              )}
            />
          </Panel>
        </section>
      </main>
    </div>
  );
}

function OverviewCard({ title, value, subtitle, actionLabel, onAction }) {
  return (
    <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <p className="text-sm font-medium text-slate-500">{title}</p>
        {actionLabel && (
          <button
            onClick={onAction}
            className="rounded-xl bg-slate-900 px-3 py-1.5 text-xs font-semibold text-white hover:bg-slate-700"
          >
            {actionLabel}
          </button>
        )}
      </div>
      <h2 className="mt-4 text-4xl font-bold tracking-tight">{value}</h2>
      <p className="mt-2 text-sm text-slate-500">{subtitle}</p>
    </div>
  );
}

function Panel({ title, children }) {
  return (
    <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
      <h2 className="mb-4 text-base font-semibold tracking-tight">{title}</h2>
      {children}
    </div>
  );
}

function Input({ label, value, onChange, placeholder, type = "text", step, required = false }) {
  return (
    <label className="block">
      <span className="mb-1 block text-xs font-medium text-slate-500">{label}</span>
      <input
        type={type}
        step={step}
        value={value}
        required={required}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
        className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm outline-none transition focus:border-slate-400 focus:ring-2 focus:ring-slate-100"
      />
    </label>
  );
}

function TextArea({ label, value, onChange, placeholder }) {
  return (
    <label className="block">
      <span className="mb-1 block text-xs font-medium text-slate-500">{label}</span>
      <textarea
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
        rows={4}
        className="w-full resize-none rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm outline-none transition focus:border-slate-400 focus:ring-2 focus:ring-slate-100"
      />
    </label>
  );
}

function Select({ label, value, onChange, options }) {
  return (
    <label className="block">
      <span className="mb-1 block text-xs font-medium text-slate-500">{label}</span>
      <select
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm outline-none transition focus:border-slate-400 focus:ring-2 focus:ring-slate-100"
      >
        <option value="">Select</option>
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </label>
  );
}

function PrimaryButton({ children, type = "button", onClick }) {
  return (
    <button
      type={type}
      onClick={onClick}
      className="w-full rounded-xl bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-slate-700"
    >
      {children}
    </button>
  );
}

function SecondaryButton({ children, onClick }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-50"
    >
      {children}
    </button>
  );
}

function Empty({ text }) {
  return <p className="text-sm text-slate-500">{text}</p>;
}

function CompactList({ items, emptyText, renderItem }) {
  if (items.length === 0) {
    return <Empty text={emptyText} />;
  }

  return (
    <div className="space-y-3">
      {items.map((item) => (
        <div key={item.id} className="rounded-2xl border border-slate-200 bg-white p-4">
          {renderItem(item)}
        </div>
      ))}
    </div>
  );
}

export default App;