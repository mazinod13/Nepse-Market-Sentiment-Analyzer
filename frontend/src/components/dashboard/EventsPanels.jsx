import { Panel, CompactList } from "../ui";

export function SentimentEventsPanel({ sentimentEvents }) {
  return (
    <Panel title="Detected Sentiment Events">
      <CompactList
        items={sentimentEvents.slice(0, 8)}
        emptyText="No sentiment events detected yet."
        renderItem={(event) => (
          <div>
            <p className="font-medium text-slate-900">
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
  );
}

export function ArticleMapsPanel({ articleMaps }) {
  return (
    <Panel title="Article Company Mappings">
      <CompactList
        items={articleMaps.slice(0, 8)}
        emptyText="No article-company mappings yet."
        renderItem={(item) => (
          <div>
            <p className="font-medium text-slate-900">
              Article #{item.article_id} → {item.company_symbol}
            </p>
            <p className="text-sm text-slate-500">
              {item.match_type} · confidence {item.confidence}
            </p>
          </div>
        )}
      />
    </Panel>
  );
}