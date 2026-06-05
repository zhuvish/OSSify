"use client";

import { MessageCircle } from "lucide-react";

export default function AskAI() {
  return (
    <div className="fixed bottom-6 right-6 z-50">
      <button
        type="button"
        className="inline-flex items-center gap-2 rounded-full bg-violet-600 px-5 py-3 text-white shadow-2xl shadow-violet-500/25 transition hover:bg-violet-700"
      >
        <MessageCircle size={18} />
        Ask AI
      </button>
    </div>
  );
}
