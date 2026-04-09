import React from "react";
import clsx from "clsx";

const VARIANTS = {
  idle: "bg-gray-800 text-gray-400",
  running: "bg-blue-900 text-blue-300 animate-pulse",
  done: "bg-green-900 text-green-300",
  error: "bg-red-900 text-red-300",
  waiting: "bg-amber-900 text-amber-300",
};

export default function StatusBadge({ status }) {
  return (
    <span className={clsx("text-xs font-semibold px-2 py-0.5 rounded-full capitalize", VARIANTS[status] || VARIANTS.idle)}>
      {status}
    </span>
  );
}
