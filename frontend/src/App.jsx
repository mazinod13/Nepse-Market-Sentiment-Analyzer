import { useEffect, useState, useCallback } from "react";
import apiClient from "./api/client";

// Dashboard chrome
import { Header }               from "./components/dashboard/Header";
import { AlertBanner }          from "./components/dashboard/AlertBanner";
import { StatsBar }             from "./components/dashboard/StatsBar";
import { CompanySentimentList } from "./components/dashboard/CompanySentimentList";
import { LatestNewsList }       from "./components/dashboard/LatestNewsList";
import { SentimentEventsPanel, ArticleMapsPanel } from "./components/dashboard/EventsPanels";
import { CompanyContentViewer } from "./components/dashboard/CompanyContentViewer";

// Forms
import { AddCompanyPanel }      from "./components/forms/AddCompanyPanel";
import { AddSourcePanel }       from "./components/forms/AddSourcePanel";
import { AddNewsArticlePanel }  from "./components/forms/AddNewsArticlePanel";

// Workflow
import { WorkflowActionsPanel } from "./components/workflow/WorkflowActionsPanel";
import { ScrapingJobsPanel }    from "./components/workflow/ScrapingJobsPanel";

// Agent
import { AgentResultPanel }     from "./components/agent/AgentResultPanel";

// ─────────────────────────────────────────────────────────────────────────────

