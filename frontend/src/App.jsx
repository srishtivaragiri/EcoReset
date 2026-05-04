import { useState } from 'react';

function App() {
  const [step, setStep] = useState('home');

  return (
    <div className="min-h-screen bg-[#050505] text-white font-sans selection:bg-orange-500/30 overflow-hidden relative">

      {/* Background Glows */}
      <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-teal-500/20 blur-[120px] rounded-full pointer-events-none"></div>

      <div className="relative z-10 max-w-6xl mx-auto px-6 py-12 min-h-screen flex flex-col">

        {/* Header */}
        <header className="flex justify-between items-center mb-20">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-teal-600 rounded-xl flex items-center justify-center shadow-[0_0_20px_rgba(234,88,12,0.4)]">
              <span className="font-bold text-white text-xl">E</span>
            </div>
            <h1 className="text-2xl font-bold tracking-tighter">ECO<span className="text-teal-500">RESET</span></h1>
          </div>
        </header>

        {/* Main Action Zone */}
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

            {/* The Dashboard Card */}
            <div className="glass p-2 rounded-2xl shadow-2xl max-w-2xl mx-auto">
              <div className="bg-[#0a0a0a] rounded-xl p-8 border border-white/5 flex flex-col gap-6">
                <div className="text-left">
                  <label className="text-xs font-bold text-gray-500 uppercase tracking-widest mb-2 block">Device or Directory Path</label>
                  <input
                    type="text"
                    placeholder="e.g. C:/Users/Sanvi/Documents"
                    className="w-full bg-black border border-white/10 p-4 rounded-lg outline-none focus:border-orange-600 transition-all text-orange-50"
                  />
                </div>
                <button
                  className="w-full bg-teal-600 hover:bg-teal-500 text-white font-bold py-5 rounded-xl transition-all shadow-[0_0_30px_rgba(234,88,12,0.2)] flex items-center justify-center gap-3 text-lg"
                >
                  INITIALIZE SECURE WIPE <span>↗</span>
                </button>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;