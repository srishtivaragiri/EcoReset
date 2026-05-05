import { useState } from 'react';

export default function BatchWipe({ onBatchStart }) {
    const [paths, setPaths] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        const pathList = paths.split('\n').filter(p => p.trim().length > 0);
        if (pathList.length === 0) {
            setError('Enter at least one path');
            return;
        }
        setLoading(true);
        setError('');
        try {
            const res = await fetch('http://localhost:8000/wipe-batch', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ paths: pathList })
            });
            if (!res.ok) throw new Error('Batch start failed');
            const data = await res.json();
            // ✅ Pass both job_ids AND the original paths
            onBatchStart(data.job_ids, pathList);
            setPaths('');
        } catch (err) {
            setError('Failed to start batch wipe');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="bg-[#0a0a0a] p-6 rounded-xl border border-white/10 mt-8">
            <h3 className="text-lg font-bold mb-2">📦 Batch Wipe (Multiple Devices/Folders)</h3>
            <p className="text-sm text-gray-400 mb-3">Enter one path per line (supports relative paths like ./test1)</p>
            <form onSubmit={handleSubmit}>
                <textarea
                    rows={4}
                    className="w-full bg-black border border-white/10 rounded-lg p-3 text-sm font-mono text-white"
                    placeholder="D:/USB_Drive\nE:/Backup\n./test_folder_1\n./test_folder_2"
                    value={paths}
                    onChange={(e) => setPaths(e.target.value)}
                />
                {error && <div className="text-red-400 text-sm mt-2">{error}</div>}
                <button
                    type="submit"
                    disabled={loading}
                    className="mt-3 w-full bg-teal-700 hover:bg-teal-600 py-2 rounded-lg font-semibold disabled:opacity-50"
                >
                    {loading ? 'Starting...' : 'Start Batch Wipe'}
                </button>
            </form>
        </div>
    );
}