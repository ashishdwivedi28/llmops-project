"use client";
import { useState, useEffect } from "react";
import type { AppId } from "@/types/api";

const APP_CONFIGS = {
  mock_app:    { pipeline: "llm",   model: "mock",          description: "Mock app for testing" },
  default_llm: { pipeline: "llm",   model: "gemini",        description: "General purpose assistant" },
  rag_bot:     { pipeline: "rag",   model: "gemini",        description: "Document Q&A with retrieval" },
  code_agent:  { pipeline: "agent", model: "gemini",        description: "Agentic coding assistant" },
} as const;

export default function AdminPage() {
  const [selectedApp, setSelectedApp] = useState<AppId>("default_llm");
  const [lastInvoke, setLastInvoke] = useState<string | null>(null);

  useEffect(() => {
    const stored = localStorage.getItem("llmops_last_invoke");
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        setLastInvoke(JSON.stringify(parsed, null, 2));
      } catch {
        setLastInvoke("Error parsing local storage data");
      }
    }
  }, []);

  return (
    <div className="max-w-5xl mx-auto p-8 space-y-8">
      <h1 className="text-3xl font-bold text-gray-900">Admin Diagnostics</h1>

      <div className="grid md:grid-cols-2 gap-8">
        {/* App Config Inspector */}
        <div className="space-y-4">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 h-full">
            <h2 className="text-xl font-semibold mb-4 text-gray-800">App Config Inspector</h2>
            
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">Select App ID</label>
              <select 
                value={selectedApp}
                onChange={(e) => setSelectedApp(e.target.value as AppId)}
                className="w-full p-2 border rounded-md bg-white"
              >
                {Object.keys(APP_CONFIGS).map((id) => (
                  <option key={id} value={id}>{id}</option>
                ))}
              </select>
            </div>

            <div className="bg-gray-50 p-4 rounded-md border border-gray-200">
              <pre className="text-sm text-gray-700 whitespace-pre-wrap font-mono">
                {JSON.stringify(APP_CONFIGS[selectedApp], null, 2)}
              </pre>
            </div>
          </div>
        </div>

        {/* Last Invoke Diagnostics */}
        <div className="space-y-4">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 h-full">
            <h2 className="text-xl font-semibold mb-4 text-gray-800">Last Invoke Diagnostics</h2>
            <p className="text-sm text-gray-500 mb-4">
              Reads from browser localStorage (populated by Chat page).
            </p>

            <div className="bg-gray-900 p-4 rounded-lg overflow-x-auto min-h-[150px]">
              <pre className="text-xs text-green-400 font-mono">
                {lastInvoke || "No invoke recorded yet. Use the chat page first."}
              </pre>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}