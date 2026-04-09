import React, { useEffect, useRef } from "react";
import clsx from "clsx";

const EVENT_COLORS = {
  on_chain_start: "text-blue-400",
  on_chain_end: "text-green-400",
  hitl_required: "text-amber-400",
  error: "text-red-400",
};

export default function EventLog({ events }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [events]);

  return (
    <div className="rounded-xl border border-gray-800 bg-gray-950 p-4">
      <h3 className="text-gray-400 text-xs font-semibold uppercase tracking-widest mb-3">Live Event Log</h3>
      <div className="h-48 overflow-y-auto space-y-1 font-mono text-xs">
        {events.length === 0 && (
          <p className="text-gray-600 italic">Waiting for events...</p>
        )}
        {events.map((e, i) => (
          <div key={i} className="flex gap-2">
            <span className={clsx("shrink-0", EVENT_COLORS[e.event] || "text-gray-500")}>
              [{e.event}]
            </span>
            <span className="text-gray-400">{e.node}</span>
            {e.data && (
              <span className="text-gray-600 truncate">{e.data.slice(0, 80)}</span>
            )}
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
