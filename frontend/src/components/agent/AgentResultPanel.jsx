import { Panel } from "../ui";

export function AgentResultPanel({ agentResult }) {
  if (!agentResult) return null;

  return (
    <section className="mt-6">
      <Panel title="Latest Agent Result">
        <pre className="max-h-96 overflow-auto rounded-2xl bg-slate-950 p-4 text-xs text-slate-100">
          {JSON.stringify(agentResult, null, 2)}
        </pre>
      </Panel>
    </section>
  );
}