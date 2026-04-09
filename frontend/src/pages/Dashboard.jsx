import React, { useState } from "react";
import { v4 as uuidv4 } from "uuid";
import AgentGraph from "../components/AgentGraph";
import HumanReview from "../components/HumanReview";
import ReportViewer from "../components/ReportViewer";
import EventLog from "../components/EventLog";
import StatusBadge from "../components/StatusBadge";
import { useResearchWebSocket } from "../hooks/useWebSocket";

export default function Dashboard() {
  const [ticker, setTicker] = useState("");
  const [query, setQuery] = useState("");
  const [reportText, setReportText] = useState(null);
  const [aggregatedContext, setAggregatedContext] = useState("");
  const [isRunning, setIsRunning] = useState(false);

  const { nodeStates, awaitingHuman, sessionId, events, connected, connect, approve, reject } =
    useResearchWebSocket();

  const handleStart = () => {
    if (!ticker.trim()) return;
    const sid = uuidv4();
    setReportText(null);
    setIsRunning(true);
    connect(
      ticker.trim().toUpperCase(),
      query.trim() || `Analyse ${ticker.trim().toUpperCase()} stock for investment`,
      sid
    );
  };

  // Extract aggregated context and final report from events
  React.useEffect(() => {
    const latest = events[events.length - 1];
    if (!latest) return;
    if (latest.node === "aggregator" && latest.event === "on_chain_end") {
      setAggregatedContext(latest.data || "");
    }
    if (latest.node === "portfolio_synthesizer" && latest.event === "on_chain_end") {
      setReportText(latest.data || "Report complete — check the DB for full text.");
      setIsRunning(false);
    }
    if (latest.event === "error") {
      setIsRunning(false);
    }
  }, [events]);

  const agentCards = [
    { id: "news_fetcher", label: "News Fetcher" },
    { id: "sec_analyzer", label: "SEC Analyzer" },
    { id: "sentiment_scorer", label: "Sentiment Scorer" },
    { id: "aggregator", label: "Aggregator" },
    { id: "human_review", label: "Human Review" },
    { id: "portfolio_synthesizer", label: "Synthesizer" },
  ];

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 p-6 max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">📈 Financial Research System</h1>
          <p className="text-gray-500 text-sm">Multi-agent AI with Human-in-the-Loop oversight</p>
        </div>
        <div className="flex items-center gap-2 text-xs">
          <span className={connected ? "text-green-400" : "text-gray-600"}>
            ● {connected ? "Connected" : "Disconnected"}
          </span>
        </div>
      </div>

      {/* Input */}
      <div className="rounded-xl border border-gray-800 bg-gray-900 p-5 space-y-4">
        <h2 className="font-semibold text-gray-300">Start Research</h2>
        <div className="flex gap-3">
          <input
            className="w-28 bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm uppercase font-mono focus:outline-none focus:border-blue-500"
            placeholder="AAPL"
            value={ticker}
            onChange={(e) => setTicker(e.target.value.toUpperCase())}
            disabled={isRunning}
          />
          <input
            className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
            placeholder="Research question (e.g. Should we invest in Apple?)"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            disabled={isRunning}
          />
          <button
            onClick={handleStart}
            disabled={!ticker.trim() || isRunning}
            className="bg-blue-700 hover:bg-blue-600 disabled:opacity-40 disabled:cursor-not-allowed text-white font-semibold px-5 py-2 rounded-lg transition-colors"
          >
            {isRunning ? "Running..." : "Run Research"}
          </button>
        </div>
      </div>

      {/* Agent status cards */}
      <div className="grid grid-cols-3 gap-3 sm:grid-cols-6">
        {agentCards.map(({ id, label }) => (
          <div key={id} className="rounded-lg border border-gray-800 bg-gray-900 p-3 text-center space-y-1">
            <p className="text-xs text-gray-400 font-medium truncate">{label}</p>
            <StatusBadge status={nodeStates[id]} />
          </div>
        ))}
      </div>

      {/* Live graph */}
      <AgentGraph nodeStates={nodeStates} />

      {/* Event log */}
      <EventLog events={events} />

      {/* HITL panel */}
      {awaitingHuman && (
        <HumanReview
          onApprove={approve}
          onReject={reject}
          aggregatedContext={aggregatedContext}
        />
      )}

      {/* Report */}
      <ReportViewer sessionId={sessionId} reportText={reportText} />
    </div>
  );
}
