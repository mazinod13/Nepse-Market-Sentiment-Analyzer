import { useState } from "react";
import { Panel, PrimaryButton, SecondaryButton } from "../ui";

const SOURCES = [
  { value: "bizmandu",      label: "Bizmandu",           defaultPreset: 20  },
  { value: "onlinekhabar",  label: "OnlineKhabar",        defaultPreset: 20  },
  { value: "nepse",         label: "NEPSE (general)",     defaultPreset: 50  },
  { value: "nepse_company", label: "NEPSE (per-company)", defaultPreset: null },
];

const LIMIT_MODES = [
  { id: "preset", label: "Default" },
  { id: "custom", label: "Custom"  },
  { id: "all",    label: "All"     },
];

export function ScrapingJobsPanel({
  scrapeTaskId,
  scrapeJobStatus,
  onRunScraper,
  onCheckStatus,
}) {
  const [sourceId, setSourceId]           = useState("bizmandu");
  const [limitMode, setLimitMode]         = useState("preset");
  const [customLimit, setCustomLimit]     = useState(10);
  const [runPipeline, setRunPipeline]     = useState(true);

  const selectedSource  = SOURCES.find((s) => s.value === sourceId) ?? SOURCES[0];
  const isCompanyScraper = sourceId === "nepse_company";

  function resolvedLimit() {
    if (isCompanyScraper || limitMode === "all") return 0;
    if (limitMode === "preset") return -1;
    return Math.max(1, Number(customLimit) || 1);
  }

  function limitSummary() {
    if (isCompanyScraper)        return "All companies will be scraped.";
    if (limitMode === "all")     return "Every available item will be fetched — may be slow.";
    if (limitMode === "preset")  return `~${selectedSource.defaultPreset ?? "default"} items (source default).`;
    return `${customLimit} item${Number(customLimit) !== 1 ? "s" : ""}.`;
  }

  function handleRun() {
    onRunScraper({
      source_id:    sourceId,
      limit:        resolvedLimit(),
      run_pipeline: runPipeline,
    });
  }

  return (
    <Panel title="Scraping Jobs">
      <div className="space-y-4">

        {/* Source selector */}
        <label className="block">
          <span className="mb-1 block text-xs font-medium text-slate-500">Scraper Source</span>
          <select
            value={sourceId}
            onChange={(e) => {
              setSourceId(e.target.value);
              setLimitMode(e.target.value === "nepse_company" ? "all" : "preset");
            }}
            className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm outline-none transition focus:border-slate-400 focus:ring-2 focus:ring-slate-100"
          >
            {SOURCES.map((s) => (
              <option key={s.value} value={s.value}>{s.label}</option>
            ))}
          </select>
        </label>

        {/* Limit mode picker */}
        {!isCompanyScraper ? (
          <div>
            <span className="mb-1.5 block text-xs font-medium text-slate-500">Fetch amount</span>

            <div className="flex rounded-xl border border-slate-200 bg-slate-50 p-1 gap-1">
              {LIMIT_MODES.map((mode) => (
                <button
                  key={mode.id}
                  type="button"
                  onClick={() => setLimitMode(mode.id)}
                  className={`flex-1 rounded-lg py-1.5 text-xs font-semibold transition ${
                    limitMode === mode.id
                      ? "bg-slate-900 text-white shadow-sm"
                      : "text-slate-500 hover:text-slate-700"
                  }`}
                >
                  {mode.label}
                </button>
              ))}
            </div>

            {limitMode === "custom" && (
              <input
                type="number"
                min={1}
                max={500}
                value={customLimit}
                onChange={(e) => setCustomLimit(e.target.value)}
                placeholder="e.g. 25"
                className="mt-2 w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm outline-none transition focus:border-slate-400 focus:ring-2 focus:ring-slate-100"
              />
            )}

            <p className="mt-1.5 text-xs text-slate-400">{limitSummary()}</p>
          </div>
        ) : (
          <p className="rounded-xl bg-slate-50 px-3 py-2 text-xs text-slate-500">
            The per-company scraper always processes every company in the mapping file.
          </p>
        )}

        {/* Pipeline toggle */}
        <label className="flex cursor-pointer select-none items-center gap-2 text-sm text-slate-600">
          <input
            type="checkbox"
            checked={runPipeline}
            onChange={(e) => setRunPipeline(e.target.checked)}
            className="rounded"
          />
          Run agent pipeline after scraping
        </label>

        <PrimaryButton onClick={handleRun}>Run Scraper</PrimaryButton>

        {scrapeTaskId && (
          <div className="rounded-2xl bg-slate-50 p-3 text-xs text-slate-600">
            <p className="font-medium text-slate-800">Task ID</p>
            <p className="mt-1 break-all">{scrapeTaskId}</p>
          </div>
        )}

        {scrapeTaskId && (
          <SecondaryButton onClick={onCheckStatus}>Check Job Status</SecondaryButton>
        )}

        {scrapeJobStatus && (
          <pre className="max-h-72 overflow-auto rounded-2xl bg-slate-950 p-4 text-xs text-slate-100">
            {JSON.stringify(scrapeJobStatus, null, 2)}
          </pre>
        )}
      </div>
    </Panel>
  );
}