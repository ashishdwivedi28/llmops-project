"use client";
import { useState, useEffect } from "react";
import { getHealth, invoke } from "@/lib/api";
import type { HealthResponse } from "@/types/api";

export default function HealthPage() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [healthError, setHealthError] = useState<string | null>(null);
  const [smokeTestResult, setSmokeTestResult] = useState<string | null>(null);
  const [isTesting, setIsTesting] = useState(false);

  useEffect(() => {
    getHealth()
      .then(setHealth)
      .catch((err) => setHealthError(err.message));
  }, []);

  const runSmokeTest = async () => {
    setIsTesting(true);
    setSmokeTestResult(null);
    try {
      const res = await invoke("mock_app", "ping");
      setSmokeTestResult(JSON.stringify(res, null, 2));
    } catch (err) {
      setSmokeTestResult(
        JSON.stringify({ error: err instanceof Error ? err.message : String(err) }, null, 2)
      );
    } finally {
      setIsTesting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-8 space-y-8">
      <h1 className="text-3xl font-bold text-gray-900">System Health</h1>
      
      <div className="grid md:grid-cols-2 gap-6">
        {/* Backend API Status Card */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <h2 className="text-xl font-semibold mb-4 text-gray-800">Backend API</h2>
          
          {health ? (
            <div className="flex items-center gap-3">
              <span className={`h-3 w-3 rounded-full ${health.status === 'ok' ? 'bg-green-500' : 'bg-red-500'}`} />
              <div>
                <p className="font-medium text-gray-900 capitalize">{health.status}</p>
                <p className="text-sm text-gray-500">{health.message}</p>
              </div>
            </div>
          ) : healthError ? (
             <div className="flex items-center gap-3">
              <span className="h-3 w-3 rounded-full bg-red-500" />
              <p className="text-red-600 font-medium">Unreachable: {healthError}</p>
            </div>
          ) : (
            <div className="flex items-center gap-3">
               <span className="h-3 w-3 rounded-full bg-gray-300 animate-pulse" />
               <p className="text-gray-500">Checking...</p>
            </div>
          )}
        </div>

        {/* Smoke Test Card */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex justify-between items-center mb-4">
             <h2 className="text-xl font-semibold text-gray-800">Smoke Test</h2>
             <button
              onClick={runSmokeTest}
              disabled={isTesting}
              className="px-4 py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors"
             >
               {isTesting ? "Running..." : "Run Test"}
             </button>
          </div>
          <p className="text-sm text-gray-500 mb-4">
            Sends a POST /invoke request to the mock_app.
          </p>
          
          <div className="bg-gray-900 rounded-lg p-4 overflow-x-auto">
            <pre className="text-xs text-green-400 font-mono">
              {smokeTestResult || "// Result will appear here..."}
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
}