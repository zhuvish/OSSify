"use client";

import { useState } from "react";

export default function AskAI() {
  const [open, setOpen] = useState(false);

  return (
    <>
      {/* Floating Chat */}

      <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50">

        {!open ? (
          <button
            onClick={() => setOpen(true)}
            className="
              bg-white
              border
              border-slate-200
              shadow-xl
              rounded-full
              px-6
              py-3
              w-[600px]
              text-left
              text-slate-500
            "
          >
            Ask about your codebase...
          </button>
        ) : (
          <div
            className="
              bg-white
              rounded-3xl
              shadow-2xl
              border
              border-slate-200
              w-[650px]
              p-6
            "
          >
            <div className="flex justify-between items-center mb-4">

              <h3 className="font-semibold text-lg">
                Ask me about your codebase
              </h3>

              <button
                onClick={() => setOpen(false)}
                className="text-slate-400"
              >
                ✕
              </button>
            </div>

            <div className="space-y-2 mb-5 text-sm">

              <button className="block text-indigo-600 hover:underline">
                Who is the expert on authentication?
              </button>

              <button className="block text-indigo-600 hover:underline">
                Which contributor knows routing?
              </button>

              <button className="block text-indigo-600 hover:underline">
                Explain repository structure
              </button>

            </div>

            <div className="flex gap-2">
              <input
                placeholder="Ask about your codebase..."
                className="
                  flex-1
                  border
                  rounded-full
                  px-4
                  py-3
                "
              />

              <button
                className="
                  bg-indigo-600
                  text-white
                  rounded-full
                  px-5
                "
              >
                →
              </button>
            </div>
          </div>
        )}
      </div>
    </>
  );
}