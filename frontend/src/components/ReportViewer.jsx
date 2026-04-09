import React from "react";

export default function ReportViewer({ sessionId, reportText }) {
  if (!reportText) return null;

  return (
    <div className="rounded-xl border border-gray-700 bg-gray-900 p-5 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-green-400 font-bold text-lg">✅ Research Report Ready</h2>
        {sessionId && (
          <a
            href={`/api/report/${sessionId}`}
            target="_blank"
            rel="noopener noreferrer"
            className="bg-blue-700 hover:bg-blue-600 text-white text-sm font-semibold py-1.5 px-4 rounded-lg transition-colors"
          >
            ⬇ Download PDF
          </a>
        )}
      </div>

      <div className="bg-gray-950 rounded-lg p-4 text-sm text-gray-200 max-h-96 overflow-y-auto whitespace-pre-wrap leading-relaxed">
        {reportText}
      </div>
    </div>
  );
}
