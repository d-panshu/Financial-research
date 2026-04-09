import React, { useState } from "react";

export default function HumanReview({ onApprove, onReject, aggregatedContext }) {
  const [feedback, setFeedback] = useState("");

  return (
    <div className="rounded-xl border border-amber-500 bg-amber-950/40 p-5 space-y-4">
      <div className="flex items-center gap-2">
        <span className="text-amber-400 text-lg">⚠️</span>
        <h2 className="text-amber-300 font-bold text-lg">Human Review Required</h2>
      </div>

      <div className="bg-gray-900 rounded-lg p-4 text-xs text-gray-300 font-mono max-h-52 overflow-y-auto whitespace-pre-wrap">
        {aggregatedContext || "Aggregated context loading..."}
      </div>

      <textarea
        className="w-full bg-gray-900 border border-gray-700 rounded-lg p-3 text-sm text-gray-100 placeholder-gray-500 resize-none focus:outline-none focus:border-blue-500"
        rows={3}
        placeholder="Optional feedback for the agent (e.g. focus on Q3 earnings, ignore macro noise)..."
        value={feedback}
        onChange={(e) => setFeedback(e.target.value)}
      />

      <div className="flex gap-3">
        <button
          onClick={() => onApprove(feedback)}
          className="flex-1 bg-green-700 hover:bg-green-600 text-white font-semibold py-2 px-4 rounded-lg transition-colors"
        >
          ✅ Approve & Generate Report
        </button>
        <button
          onClick={() => onReject(feedback)}
          className="flex-1 bg-red-800 hover:bg-red-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors"
        >
          ❌ Reject & Re-run
        </button>
      </div>
    </div>
  );
}
