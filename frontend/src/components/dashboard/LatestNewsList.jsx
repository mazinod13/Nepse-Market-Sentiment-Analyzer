import { Panel, Empty } from "../ui";

export function LatestNewsList({ newsArticles }) {
  return (
    <Panel title="Latest News">
      <div className="space-y-3">
        {newsArticles.length === 0 ? (
          <Empty text="No news articles found." />
        ) : (
          newsArticles.slice(0, 8).map((article) => (
            <div
              key={article.id}
              className="rounded-2xl border border-slate-200 bg-white p-4"
            >
              <div className="flex items-start justify-between gap-4">
                <div>
                  <h3 className="font-semibold text-slate-900">{article.title}</h3>
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
  );
}