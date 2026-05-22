import { Panel, Select, SecondaryButton, PrimaryButton } from "../ui";

export function WorkflowActionsPanel({
  newsArticles,
  companies,
  selectedArticleId,
  setSelectedArticleId,
  selectedCompanySymbol,
  setSelectedCompanySymbol,
  isRunningAgent,
  onMapArticle,
  onDetectSentiment,
  onCalculateCompanySentiment,
  onCalculateMarketSentiment,
  onRunAgentForArticle,
  onRunAgentForAll,
}) {
  return (
    <Panel title="Workflow Actions">
      <div className="space-y-4">
        <Select
          label="Article"
          value={selectedArticleId}
          onChange={setSelectedArticleId}
          options={newsArticles.map((a) => ({
            value: String(a.id),
            label: `#${a.id} — ${a.title}`,
          }))}
        />

        <div className="grid grid-cols-2 gap-3">
          <SecondaryButton onClick={onMapArticle}>Map Article</SecondaryButton>
          <SecondaryButton onClick={onDetectSentiment}>Detect Event</SecondaryButton>
        </div>

        <Select
          label="Company"
          value={selectedCompanySymbol}
          onChange={setSelectedCompanySymbol}
          options={companies.map((c) => ({
            value: c.symbol,
            label: `${c.symbol} — ${c.company_name}`,
          }))}
        />

        <SecondaryButton onClick={onCalculateCompanySentiment}>
          Calculate Company Sentiment
        </SecondaryButton>

        <SecondaryButton onClick={onRunAgentForArticle} disabled={isRunningAgent}>
          {isRunningAgent ? "Running Agent…" : "Run Agent for Selected Article"}
        </SecondaryButton>

        <SecondaryButton onClick={onRunAgentForAll} disabled={isRunningAgent}>
          {isRunningAgent ? "Running Agent…" : "Run Agent for All"}
        </SecondaryButton>

        <PrimaryButton onClick={onCalculateMarketSentiment}>
          Calculate Market Sentiment
        </PrimaryButton>
      </div>
    </Panel>
  );
}