export default function App() {
  // ── Server data ────────────────────────────────────────────────────────────
  const [companies,        setCompanies]        = useState([]);
  const [sources,          setSources]          = useState([]);
  const [newsArticles,     setNewsArticles]      = useState([]);
  const [marketSentiment,  setMarketSentiment]   = useState(null);
  const [companySentiments,setCompanySentiments] = useState({});
  const [sentimentEvents,  setSentimentEvents]   = useState([]);
  const [articleMaps,      setArticleMaps]       = useState([]);

  // ── UI / selection state ───────────────────────────────────────────────────
  const [selectedArticleId,        setSelectedArticleId]        = useState("");
  const [selectedCompanySymbol,    setSelectedCompanySymbol]    = useState("");
  const [selectedCompanyArticleId, setSelectedCompanyArticleId] = useState("");

  // ── Feedback ───────────────────────────────────────────────────────────────
  const [message, setMessage] = useState("");
  const [error,   setError]   = useState("");
  const [loading, setLoading] = useState(false);

  // ── Agent ──────────────────────────────────────────────────────────────────
  const [agentResult,    setAgentResult]    = useState(null);
  const [isRunningAgent, setIsRunningAgent] = useState(false);

  // ── Scraping job ───────────────────────────────────────────────────────────
  const [scrapeTaskId,    setScrapeTaskId]    = useState("");
  const [scrapeJobStatus, setScrapeJobStatus] = useState(null);

  // ─────────────────────────────────────────────────────────────────────────
  // Helpers
  // ─────────────────────────────────────────────────────────────────────────

  const ok  = (text) => { setMessage(text); setError(""); };
  const err = (text) => { setError(text);   setMessage(""); };

  // ─────────────────────────────────────────────────────────────────────────
  // Data fetching
  // ─────────────────────────────────────────────────────────────────────────

  const fetchCompanySentiments = useCallback(async (companyList) => {
    const map = {};
    await Promise.all(
      companyList.map(async (company) => {
        try {
          const res = await apiClient.get(`/sentiment/company/${company.symbol}/latest`);
          map[company.symbol] = res.data;
        } catch {
          map[company.symbol] = null;
        }
      })
    );
    setCompanySentiments(map);
  }, []);

  const fetchDashboardData = useCallback(async () => {
    try {
      setLoading(true);
      setError("");

      const [companiesRes, sourcesRes, newsRes, eventsRes, mapsRes] = await Promise.all([
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
        const mktRes = await apiClient.get("/sentiment/market/latest");
        setMarketSentiment(mktRes.data);
      } catch {
        setMarketSentiment(null);
      }
    } catch {
      err("Could not load dashboard data. Make sure FastAPI is running.");
    } finally {
      setLoading(false);
    }
  }, [fetchCompanySentiments, selectedCompanySymbol, selectedArticleId]);

  useEffect(() => { fetchDashboardData(); }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // ─────────────────────────────────────────────────────────────────────────
  // Form submit handlers
  // ─────────────────────────────────────────────────────────────────────────

  async function handleAddCompany(payload) {
    try {
      await apiClient.post("/companies/", payload);
      ok("Company added successfully.");
      await fetchDashboardData();
    } catch (e) {
      err(e.response?.data?.detail || "Could not add company.");
    }
  }

  async function handleAddSource(payload) {
    try {
      await apiClient.post("/sources/", payload);
      ok("Source added successfully.");
      await fetchDashboardData();
    } catch (e) {
      err(e.response?.data?.detail || "Could not add source.");
    }
  }

  async function handleAddNewsArticle(payload) {
    try {
      await apiClient.post("/news/", payload);
      ok("News article added successfully.");
      await fetchDashboardData();
    } catch (e) {
      err(e.response?.data?.detail || "Could not add news article.");
    }
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Workflow actions
  // ─────────────────────────────────────────────────────────────────────────

  async function handleMapArticle() {
    if (!selectedArticleId) { err("Select an article first."); return; }
    try {
      await apiClient.post(`/article-company-maps/match/${selectedArticleId}`);
      ok("Article-company mapping completed.");
      await fetchDashboardData();
    } catch (e) { err(e.response?.data?.detail || "Could not map article."); }
  }

  async function handleDetectSentiment() {
    if (!selectedArticleId) { err("Select an article first."); return; }
    try {
      await apiClient.post(`/sentiment-events/detect/${selectedArticleId}`);
      ok("Sentiment events detected.");
      await fetchDashboardData();
    } catch (e) { err(e.response?.data?.detail || "Could not detect sentiment."); }
  }

  async function handleCalculateCompanySentiment() {
    if (!selectedCompanySymbol) { err("Select a company first."); return; }
    try {
      await apiClient.post(`/sentiment/company/${selectedCompanySymbol}/calculate`);
      ok("Company sentiment calculated.");
      await fetchDashboardData();
    } catch (e) { err(e.response?.data?.detail || "Could not calculate company sentiment."); }
  }

  async function handleCalculateMarketSentiment() {
    try {
      const res = await apiClient.post("/sentiment/market/calculate");
      setMarketSentiment(res.data);
      ok("Market sentiment calculated.");
      await fetchDashboardData();
    } catch (e) { err(e.response?.data?.detail || "Could not calculate market sentiment."); }
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Agent
  // ─────────────────────────────────────────────────────────────────────────

  async function handleRunAgentForArticle() {
    if (!selectedArticleId) { err("Select an article first."); return; }
    try {
      setIsRunningAgent(true);
      setError("");
      const res = await apiClient.post(`/agent/articles/${selectedArticleId}/run`);
      setAgentResult(res.data);
      ok("Agent pipeline completed for selected article.");
      await fetchDashboardData();
    } catch (e) { err(e.response?.data?.detail || "Could not run agent pipeline."); }
    finally { setIsRunningAgent(false); }
  }

  async function handleRunAgentForAll() {
    try {
      setIsRunningAgent(true);
      setError("");
      const res = await apiClient.post("/agent/articles/run-all");
      setAgentResult(res.data);
      ok("Agent pipeline completed for all articles.");
      await fetchDashboardData();
    } catch (e) { err(e.response?.data?.detail || "Could not run agent pipeline."); }
    finally { setIsRunningAgent(false); }
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Scraping
  // ─────────────────────────────────────────────────────────────────────────

  async function handleRunScraper({ source_id, limit, run_pipeline }) {
    try {
      setError("");
      setMessage("");
      setScrapeJobStatus(null);
      const res = await apiClient.post("/scraping-jobs/run", { source_id, limit, run_pipeline });
      setScrapeTaskId(res.data.task_id);
      ok(`Scraping job queued. Task ID: ${res.data.task_id}`);
    } catch (e) { err(e.response?.data?.detail || "Could not start scraping job."); }
  }

  async function handleCheckScrapingStatus() {
    if (!scrapeTaskId) { err("No scraping task ID found."); return; }
    try {
      const res = await apiClient.get(`/scraping-jobs/${scrapeTaskId}`);
      setScrapeJobStatus(res.data);
      if (res.data.state === "SUCCESS") {
        ok("Scraping job completed.");
        await fetchDashboardData();
      } else if (res.data.state === "FAILURE") {
        err("Scraping job failed.");
      }
    } catch (e) { err(e.response?.data?.detail || "Could not check scraping job."); }
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Render
  // ─────────────────────────────────────────────────────────────────────────

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">

      <Header loading={loading} onRefresh={fetchDashboardData} />

      <main className="mx-auto max-w-7xl px-6 py-8 space-y-8">

        <AlertBanner message={message} error={error} />

        {/* ── Stats row ─────────────────────────────────────────────────── */}
        <StatsBar
          marketSentiment={marketSentiment}
          companies={companies}
          sources={sources}
          newsArticles={newsArticles}
          onCalculateMarket={handleCalculateMarketSentiment}
        />

        {/* ── Action panels row ─────────────────────────────────────────── */}
        <section className="grid gap-6 xl:grid-cols-4">
          <AddCompanyPanel onSubmit={handleAddCompany} />

          <AddSourcePanel onSubmit={handleAddSource} />

          <WorkflowActionsPanel
            newsArticles={newsArticles}
            companies={companies}
            selectedArticleId={selectedArticleId}
            setSelectedArticleId={setSelectedArticleId}
            selectedCompanySymbol={selectedCompanySymbol}
            setSelectedCompanySymbol={setSelectedCompanySymbol}
            isRunningAgent={isRunningAgent}
            onMapArticle={handleMapArticle}
            onDetectSentiment={handleDetectSentiment}
            onCalculateCompanySentiment={handleCalculateCompanySentiment}
            onCalculateMarketSentiment={handleCalculateMarketSentiment}
            onRunAgentForArticle={handleRunAgentForArticle}
            onRunAgentForAll={handleRunAgentForAll}
          />

          <ScrapingJobsPanel
            scrapeTaskId={scrapeTaskId}
            scrapeJobStatus={scrapeJobStatus}
            onRunScraper={handleRunScraper}
            onCheckStatus={handleCheckScrapingStatus}
          />
        </section>

        {/* ── Agent result ──────────────────────────────────────────────── */}
        <AgentResultPanel agentResult={agentResult} />

        {/* ── Add news article (full width) ─────────────────────────────── */}
        <AddNewsArticlePanel sources={sources} onSubmit={handleAddNewsArticle} />

        {/* ── Sentiment + news feed ─────────────────────────────────────── */}
        <section className="grid gap-6 xl:grid-cols-2">
          <CompanySentimentList
            companies={companies}
            companySentiments={companySentiments}
          />
          <LatestNewsList newsArticles={newsArticles} />
        </section>

        {/* ── Company content viewer ────────────────────────────────────── */}
        <CompanyContentViewer
          companies={companies}
          newsArticles={newsArticles}
          articleMaps={articleMaps}
          selectedCompanySymbol={selectedCompanySymbol}
          setSelectedCompanySymbol={setSelectedCompanySymbol}
          selectedCompanyArticleId={selectedCompanyArticleId}
          setSelectedCompanyArticleId={setSelectedCompanyArticleId}
        />

        {/* ── Events + mappings ─────────────────────────────────────────── */}
        <section className="grid gap-6 xl:grid-cols-2">
          <SentimentEventsPanel sentimentEvents={sentimentEvents} />
          <ArticleMapsPanel     articleMaps={articleMaps} />
        </section>

      </main>
    </div>
  );
}