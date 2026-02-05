"use client";

import { useState, ChangeEvent, useEffect } from 'react';
import axios from 'axios';
import { useSession, signOut } from "next-auth/react";
import { useRouter } from "next/navigation";

// --- Types ---
interface LeakDetail {
  type: string;
  value_masked: string;
  line: string | number;
}
interface ScanReport {
  filename: string;
  total_leaks: number;
  risk_score: string;
  details: LeakDetail[];
}
interface HistoryItem {
  filename: string;
  date: string;
  leaks: number;
  risk: string;
}

export default function Home() {
  const { data: session, status } = useSession();
  const router = useRouter();

  // --- Redirect if not logged in ---
  useEffect(() => {
    if (status === "unauthenticated") router.push("/login");
  }, [status, router]);

  // --- State ---
  const [mode, setMode] = useState<'FILE' | 'DB' | 'S3'>('FILE');
  const [file, setFile] = useState<File | null>(null);
  const [dbString, setDbString] = useState<string>("");
  const [awsConfig, setAwsConfig] = useState({ accessKey: '', secretKey: '', bucket: '', region: 'us-east-1' });
  const [report, setReport] = useState<ScanReport | null>(null);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>("");

  // Helpers
  const getBaseUrl = () => process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  
  const fetchHistory = async () => {
    try {
      const res = await axios.get(`${getBaseUrl()}/history/`);
      setHistory(res.data);
    } catch (err) { console.error("History Error"); }
  };
  useEffect(() => { if (session) fetchHistory(); }, [session]);

  const handleScan = async () => {
    setLoading(true); setReport(null); setError("");
    try {
      let res;
      if (mode === 'FILE') {
        if (!file) throw new Error("Select a file.");
        const formData = new FormData(); formData.append("file", file);
        res = await axios.post(`${getBaseUrl()}/scan-file/`, formData);
      } else if (mode === 'DB') {
        if (!dbString) throw new Error("Enter Connection String.");
        res = await axios.post(`${getBaseUrl()}/scan-database/`, { connection_string: dbString });
      } else if (mode === 'S3') {
        if (!awsConfig.accessKey) throw new Error("Enter AWS Config.");
        res = await axios.post(`${getBaseUrl()}/scan-s3/`, { 
          access_key: awsConfig.accessKey, secret_key: awsConfig.secretKey, 
          bucket_name: awsConfig.bucket, region: awsConfig.region 
        });
      }
      setReport(res?.data);
      fetchHistory();
    } catch (err: any) { setError(err.response?.data?.detail || err.message); } 
    finally { setLoading(false); }
  };

  const handleDownloadPDF = async () => {
    if (!report) return;
    const res = await axios.post(`${getBaseUrl()}/generate-pdf/`, { filename: report.filename, findings: report.details }, { responseType: 'blob' });
    const url = window.URL.createObjectURL(new Blob([res.data]));
    const link = document.createElement('a'); link.href = url; link.setAttribute('download', 'Report.pdf'); document.body.appendChild(link); link.click();
  };

  if (status === "loading") return <div className="min-h-screen bg-slate-900 flex items-center justify-center text-white">Loading Security Module...</div>;

  return (
    <div className="min-h-screen bg-slate-50 flex font-sans text-slate-900">
      
      {/* --- SIDEBAR --- */}
      <aside className="w-64 bg-slate-900 text-white flex flex-col hidden md:flex">
        <div className="p-6 border-b border-slate-800">
          <h1 className="text-xl font-bold flex items-center gap-2">
            <span className="text-blue-500">🛡️</span> DPDP Shield
          </h1>
          <p className="text-xs text-slate-500 mt-1">v1.0.0 Enterprise</p>
        </div>
        <nav className="flex-1 p-4 space-y-2">
          <button onClick={() => setMode('FILE')} className={`w-full text-left px-4 py-3 rounded-lg transition-colors ${mode === 'FILE' ? 'bg-blue-600 text-white shadow-lg shadow-blue-900/50' : 'text-slate-400 hover:bg-slate-800'}`}>📂 File Scan</button>
          <button onClick={() => setMode('DB')} className={`w-full text-left px-4 py-3 rounded-lg transition-colors ${mode === 'DB' ? 'bg-blue-600 text-white shadow-lg shadow-blue-900/50' : 'text-slate-400 hover:bg-slate-800'}`}>🔌 Database Scan</button>
          <button onClick={() => setMode('S3')} className={`w-full text-left px-4 py-3 rounded-lg transition-colors ${mode === 'S3' ? 'bg-blue-600 text-white shadow-lg shadow-blue-900/50' : 'text-slate-400 hover:bg-slate-800'}`}>☁️ Cloud S3</button>
        </nav>
        <div className="p-4 border-t border-slate-800">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center">👤</div>
            <div className="text-sm">
              <p className="font-medium">Admin User</p>
              <p className="text-xs text-green-400">● Online</p>
            </div>
          </div>
          <button onClick={() => signOut()} className="w-full py-2 text-xs font-bold text-red-400 border border-red-900/50 rounded hover:bg-red-900/20">Sign Out</button>
        </div>
      </aside>

      {/* --- MAIN CONTENT --- */}
      <main className="flex-1 overflow-y-auto">
        {/* Header (Mobile Only) */}
        <header className="bg-white border-b border-slate-200 p-4 md:hidden flex justify-between items-center">
          <span className="font-bold text-slate-800">DPDP Shield</span>
          <button onClick={() => signOut()} className="text-sm text-red-500">Sign Out</button>
        </header>

        <div className="p-8 max-w-6xl mx-auto">
          
          <div className="mb-8">
            <h2 className="text-3xl font-bold text-slate-800">Security Operations Center</h2>
            <p className="text-slate-500">Select a target vector to initiate a compliance scan.</p>
          </div>

          {/* --- INPUT AREA --- */}
          <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-1">
            <div className="p-8">
              {mode === 'FILE' && (
                <div className="border-2 border-dashed border-slate-300 rounded-xl p-12 text-center hover:bg-slate-50 transition-colors">
                  <input type="file" onChange={(e) => setFile(e.target.files?.[0] || null)} className="block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100" />
                  <p className="mt-4 text-xs text-slate-400">Supports .csv, .sql, .txt files up to 50MB</p>
                </div>
              )}

              {mode === 'DB' && (
                <div>
                  <label className="block text-sm font-bold text-slate-700 mb-2">Database Connection String</label>
                  <input type="text" value={dbString} onChange={(e) => setDbString(e.target.value)} placeholder="e.g. sqlite:///vulnerable.db" className="w-full p-4 bg-slate-50 border border-slate-200 rounded-lg font-mono text-sm focus:ring-2 focus:ring-blue-500 outline-none" />
                </div>
              )}

              {mode === 'S3' && (
                <div className="grid grid-cols-2 gap-4">
                  <div className="col-span-2 md:col-span-1"><label className="text-xs font-bold text-slate-500">AWS Access Key</label><input type="text" onChange={(e) => setAwsConfig({...awsConfig, accessKey: e.target.value})} className="w-full p-3 bg-slate-50 border rounded-lg mt-1" /></div>
                  <div className="col-span-2 md:col-span-1"><label className="text-xs font-bold text-slate-500">AWS Secret Key</label><input type="password" onChange={(e) => setAwsConfig({...awsConfig, secretKey: e.target.value})} className="w-full p-3 bg-slate-50 border rounded-lg mt-1" /></div>
                  <div className="col-span-2 md:col-span-1"><label className="text-xs font-bold text-slate-500">Bucket Name</label><input type="text" onChange={(e) => setAwsConfig({...awsConfig, bucket: e.target.value})} className="w-full p-3 bg-slate-50 border rounded-lg mt-1" /></div>
                  <div className="col-span-2 md:col-span-1"><label className="text-xs font-bold text-slate-500">Region</label><input type="text" defaultValue="us-east-1" onChange={(e) => setAwsConfig({...awsConfig, region: e.target.value})} className="w-full p-3 bg-slate-50 border rounded-lg mt-1" /></div>
                </div>
              )}

              {error && <div className="mt-4 p-3 bg-red-50 text-red-600 rounded-lg text-sm font-medium flex items-center gap-2">❌ {error}</div>}

              <button onClick={handleScan} disabled={loading} className="w-full mt-6 py-4 bg-slate-900 text-white rounded-xl font-bold hover:bg-slate-800 shadow-lg shadow-slate-900/20 transition-all flex items-center justify-center gap-2">
                {loading ? <span className="animate-spin">↻</span> : <span>⚡ Initiate Scan</span>}
              </button>
            </div>
          </div>

          {/* --- REPORT CARD --- */}
          {report && (
            <div className="mt-8 bg-white rounded-2xl shadow-xl border border-slate-200 overflow-hidden animate-fade-in-up">
              <div className="p-6 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
                <div>
                  <h3 className="text-lg font-bold text-slate-800">Scan Results: {report.filename}</h3>
                  <p className="text-xs text-slate-500">Generated automatically by DPDP Engine</p>
                </div>
                <div className={`px-4 py-2 rounded-lg font-bold text-sm ${report.risk_score === 'HIGH' ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`}>
                  {report.risk_score} RISK
                </div>
              </div>
              
              <div className="p-6">
                <div className="flex gap-4 mb-6">
                  <div className="flex-1 bg-blue-50 p-4 rounded-xl border border-blue-100">
                    <p className="text-xs font-bold text-blue-400 uppercase">Total Leaks</p>
                    <p className="text-3xl font-bold text-blue-900">{report.total_leaks}</p>
                  </div>
                  <div className="flex-1 bg-purple-50 p-4 rounded-xl border border-purple-100">
                    <p className="text-xs font-bold text-purple-400 uppercase">Status</p>
                    <p className="text-xl font-bold text-purple-900 mt-1">{report.total_leaks > 0 ? "Non-Compliant" : "Compliant"}</p>
                  </div>
                </div>

                <div className="overflow-hidden rounded-lg border border-slate-200">
                  <table className="w-full text-sm text-left">
                    <thead className="bg-slate-50 text-slate-500 font-medium">
                      <tr><th className="p-3 pl-4">Type</th><th className="p-3">Location</th><th className="p-3">Detected Data</th></tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {report.details.map((item, i) => (
                        <tr key={i} className="hover:bg-slate-50 transition-colors">
                          <td className="p-3 pl-4 font-bold text-red-600">{item.type}</td>
                          <td className="p-3 text-slate-500">{item.line}</td>
                          <td className="p-3 font-mono text-slate-700 bg-slate-50/50">{item.value_masked}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                <button onClick={handleDownloadPDF} className="mt-6 w-full py-3 border-2 border-slate-200 text-slate-700 font-bold rounded-xl hover:bg-slate-50 hover:border-slate-300 transition-all">
                  📄 Download Official Audit Certificate
                </button>
              </div>
            </div>
          )}

          {/* --- HISTORY --- */}
          <div className="mt-12">
            <h3 className="text-lg font-bold text-slate-800 mb-4">Recent Audit Logs</h3>
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
              <table className="w-full text-sm text-left">
                <thead className="bg-slate-50 text-slate-500">
                  <tr><th className="p-4">Target</th><th className="p-4">Timestamp</th><th className="p-4">Findings</th><th className="p-4">Verdict</th></tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {history.map((scan, i) => (
                    <tr key={i} className="hover:bg-slate-50 transition-colors">
                      <td className="p-4 font-medium text-slate-900">{scan.filename}</td>
                      <td className="p-4 text-slate-500">{scan.date}</td>
                      <td className="p-4 font-bold text-slate-700">{scan.leaks} Leaks</td>
                      <td className="p-4"><span className={`px-2 py-1 rounded text-xs font-bold ${scan.risk === 'HIGH' ? 'bg-red-100 text-red-600' : 'bg-green-100 text-green-600'}`}>{scan.risk}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

        </div>
      </main>
    </div>
  );
}