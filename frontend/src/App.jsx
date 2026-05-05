import { useState } from 'react';

function App() {
  const [path, setPath] = useState('');
  const [isWiping, setIsWiping] = useState(false);
  const [progress, setProgress] = useState(0);
  const [statusText, setStatusText] = useState('');
  const [certificate, setCertificate] = useState(null);
  const [ecoImpact, setEcoImpact] = useState(null);
  const [error, setError] = useState('');

  const handleWipe = async () => {
    if (!path.trim()) return alert('Please enter a valid folder path');
    setError('');
    setCertificate(null);
    setEcoImpact(null);
    setIsWiping(true);
    setProgress(0);
    setStatusText('Starting secure wipe...');

    try {
      // Step 1: Start wipe
      const startRes = await fetch('/wipe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path })
      });
      if (!startRes.ok) {
        const err = await startRes.json();
        throw new Error(err.detail || 'Failed to start wipe');
      }
      const { job_id } = await startRes.json();

      // Step 2: Poll status
      await new Promise((resolve, reject) => {
        const interval = setInterval(async () => {
          try {
            const statusRes = await fetch(`/status/${job_id}`);
            const data = await statusRes.json();
            setProgress(data.progress || 0);
            setStatusText(data.status || '');

            if (data.status === 'completed' || data.status === 'completed_with_errors') {
              clearInterval(interval);
              resolve();
            } else if (data.status === 'failed') {
              clearInterval(interval);
              reject(new Error('Wipe failed'));
            }
          } catch (err) {
            clearInterval(interval);
            reject(err);
          }
        }, 500);
      });

      // Step 3: Generate certificate
      setStatusText('Generating certificate...');
      const certRes = await fetch('/generate-cert', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ job_id, device_path: path })
      });
      if (!certRes.ok) {
        const errText = await certRes.text();
        throw new Error('Certificate generation failed: ' + errText.substring(0, 100));
      }
      const certData = await certRes.json();

      setCertificate({
        certId: certData.cert_id,
        signature: certData.signature,
        pdfUrl: certData.pdf_url,
        verificationUrl: certData.verification_url
      });
      setEcoImpact({ co2Saved: '2.1 kg', ewasteDiverted: '450 g' });
      setStatusText('Complete!');
    } catch (err) {
      setError(err.message);
    } finally {
      setIsWiping(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#050505] text-white font-sans overflow-hidden relative">
      <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-teal-500/20 blur-[120px] rounded-full pointer-events-none"></div>
      <div className="relative z-10 max-w-6xl mx-auto px-6 py-12 min-h-screen flex flex-col">
        <header className="flex justify-between items-center mb-20">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-teal-600 rounded-xl flex items-center justify-center shadow-[0_0_20px_rgba(234,88,12,0.4)]">
              <span className="font-bold text-white text-xl">E</span>
            </div>
            <h1 className="text-2xl font-bold tracking-tighter">ECO<span className="text-teal-500">RESET</span></h1>
          </div>
        </header>

        <main className="flex-1 flex flex-col items-center justify-center text-center">
          <div className="w-full max-w-4xl space-y-12">
            <div className="space-y-4">
              <h2 className="text-6xl md:text-7xl font-black leading-tight">
                Secure Data <span className="text-teal-500">Sanitization</span>
              </h2>
              <p className="text-gray-400 text-lg max-w-xl mx-auto">
                Municipal E-Waste management with verifiable forensic wiping.
              </p>
            </div>

            <div className="glass p-2 rounded-2xl shadow-2xl max-w-2xl mx-auto">
              <div className="bg-[#0a0a0a] rounded-xl p-8 border border-white/5 flex flex-col gap-6">
                <div className="text-left">
                  <label className="text-xs font-bold text-gray-500 uppercase tracking-widest mb-2 block">
                    Device or Directory Path
                  </label>
                  <input type="text" value={path} onChange={(e) => setPath(e.target.value)}
                    placeholder="e.g. C:/Users/Sanvi/Documents"
                    className="w-full bg-black border border-white/10 p-4 rounded-lg outline-none focus:border-teal-600 transition-all"
                    disabled={isWiping} />
                </div>

                <button onClick={handleWipe} disabled={isWiping || !path.trim()}
                  className={`w-full py-5 rounded-xl font-bold text-lg transition-all flex items-center justify-center gap-3 ${isWiping || !path.trim() ? 'bg-gray-700 cursor-not-allowed text-gray-400'
                      : 'bg-teal-600 hover:bg-teal-500 text-white shadow-[0_0_30px_rgba(234,88,12,0.2)]'
                    }`}>
                  {isWiping ? 'WIPING...' : 'INITIALIZE SECURE WIPE'} <span>↗</span>
                </button>

                {isWiping && (
                  <div className="text-left">
                    <div className="flex justify-between text-sm text-gray-400 mb-1">
                      <span>{statusText}</span><span>{progress}%</span>
                    </div>
                    <div className="w-full bg-gray-800 rounded-full h-2">
                      <div className="bg-teal-500 h-2 rounded-full transition-all duration-500" style={{ width: `${progress}%` }} />
                    </div>
                  </div>
                )}

                {error && (
                  <div className="p-3 bg-red-900/30 border border-red-700 rounded-lg text-red-300 text-sm text-left">⚠️ {error}</div>
                )}

                {certificate && (
                  <div className="p-4 bg-teal-900/20 border border-teal-700 rounded-lg text-left space-y-2">
                    <h3 className="text-lg font-bold text-teal-400">✅ Verifiable Certificate</h3>
                    <p className="text-sm text-gray-300">Cert ID: <span className="text-teal-200">{certificate.certId}</span></p>
                    <p className="text-sm text-gray-300 break-all">Signature: <span className="text-teal-200">{certificate.signature}</span></p>
                    <a href={`/download/${certificate.certId}`} target="_blank" className="inline-block text-sm text-blue-400 hover:underline" rel="noreferrer">
                      📄 Download Certificate (PDF)
                    </a>
                    {ecoImpact && (
                      <div className="mt-3 p-3 bg-teal-900/30 rounded border border-teal-600">
                        <h4 className="text-sm font-semibold text-teal-300">🌍 Environmental Impact</h4>
                        <p className="text-xs text-teal-200">CO₂ prevented: {ecoImpact.co2Saved}</p>
                        <p className="text-xs text-teal-200">E‑waste reduced: {ecoImpact.ewasteDiverted}</p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;