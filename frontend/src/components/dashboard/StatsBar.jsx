import { OverviewCard } from "../ui";

export function StatsBar({ marketSentiment, companies, sources, newsArticles, onCalculateMarket }) {
  return (
    <section className="grid gap-5 md:grid-cols-4">
      <OverviewCard
        title="Market Sentiment"
        value={marketSentiment?.score ?? "—"}
        subtitle={marketSentiment?.label || "No market score yet"}
        actionLabel="Calculate"
        onAction={onCalculateMarket}
      />
      <OverviewCard
        title="Companies"
        value={companies.length}
        subtitle="Listed in database"
      />
      <OverviewCard
        title="Sources"
        value={sources.length}
        subtitle="News / data sources"
      />
      <OverviewCard
        title="News Articles"
        value={newsArticles.length}
        subtitle="Stored articles"
      />
    </section>
  );
}