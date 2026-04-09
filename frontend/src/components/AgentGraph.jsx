import React, { useMemo } from "react";
import ReactFlow, { Background, Controls, MiniMap } from "reactflow";
import "reactflow/dist/style.css";
import clsx from "clsx";

const STATUS_COLORS = {
  idle: "#374151",
  running: "#2563eb",
  done: "#16a34a",
  error: "#dc2626",
  waiting: "#d97706",
};

const NODE_LABELS = {
  news_fetcher: "📰 News Fetcher",
  sec_analyzer: "📄 SEC Analyzer",
  sentiment_scorer: "📊 Sentiment Scorer",
  aggregator: "🔗 Aggregator",
  human_review: "👤 Human Review",
  portfolio_synthesizer: "📝 Synthesizer",
};

const NODE_POSITIONS = {
  news_fetcher: { x: 50, y: 80 },
  sec_analyzer: { x: 50, y: 180 },
  sentiment_scorer: { x: 50, y: 280 },
  aggregator: { x: 300, y: 180 },
  human_review: { x: 550, y: 120 },
  portfolio_synthesizer: { x: 550, y: 240 },
};

const EDGES = [
  { id: "e1", source: "news_fetcher", target: "sec_analyzer" },
  { id: "e2", source: "sec_analyzer", target: "sentiment_scorer" },
  { id: "e3", source: "sentiment_scorer", target: "aggregator" },
  { id: "e4", source: "aggregator", target: "human_review" },
  { id: "e5", source: "human_review", target: "portfolio_synthesizer", label: "approved" },
  { id: "e6", source: "human_review", target: "news_fetcher", label: "rejected", style: { stroke: "#dc2626" } },
];

export default function AgentGraph({ nodeStates }) {
  const nodes = useMemo(() =>
    Object.entries(NODE_POSITIONS).map(([id, position]) => ({
      id,
      position,
      data: {
        label: (
          <div className="text-xs font-semibold">
            {NODE_LABELS[id]}
            <div className="text-[10px] mt-0.5 opacity-70 capitalize">{nodeStates[id] || "idle"}</div>
          </div>
        ),
      },
      style: {
        background: STATUS_COLORS[nodeStates[id]] || STATUS_COLORS.idle,
        color: "#fff",
        border: "none",
        borderRadius: 8,
        padding: "8px 14px",
        minWidth: 140,
        transition: "background 0.4s ease",
      },
    })), [nodeStates]);

  return (
    <div className="h-80 w-full rounded-xl overflow-hidden border border-gray-800 bg-gray-900">
      <ReactFlow nodes={nodes} edges={EDGES} fitView>
        <Background color="#374151" gap={20} />
        <Controls />
        <MiniMap nodeColor={(n) => n.style?.background || "#374151"} style={{ background: "#111827" }} />
      </ReactFlow>
    </div>
  );
}
