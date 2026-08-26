'use client';
import { useState } from 'react';

const API = 'http://localhost:8000';

type Tab = 'recovery' | 'risk' | 'growth' | 'finance' | 'audit';

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
    { id: 'recovery', label: '💰 Recovery' },
    { id: 'risk',     label: '🛡️ Risk' },
    { id: 'growth',   label: '📈 Growth' },
    { id: 'finance',  label: '📊 Finance' },
    { id: 'audit',    label: '📋 Audit' },
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
          <button key={t.id} onClick={() => { setTab(t.id as Tab); setResults(null); }}
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
            <p className="text-gray-400 mb-4">Evaluates each payment for fraud signals, enforces stopping rules, blocks high-risk recovery attempts.</p>
            <button onClick={() => run('run-batch')} disabled={loading}
              className="bg-red-600 hover:bg-red-700 disabled:opacity-50 px-6 py-3 rounded-lg font-bold mb-4">
              {loading ? 'Running Agent...' : '▶ Run Risk Agent'}
            </button>
            {results?.results?.map((r: any, i: number) => (
              <div key={i} className="bg-gray-800 rounded-lg p-4 mb-3 border border-gray-700">
                {r.status === 'BLOCKED' ? (
                  <>
                    <p className="text-red-400 text-sm font-bold">🚫 NO-GO — Blocked</p>
                    <p className="text-gray-400 text-xs mt-1">{r.reason}</p>
                  </>
                ) : (
                  <>
                    <p className="text-green-400 text-sm font-bold">✓ GO — Recovery Approved</p>
                    <p className="text-gray-400 text-xs mt-1">Payment ID: {r.result?.payment_id}</p>
                  </>
                )}
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

      </div>
    </main>
  );
}