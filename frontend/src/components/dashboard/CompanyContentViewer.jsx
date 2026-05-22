import { Panel, Select, Empty } from "../ui";

export function CompanyContentViewer({
  companies,
  newsArticles,
  articleMaps,
  selectedCompanySymbol,
  setSelectedCompanySymbol,
  selectedCompanyArticleId,
  setSelectedCompanyArticleId,
}) {
  const selectedCompanyMaps = articleMaps.filter(
    (item) => item.company_symbol === selectedCompanySymbol
  );

  const selectedCompanyArticles = selectedCompanyMaps
    .map((mapItem) => newsArticles.find((a) => a.id === mapItem.article_id))
    .filter(Boolean);

  const selectedCompanyArticle =
    newsArticles.find((a) => String(a.id) === String(selectedCompanyArticleId)) ||
    selectedCompanyArticles[0];

  return (
    <Panel title="Company Content Viewer">
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Left: company picker + article list */}
        <div className="space-y-4">
          <Select
            label="Company"
            value={selectedCompanySymbol}
            onChange={(value) => {
              setSelectedCompanySymbol(value);
              setSelectedCompanyArticleId("");
            }}
            options={companies.map((c) => ({
              value: c.symbol,
              label: `${c.symbol} — ${c.company_name}`,
            }))}
          />

          <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
            <p className="text-sm font-semibold text-slate-800">Mapped Articles</p>
            <p className="mt-1 text-3xl font-bold text-slate-900">
              {selectedCompanyArticles.length}
            </p>
            <p className="mt-1 text-xs text-slate-500">
              Articles connected to {selectedCompanySymbol || "selected company"}
            </p>
          </div>

          <div className="space-y-2">
            {selectedCompanyArticles.length === 0 ? (
              <Empty text="No mapped articles found for this company." />
            ) : (
              selectedCompanyArticles.map((article) => (
                <button
                  key={article.id}
                  onClick={() => setSelectedCompanyArticleId(String(article.id))}
                  className={`w-full rounded-2xl border p-3 text-left text-sm transition ${
                    String(selectedCompanyArticle?.id) === String(article.id)
                      ? "border-slate-900 bg-slate-900 text-white"
                      : "border-slate-200 bg-white text-slate-700 hover:bg-slate-50"
                  }`}
                >
                  <p className="font-medium">#{article.id}</p>
                  <p className="mt-1 line-clamp-2">{article.title}</p>
                </button>
              ))
            )}
          </div>
        </div>

        {/* Right: article detail */}
        <div className="lg:col-span-2">
          {selectedCompanyArticle ? (
            <div className="rounded-2xl border border-slate-200 bg-white p-5">
              <div className="flex flex-wrap items-center gap-2">
                <span className="rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-600">
                  #{selectedCompanyArticle.id}
                </span>
                <span className="rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-600">
                  {selectedCompanyArticle.source_id || "unknown source"}
                </span>
                <span className="rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-600">
                  {selectedCompanyArticle.language_code || "unknown language"}
                </span>
              </div>

              <h3 className="mt-4 text-xl font-bold text-slate-900">
                {selectedCompanyArticle.title}
              </h3>

              {selectedCompanyArticle.summary && (
                <p className="mt-3 rounded-2xl bg-slate-50 p-4 text-sm leading-7 text-slate-700">
                  {selectedCompanyArticle.summary}
                </p>
              )}

              <div className="mt-5 max-h-[520px] overflow-auto rounded-2xl border border-slate-200 bg-white p-4">
                <p className="whitespace-pre-line text-sm leading-8 text-slate-700">
                  {selectedCompanyArticle.content || "No full content stored."}
                </p>
              </div>

              {selectedCompanyArticle.original_url && (
                <a
                  href={selectedCompanyArticle.original_url}
                  target="_blank"
                  rel="noreferrer"
                  className="mt-4 inline-flex text-sm font-semibold text-slate-900 underline"
                >
                  Open original article ↗
                </a>
              )}
            </div>
          ) : (
            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
              <Empty text="Select a company and mapped article to view content." />
            </div>
          )}
        </div>
      </div>
    </Panel>
  );
}