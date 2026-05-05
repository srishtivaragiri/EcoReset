import React, { useEffect, useState } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';

function Verify() {
  const { certId } = useParams();
  const [searchParams] = useSearchParams();
  
  const [status, setStatus] = useState('loading'); // 'loading', 'success', 'error'
  const [data, setData] = useState(null);
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    const verifyCert = async () => {
      try {
        const sig = searchParams.get('sig');
        const ts = searchParams.get('ts');

        if (!sig || !ts) {
          throw new Error('Missing verification parameters (sig, ts)');
        }

        const res = await fetch(`/api/verify/${certId}?sig=${encodeURIComponent(sig)}&ts=${encodeURIComponent(ts)}`);
        
        if (!res.ok) {
          const err = await res.json();
          throw new Error(err.detail || 'Verification failed');
        }

        const result = await res.json();
        setData(result);
        setStatus('success');
      } catch (err) {
        setErrorMsg(err.message);
        setStatus('error');
      }
    };

    verifyCert();
  }, [certId, searchParams]);

  return (
    <div className="min-h-screen bg-[#050505] text-white font-sans selection:bg-teal-500/30 overflow-hidden relative flex flex-col items-center justify-center p-6">
      {/* Background glow */}
      <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-teal-500/20 blur-[120px] rounded-full pointer-events-none"></div>

      <header className="absolute top-6 left-6 flex items-center gap-3">
        <div className="w-10 h-10 bg-teal-600 rounded-xl flex items-center justify-center shadow-[0_0_20px_rgba(20,184,166,0.4)]">
          <span className="font-bold text-white text-xl">E</span>
        </div>
        <h1 className="text-2xl font-bold tracking-tighter">ECO<span className="text-teal-500">RESET</span></h1>
      </header>

      <div className="relative z-10 w-full max-w-2xl">
        <div className="glass p-2 rounded-2xl shadow-2xl">
          <div className="bg-[#0a0a0a] rounded-xl p-8 border border-white/5 flex flex-col gap-6 items-center text-center">
            
            {status === 'loading' && (
              <div className="py-12 space-y-4">
                <div className="w-12 h-12 border-4 border-teal-500/30 border-t-teal-500 rounded-full animate-spin mx-auto"></div>
                <h2 className="text-xl font-bold text-gray-300">Verifying Certificate...</h2>
                <p className="text-sm text-gray-500">Checking blockchain & cryptographic signatures</p>
              </div>
            )}

            {status === 'error' && (
              <div className="py-8 space-y-4 w-full">
                <div className="w-20 h-20 bg-red-900/30 rounded-full flex items-center justify-center mx-auto border border-red-500/50">
                  <span className="text-4xl">❌</span>
                </div>
                <h2 className="text-2xl font-black text-red-400">Verification Failed</h2>
                <p className="text-red-300 bg-red-950/50 p-4 rounded-lg border border-red-900 break-words text-sm">
                  {errorMsg}
                </p>
              </div>
            )}

            {status === 'success' && data && (
              <div className="w-full space-y-8">
                {/* Status Header */}
                <div className="space-y-3">
                  {data.is_verified ? (
                    <div className="w-24 h-24 bg-teal-900/30 rounded-full flex items-center justify-center mx-auto border border-teal-500/50 shadow-[0_0_40px_rgba(20,184,166,0.3)]">
                      <span className="text-5xl">✅</span>
                    </div>
                  ) : (
                    <div className="w-24 h-24 bg-red-900/30 rounded-full flex items-center justify-center mx-auto border border-red-500/50 shadow-[0_0_40px_rgba(239,68,68,0.3)]">
                      <span className="text-5xl">⚠️</span>
                    </div>
                  )}
                  
                  <h2 className={`text-3xl font-black ${data.is_verified ? 'text-teal-400' : 'text-red-400'}`}>
                    {data.is_verified ? 'Authentic Certificate' : 'Tampered / Invalid'}
                  </h2>
                  <p className="text-gray-400">{data.message}</p>
                </div>

                {/* Details Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-left">
                  <div className={`p-5 rounded-xl border ${data.is_tamper_proof ? 'bg-teal-900/10 border-teal-800' : 'bg-red-900/10 border-red-800'}`}>
                    <div className="flex items-center gap-3 mb-2">
                      <span className="text-2xl">🔒</span>
                      <h3 className="font-bold text-gray-200">Tamper-Proof</h3>
                    </div>
                    <p className={`text-sm ${data.is_tamper_proof ? 'text-teal-300' : 'text-red-300'}`}>
                      {data.is_tamper_proof ? 'Cryptographic signature is valid and data is unchanged.' : 'Warning: Signature mismatch or data altered.'}
                    </p>
                  </div>

                  <div className={`p-5 rounded-xl border ${data.ok_for_resale ? 'bg-teal-900/10 border-teal-800' : 'bg-orange-900/10 border-orange-800'}`}>
                    <div className="flex items-center gap-3 mb-2">
                      <span className="text-2xl">♻️</span>
                      <h3 className="font-bold text-gray-200">Resale Status</h3>
                    </div>
                    <p className={`text-sm ${data.ok_for_resale ? 'text-teal-300' : 'text-orange-300'}`}>
                      {data.ok_for_resale ? 'Device securely wiped and ready for safe resale.' : 'Device data wipe status unknown or incomplete.'}
                    </p>
                  </div>
                </div>

                {/* Meta details */}
                <div className="bg-black/50 p-4 rounded-lg border border-white/5 text-left space-y-2 mt-6">
                  <div className="flex justify-between items-center text-xs border-b border-white/5 pb-2">
                    <span className="text-gray-500 uppercase tracking-wider font-bold">Certificate ID</span>
                    <span className="text-gray-300 font-mono">{certId}</span>
                  </div>
                  <div className="flex justify-between items-center text-xs border-b border-white/5 pb-2">
                    <span className="text-gray-500 uppercase tracking-wider font-bold">Device Hash</span>
                    <span className="text-gray-300 font-mono truncate max-w-[200px]" title={data.device_hash}>{data.device_hash || 'N/A'}</span>
                  </div>
                  <div className="flex justify-between items-center text-xs pt-1">
                    <span className="text-gray-500 uppercase tracking-wider font-bold">Issued At</span>
                    <span className="text-gray-300">{data.timestamp && !isNaN(parseFloat(data.timestamp)) ? new Date(parseFloat(data.timestamp) * 1000).toLocaleString() : (data.timestamp || 'N/A')}</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Verify;