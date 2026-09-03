'use client';
import { useState } from 'react';

const API = 'http://localhost:8000';

type Tab = 'recovery' | 'risk' | 'growth' | 'finance' | 'audit' | 'performance' | 'harness';

export default function Home() {
  const [tab, setTab] = useState<Tab>('recovery');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [metrics, setMetrics] = useState<any>(null);

  const run = async (endpoint: string, method: string = 'POST') => {
    setLoading(true);
    setResults(null);
    try {
      const res = await fetch(`${API}/api/${endpoint}`, { method });
      const data = await res.json();
      setResults(data);
      if (endpoint === 'run-batch') {
        const m = await fetch(`${API}/api/metrics`);
        setMetrics(await m.json());
      }
    } catch (e) {
      setResults({ error: 'Failed to connect to backend' });
    }
    setLoading(false);
  };

  const tabs = [
    { id: 'recovery',    label: '💰 Recovery' },
    { id: 'risk',        label: '🛡️ Risk' },
    { id: 'growth',      label: '📈 Growth' },
    { id: 'finance',     label: '📊 Finance' },
    { id: 'audit',       label: '📋 Audit' },
    { id: 'performance', label: '⚡ Performance' },
    { id: 'harness',     label: '🧪 Harness' },
  ];

  return (
    <main className="min-h-screen bg-gray-950 text-white p-6">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-white">PayPulse</h1>
        <p className="text-gray-400 mt-1">AI-powered merchant intelligence — built on Razorpay APIs</p>
      </div>

      {metrics && (
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="bg-gray-900 rounded-xl p-4 border border-gray-800">
            <p className="text-gray-400 text-sm">Total Payments</p>
            <p className="text-2xl font-bold text-white">{metrics.total_payments}</p>
          </div>
          <div className="bg-gray-900 rounded-xl p-4 border border-gray-800">
            <p className="text-gray-400 text-sm">Recovery Attempted</p>
            <p className="text-2xl font-bold text-green-400">{metrics.recovery_attempted}</p>
          </div>
          <div className="bg-gray-900 rounded-xl p-4 border border-gray-800">
            <p className="text-gray-400 text-sm">Amount Recovered</p>
            <p className="text-2xl font-bold text-green-400">₹{metrics.amount_recovered?.toLocaleString()}</p>
          </div>
        </div>
      )}

      <div className="flex gap-2 mb-6 flex-wrap">
        {tabs.map(t => (
          <button key={t.id} onClick={() => { setTab(t.id as Tab); }}
            className={`px-4 py-2 rounded-lg font-medium transition-all ${
              tab === t.id ? 'bg-blue-600 text-white' : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
            }`}>
            {t.label}
          </button>
        ))}
      </div>

      <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">

        {tab === 'recovery' && (
          <div>
            <h2 className="text-xl font-bold mb-2">AI Revenue Recovery</h2>
            <p className="text-gray-400 mb-4">Detects failed payments, diagnoses root cause, executes Hinglish recovery messages with Razorpay payment links.</p>
            <button onClick={() => run('run-batch')} disabled={loading}
              className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 px-6 py-3 rounded-lg font-bold mb-4">
              {loading ? 'Running Agent...' : '▶ Run Recovery Agent'}
            </button>
            {results?.results?.map((r: any, i: number) => (
              <div key={i} className="bg-gray-800 rounded-lg p-4 mb-3 border border-gray-700">
                {r.status === 'BLOCKED' ? (
                  <p className="text-red-400 font-bold text-sm">🚫 BLOCKED — {r.reason}</p>
                ) : (
                  <>
                    <p className="text-green-400 font-bold text-sm mb-1">✓ Recovery Attempted</p>
                    <p className="text-white text-sm mb-2">💬 {r.result?.message}</p>
                    <p className="text-blue-400 text-xs">🔗 {r.result?.link}</p>
                    <details className="mt-2">
                      <summary className="text-gray-400 text-xs cursor-pointer">View AI Reasoning</summary>
                      <p className="text-gray-300 text-xs mt-1">{r.result?.diagnosis}</p>
                    </details>
                  </>
                )}
              </div>
            ))}
          </div>
        )}

        {tab === 'risk' && (
          <div>
            <h2 className="text-xl font-bold mb-2">AI Risk Manager</h2>
            <p className="text-gray-400 mb-4">Dynamic risk scoring with Human-in-the-Loop review for medium risk payments.</p>
            <button onClick={() => run('run-batch')} disabled={loading}
              className="bg-red-600 hover:bg-red-700 disabled:opacity-50 px-6 py-3 rounded-lg font-bold mb-4">
              {loading ? 'Running...' : '▶ Run Risk Agent'}
            </button>
            <button onClick={() => run('hitl-queue', 'GET')} disabled={loading}
              className="bg-yellow-600 hover:bg-yellow-700 disabled:opacity-50 px-6 py-3 rounded-lg font-bold mb-4 ml-2">
              📋 Load Review Queue
            </button>

            {results?.results?.map((r: any, i: number) => (
              <div key={i} className={`rounded-lg p-4 mb-3 border ${
                r.status === 'BLOCKED' ? 'bg-red-950 border-red-800' :
                r.status === 'HUMAN_REVIEW' ? 'bg-yellow-950 border-yellow-800' :
                'bg-gray-800 border-gray-700'
              }`}>
                <div className="flex justify-between items-center mb-2">
                  <p className={`font-bold text-sm ${
                    r.status === 'BLOCKED' ? 'text-red-400' :
                    r.status === 'HUMAN_REVIEW' ? 'text-yellow-400' :
                    'text-green-400'
                  }`}>
                    {r.status === 'BLOCKED' ? '🚫 AUTO BLOCKED' :
                     r.status === 'HUMAN_REVIEW' ? '⚠️ HUMAN REVIEW REQUIRED' :
                     '✓ AUTO APPROVED'}
                  </p>
                  <span className={`text-xs font-bold px-2 py-1 rounded ${
                    (r.risk_score || r.result?.risk_score) >= 70 ? 'bg-red-600' :
                    (r.risk_score || r.result?.risk_score) >= 40 ? 'bg-yellow-600' :
                    'bg-green-600'
                  }`}>
                    Risk: {r.risk_score || r.result?.risk_score}/100
                  </span>
                </div>
                {r.factors?.map((f: any, j: number) => (
                  <p key={j} className="text-gray-400 text-xs">• {f.factor}: +{f.points}</p>
                ))}
              </div>
            ))}

            {/* HITL Queue */}
            {Array.isArray(results) && results.map((item: any, i: number) => (
              <div key={i} className="bg-yellow-950 border border-yellow-800 rounded-lg p-4 mb-3">
                <div className="flex justify-between items-center mb-2">
                  <div>
                    <p className="text-yellow-400 font-bold text-sm">⚠️ {item.customer_name}</p>
                    <p className="text-gray-400 text-xs">₹{item.amount} — {item.failure_code}</p>
                    <p className="text-gray-400 text-xs">Risk Score: {item.risk_score}/100</p>
                  </div>
                  <div className="flex gap-2">
                    <button onClick={async () => {
                      await fetch(`${API}/api/hitl-decision/${item.payment_id}?decision=APPROVE`, {method:'POST'});
                      alert('Approved!');
                    }} className="bg-green-600 hover:bg-green-700 px-3 py-1 rounded text-xs font-bold">
                      ✓ Approve
                    </button>
                    <button onClick={async () => {
                      await fetch(`${API}/api/hitl-decision/${item.payment_id}?decision=REJECT`, {method:'POST'});
                      alert('Rejected!');
                    }} className="bg-red-600 hover:bg-red-700 px-3 py-1 rounded text-xs font-bold">
                      ✗ Reject
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {tab === 'growth' && (
          <div>
            <h2 className="text-xl font-bold mb-2">AI Growth Agent</h2>
            <p className="text-gray-400 mb-4">Analyzes customer purchase history and generates personalized upsell offers in Hinglish.</p>
            <button onClick={() => run('run-growth')} disabled={loading}
              className="bg-purple-600 hover:bg-purple-700 disabled:opacity-50 px-6 py-3 rounded-lg font-bold mb-4">
              {loading ? 'Running Agent...' : '▶ Run Growth Agent'}
            </button>
            {results?.results?.map((r: any, i: number) => (
              <div key={i} className="bg-gray-800 rounded-lg p-4 mb-3 border border-gray-700">
                <p className="text-purple-400 font-bold text-sm mb-1">👤 {r.customer}</p>
                <p className="text-white text-sm mb-2">
                  {(() => { try { return JSON.parse(r.upsell_result).message; } catch { return r.upsell_result; } })()}
                </p>
                <p className="text-blue-400 text-xs">🔗 {r.payment_link}</p>
              </div>
            ))}
          </div>
        )}

        {tab === 'finance' && (
          <div>
            <h2 className="text-xl font-bold mb-2">AI Finance Controller</h2>
            <p className="text-gray-400 mb-4">Reconciles settlement records, identifies exceptions, generates financial reports.</p>
            <button onClick={() => run('run-finance')} disabled={loading}
              className="bg-amber-600 hover:bg-amber-700 disabled:opacity-50 px-6 py-3 rounded-lg font-bold mb-4">
              {loading ? 'Running Agent...' : '▶ Run Finance Agent'}
            </button>
            {results && (
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-800 rounded-lg p-4">
                  <p className="text-gray-400 text-sm">Total Records</p>
                  <p className="text-2xl font-bold">{results.total_records}</p>
                </div>
                <div className="bg-gray-800 rounded-lg p-4">
                  <p className="text-gray-400 text-sm">Settled</p>
                  <p className="text-2xl font-bold text-green-400">{results.settled}</p>
                </div>
                <div className="bg-gray-800 rounded-lg p-4">
                  <p className="text-gray-400 text-sm">Pending</p>
                  <p className="text-2xl font-bold text-yellow-400">{results.pending}</p>
                </div>
                <div className="bg-gray-800 rounded-lg p-4">
                  <p className="text-gray-400 text-sm">Failed</p>
                  <p className="text-2xl font-bold text-red-400">{results.failed}</p>
                </div>
                <div className="bg-gray-800 rounded-lg p-4">
                  <p className="text-gray-400 text-sm">Total Amount</p>
                  <p className="text-2xl font-bold">₹{results.total_amount?.toLocaleString()}</p>
                </div>
                <div className="bg-gray-800 rounded-lg p-4">
                  <p className="text-gray-400 text-sm">Settled Amount</p>
                  <p className="text-2xl font-bold text-green-400">₹{results.settled_amount?.toLocaleString()}</p>
                </div>
                <div className="bg-gray-800 rounded-lg p-4 col-span-2">
                  <p className="text-gray-400 text-sm mb-2">AI Analysis</p>
                  <p className="text-gray-300 text-xs">{results.ai_analysis}</p>
                </div>
              </div>
            )}
          </div>
        )}

        {tab === 'audit' && (
          <div>
            <h2 className="text-xl font-bold mb-2">Audit Trail</h2>
            <p className="text-gray-400 mb-4">Every agent decision logged with reasoning and timestamp.</p>
            <button onClick={() => run('audit-trail', 'GET')} disabled={loading}
              className="bg-gray-600 hover:bg-gray-700 disabled:opacity-50 px-6 py-3 rounded-lg font-bold mb-4">
              {loading ? 'Loading...' : '📋 Load Audit Trail'}
            </button>
            {Array.isArray(results) && results.map((log: any, i: number) => (
              <div key={i} className="bg-gray-800 rounded-lg p-3 mb-2 border border-gray-700">
                <div className="flex justify-between items-center mb-1">
                  <span className="text-blue-400 text-xs font-bold">{log.agent}</span>
                  <span className="text-gray-500 text-xs">{log.timestamp?.slice(0, 19)}</span>
                </div>
                <p className="text-green-400 text-xs font-bold">{log.decision}</p>
                <p className="text-gray-300 text-xs mt-1">{log.reasoning?.slice(0, 150)}...</p>
              </div>
            ))}
          </div>
        )}

        {tab === 'performance' && (
          <div>
            <h2 className="text-xl font-bold mb-2">Agent Performance Dashboard</h2>
            <p className="text-gray-400 mb-4">Real-time metrics across all 4 AI agents.</p>
            <button onClick={() => run('performance', 'GET')} disabled={loading}
              className="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 px-6 py-3 rounded-lg font-bold mb-6">
              {loading ? 'Loading...' : '⚡ Load Performance'}
            </button>
            {results && (
              <div className="grid grid-cols-2 gap-4">
                {/* Recovery */}
                <div className="bg-gray-800 rounded-xl p-4 border border-blue-800 col-span-2">
                  <p className="text-blue-400 font-bold mb-3">💰 Recovery Agent</p>
                  <div className="grid grid-cols-4 gap-3">
                    <div>
                      <p className="text-gray-400 text-xs">Total Payments</p>
                      <p className="text-2xl font-bold">{results.recovery?.total_payments}</p>
                    </div>
                    <div>
                      <p className="text-gray-400 text-xs">Recovered</p>
                      <p className="text-2xl font-bold text-green-400">{results.recovery?.attempted}</p>
                    </div>
                    <div>
                      <p className="text-gray-400 text-xs">Amount</p>
                      <p className="text-2xl font-bold text-green-400">₹{results.recovery?.amount_recovered?.toLocaleString()}</p>
                    </div>
                    <div>
                      <p className="text-gray-400 text-xs">Recovery Rate</p>
                      <p className="text-2xl font-bold text-green-400">{results.recovery?.recovery_rate}%</p>
                    </div>
                  </div>
                </div>
                {/* Risk */}
                <div className="bg-gray-800 rounded-xl p-4 border border-red-800">
                  <p className="text-red-400 font-bold mb-3">🛡️ Risk Agent</p>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <p className="text-gray-400 text-sm">Auto Approved</p>
                      <p className="text-green-400 font-bold">{results.risk?.approved}</p>
                    </div>
                    <div className="flex justify-between">
                      <p className="text-gray-400 text-sm">Auto Blocked</p>
                      <p className="text-red-400 font-bold">{results.risk?.blocked}</p>
                    </div>
                    <div className="flex justify-between">
                      <p className="text-gray-400 text-sm">Human Review</p>
                      <p className="text-yellow-400 font-bold">{results.risk?.human_review}</p>
                    </div>
                  </div>
                </div>
                {/* Memory */}
                <div className="bg-gray-800 rounded-xl p-4 border border-purple-800">
                  <p className="text-purple-400 font-bold mb-3">🧠 Memory Layer</p>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <p className="text-gray-400 text-sm">Customers Tracked</p>
                      <p className="text-purple-400 font-bold">{results.memory?.customers_tracked}</p>
                    </div>
                    <div className="flex justify-between">
                      <p className="text-gray-400 text-sm">Escalated Cases</p>
                      <p className="text-yellow-400 font-bold">{results.memory?.escalated}</p>
                    </div>
                  </div>
                </div>
                {/* Finance */}
                <div className="bg-gray-800 rounded-xl p-4 border border-amber-800 col-span-2">
                  <p className="text-amber-400 font-bold mb-3">📊 Finance Agent</p>
                  <div className="flex justify-between">
                    <p className="text-gray-400 text-sm">Reconciliations Run</p>
                    <p className="text-amber-400 font-bold">{results.finance?.reconciliations}</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
        {tab === 'harness' && (
  <div>
    <h2 className="text-xl font-bold mb-2">Agent Evaluation Harness</h2>
    <p className="text-gray-400 mb-4">
      Runs 10 predefined test cases across RecoveryAgent and RiskAgent. 
      Measures accuracy, intervention correctness, and edge case handling.
    </p>
    <button onClick={() => run('run-harness')} disabled={loading}
      className="bg-green-600 hover:bg-green-700 disabled:opacity-50 px-6 py-3 rounded-lg font-bold mb-4">
      {loading ? 'Running Tests...' : '🧪 Run Harness'}
    </button>

    {results && (
      <>
        {/* Summary */}
        <div className="grid grid-cols-4 gap-4 mb-6">
          <div className="bg-gray-800 rounded-xl p-4 border border-gray-700">
            <p className="text-gray-400 text-xs">Total Tests</p>
            <p className="text-2xl font-bold">{results.total_tests}</p>
          </div>
          <div className="bg-gray-800 rounded-xl p-4 border border-green-800">
            <p className="text-gray-400 text-xs">Passed</p>
            <p className="text-2xl font-bold text-green-400">{results.passed}</p>
          </div>
          <div className="bg-gray-800 rounded-xl p-4 border border-red-800">
            <p className="text-gray-400 text-xs">Failed</p>
            <p className="text-2xl font-bold text-red-400">{results.failed}</p>
          </div>
          <div className={`rounded-xl p-4 border ${
            results.grade === 'A' ? 'bg-green-950 border-green-600' :
            results.grade === 'B' ? 'bg-yellow-950 border-yellow-600' :
            'bg-red-950 border-red-600'
          }`}>
            <p className="text-gray-400 text-xs">Accuracy</p>
            <p className="text-2xl font-bold text-white">
              {results.accuracy} ({results.grade})
            </p>
          </div>
        </div>

        {/* Test Results */}
        {results.results?.map((r: any, i: number) => (
          <div key={i} className={`rounded-lg p-4 mb-3 border ${
            r.status === 'PASS' ? 'bg-green-950 border-green-800' :
            r.status === 'FAIL' ? 'bg-red-950 border-red-800' :
            'bg-yellow-950 border-yellow-800'
          }`}>
            <div className="flex justify-between items-center mb-2">
              <div className="flex items-center gap-2">
                <span className={`text-xs font-bold px-2 py-1 rounded ${
                  r.status === 'PASS' ? 'bg-green-600' :
                  r.status === 'FAIL' ? 'bg-red-600' : 'bg-yellow-600'
                }`}>{r.status}</span>
                <span className="text-blue-400 text-xs font-bold">{r.test_id}</span>
                <span className="text-purple-400 text-xs">{r.agent}</span>
              </div>
              <span className="text-gray-500 text-xs">{r.response_time}</span>
            </div>
            <p className="text-white text-sm mb-2">{r.description}</p>
            <div className="grid grid-cols-2 gap-2">
              <div>
                <p className="text-gray-400 text-xs">Expected</p>
                <p className="text-yellow-400 text-xs">
                  {JSON.stringify(r.expected)}
                </p>
              </div>
              <div>
                <p className="text-gray-400 text-xs">Got</p>
                <p className="text-green-400 text-xs">
                  {JSON.stringify(r.got)}
                </p>
              </div>
            </div>
            {r.failures?.length > 0 && (
              <p className="text-red-400 text-xs mt-2">
                ❌ {r.failures.join(', ')}
              </p>
            )}
          </div>
        ))}
      </>
    )}
  </div>
)}

      </div>
    </main>
  );
}