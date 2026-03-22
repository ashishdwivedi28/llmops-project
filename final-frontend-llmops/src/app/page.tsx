import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 flex flex-col justify-center items-center p-6">
      <div className="max-w-3xl w-full space-y-12 text-center">
        
        <div className="space-y-4">
          <h1 className="text-5xl font-extrabold text-gray-900 tracking-tight">
            LLMOps <span className="text-blue-600">Pipeline</span>
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Config-driven LLM orchestration — RAG, Agents, and direct LLM in one system.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-6 text-left">
          
          {/* Card 1: GET / */}
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between mb-4">
              <span className="bg-green-100 text-green-700 px-3 py-1 rounded-full text-xs font-bold font-mono">GET /</span>
              <span className="text-gray-400 text-sm">Health Check</span>
            </div>
            <p className="text-gray-600 text-sm mb-4">
              Verifies the backend API status and connectivity.
            </p>
            <div className="bg-gray-50 p-3 rounded-md border border-gray-100 font-mono text-xs text-gray-500">
              {"{ status: 'ok', message: '...' }"}
            </div>
          </div>

          {/* Card 2: POST /invoke */}
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between mb-4">
              <span className="bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-xs font-bold font-mono">POST /invoke</span>
              <span className="text-gray-400 text-sm">Main Endpoint</span>
            </div>
            <p className="text-gray-600 text-sm mb-4">
              Orchestrates LLM calls, RAG retrieval, and Agent actions based on app_id.
            </p>
            <div className="bg-gray-50 p-3 rounded-md border border-gray-100 font-mono text-xs text-gray-500">
              {"{ app_id: '...', user_input: '...' }"}
            </div>
          </div>
        </div>

        <div className="flex flex-wrap gap-4 justify-center mt-8">
          <Link 
            href="/chat"
            className="px-8 py-3 bg-blue-600 text-white font-medium rounded-full hover:bg-blue-700 transition-colors shadow-lg shadow-blue-200"
          >
            Start Chatting
          </Link>
          <Link 
            href="/health"
            className="px-8 py-3 bg-white text-gray-700 font-medium rounded-full hover:bg-gray-50 border border-gray-200 transition-colors"
          >
            System Health
          </Link>
          <Link 
            href="/admin"
            className="px-8 py-3 bg-white text-gray-700 font-medium rounded-full hover:bg-gray-50 border border-gray-200 transition-colors"
          >
            Admin Panel
          </Link>
        </div>

      </div>
    </div>
  );
}