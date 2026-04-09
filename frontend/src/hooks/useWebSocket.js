import { useEffect, useRef, useState, useCallback } from "react";

const AGENT_NODES = [
  "news_fetcher",
  "sec_analyzer",
  "sentiment_scorer",
  "aggregator",
  "human_review",
  "portfolio_synthesizer",
];

const initialNodeStates = () =>
  Object.fromEntries(AGENT_NODES.map((n) => [n, "idle"]));

export function useResearchWebSocket() {
  const [nodeStates, setNodeStates] = useState(initialNodeStates());
  const [awaitingHuman, setAwaitingHuman] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [events, setEvents] = useState([]);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef(null);

  const connect = useCallback((ticker, query, sid) => {
    setNodeStates(initialNodeStates());
    setAwaitingHuman(false);
    setEvents([]);
    setSessionId(sid);

    const ws = new WebSocket(`ws://localhost:8000/ws/research`);
    wsRef.current = ws;

    ws.onopen = () => {
      setConnected(true);
      ws.send(JSON.stringify({ ticker, query, session_id: sid }));
    };

    ws.onmessage = (e) => {
      const msg = JSON.parse(e.data);
      setEvents((prev) => [...prev.slice(-99), msg]);

      if (msg.event === "on_chain_start" && AGENT_NODES.includes(msg.node)) {
        setNodeStates((prev) => ({ ...prev, [msg.node]: "running" }));
      }
      if (msg.event === "on_chain_end" && AGENT_NODES.includes(msg.node)) {
        setNodeStates((prev) => ({ ...prev, [msg.node]: "done" }));
      }
      if (msg.event === "hitl_required") {
        setAwaitingHuman(true);
        setNodeStates((prev) => ({ ...prev, human_review: "waiting" }));
      }
      if (msg.event === "error") {
        setNodeStates((prev) => {
          const updated = { ...prev };
          Object.keys(updated).forEach((k) => {
            if (updated[k] === "running") updated[k] = "error";
          });
          return updated;
        });
      }
    };

    ws.onclose = () => setConnected(false);
    ws.onerror = () => setConnected(false);
  }, []);

  const approve = useCallback(
    async (feedback) => {
      await fetch("/api/approve", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ticker: sessionId?.split("_")[0], session_id: sessionId, feedback }),
      });
      setAwaitingHuman(false);
      setNodeStates((prev) => ({ ...prev, human_review: "done" }));
    },
    [sessionId]
  );

  const reject = useCallback(
    async (feedback) => {
      await fetch("/api/reject", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ticker: sessionId?.split("_")[0], session_id: sessionId, feedback }),
      });
      setAwaitingHuman(false);
      setNodeStates(initialNodeStates());
    },
    [sessionId]
  );

  useEffect(() => () => wsRef.current?.close(), []);

  return { nodeStates, awaitingHuman, sessionId, events, connected, connect, approve, reject };
}
