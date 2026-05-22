import { Panel, Empty } from "../ui";

function scoreBadgeClass(score) {
  if (score >= 80) return "bg-emerald-50 text-emerald-700 ring-emerald-200";
  if (score >= 60) return "bg-green-50 text-green-700 ring-green-200";
  if (score >= 40) return "bg-slate-50 text-slate-700 ring-slate-200";
  if (score >= 20) return "bg-orange-50 text-orange-700 ring-orange-200";
  return "bg-red-50 text-red-700 ring-red-200";
}

export function CompanySentimentList({ companies, companySentiments }) {
  return (
    <Panel title="Company Sentiment">
      <div className="space-y-3">
        {companies.length === 0 ? (
          <Empty text="No companies found." />
        ) : (
          companies.map((company) => {
            const sentiment = companySentiments[company.symbol];
            return (
              <div
                key={company.id}
                className="rounded-2xl border border-slate-200 bg-white p-4"
              >
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
                      <span
                        className={`inline-flex rounded-full px-3 py-1 text-sm font-bold ring-1 ${scoreBadgeClass(
                          sentiment.score
                        )}`}
                      >
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
  );
}