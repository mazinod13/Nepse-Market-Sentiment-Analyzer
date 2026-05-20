import { useEffect, useState } from "react";
import apiClient from "./api/client";

function App() {
  const [marketSentiment, setMarketSentiment] = useState(null);
  const [companies, setCompanies] = useState([]);
  const [newsArticles, setNewsArticles] = useState([]);
  const [error, setError] = useState("");

  const fetchDashboardData = async () => {
    try {
      setError("");

      const [companiesRes, newsRes] = await Promise.all([
        apiClient.get("/companies/"),
        apiClient.get("/news/"),
      ]);

      setCompanies(companiesRes.data);
      setNewsArticles(newsRes.data);

      try {
        const marketRes = await apiClient.get("/sentiment/market/latest");
        setMarketSentiment(marketRes.data);
      } catch {
        setMarketSentiment(null);
      }
    } catch (err) {
      setError("Could not load dashboard data. Make sure FastAPI is running.");
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  return (
    <div className="min-h-screen bg-slate-100">
      <header className="border-b bg-white">
        <div className="mx-auto max-w-6xl px-6 py-5">
          <h1 className="text-2xl font-bold text-slate-900">
            NEPSE Market Sentiment Analyzer
          </h1>
          <p className="mt-1 text-sm text-slate-500">
            MVP dashboard connected to FastAPI backend
          </p>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-6 py-8">
        {error && (
          <div className="mb-6 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-red-700">
            {error}
          </div>
        )}

        <section className="grid gap-6 md:grid-cols-3">
          <div className="rounded-xl bg-white p-6 shadow-sm">
            <p className="text-sm font-medium text-slate-500">
              Market Sentiment
            </p>

            {marketSentiment ? (
              <>
                <h2 className="mt-3 text-4xl font-bold text-slate-900">
                  {marketSentiment.score}
                </h2>
                <p className="mt-2 text-sm text-slate-600">
                  {marketSentiment.label}
                </p>
                <p className="mt-1 text-xs text-slate-400">
                  Confidence: {marketSentiment.confidence}
                </p>
              </>
            ) : (
              <p className="mt-3 text-sm text-slate-500">
                No market sentiment calculated yet.
              </p>
            )}
          </div>

          <div className="rounded-xl bg-white p-6 shadow-sm">
            <p className="text-sm font-medium text-slate-500">
              Listed Companies
            </p>
            <h2 className="mt-3 text-4xl font-bold text-slate-900">
              {companies.length}
            </h2>
            <p className="mt-2 text-sm text-slate-600">
              Companies stored in database
            </p>
          </div>

          <div className="rounded-xl bg-white p-6 shadow-sm">
            <p className="text-sm font-medium text-slate-500">
              News Articles
            </p>
            <h2 className="mt-3 text-4xl font-bold text-slate-900">
              {newsArticles.length}
            </h2>
            <p className="mt-2 text-sm text-slate-600">
              Articles stored for analysis
            </p>
          </div>
        </section>

        <section className="mt-8 grid gap-6 lg:grid-cols-2">
          <div className="rounded-xl bg-white p-6 shadow-sm">
            <h2 className="text-lg font-semibold text-slate-900">
              Companies
            </h2>

            <div className="mt-4 space-y-3">
              {companies.length === 0 ? (
                <p className="text-sm text-slate-500">No companies found.</p>
              ) : (
                companies.map((company) => (
                  <div
                    key={company.id}
                    className="rounded-lg border border-slate-200 p-4"
                  >
                    <div className="flex items-center justify-between">
                      <h3 className="font-semibold text-slate-900">
                        {company.symbol}
                      </h3>
                      <span className="rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-600">
                        {company.sector || "Unknown sector"}
                      </span>
                    </div>
                    <p className="mt-1 text-sm text-slate-600">
                      {company.company_name}
                    </p>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="rounded-xl bg-white p-6 shadow-sm">
            <h2 className="text-lg font-semibold text-slate-900">
              Latest News
            </h2>

            <div className="mt-4 space-y-3">
              {newsArticles.length === 0 ? (
                <p className="text-sm text-slate-500">No news found.</p>
              ) : (
                newsArticles.slice(0, 5).map((article) => (
                  <div
                    key={article.id}
                    className="rounded-lg border border-slate-200 p-4"
                  >
                    <h3 className="font-semibold text-slate-900">
                      {article.title}
                    </h3>
                    <p className="mt-1 text-sm text-slate-600">
                      {article.summary || "No summary available"}
                    </p>
                    <p className="mt-2 text-xs text-slate-400">
                      Source: {article.source_id || "unknown"}
                    </p>
                  </div>
                ))
              )}
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;