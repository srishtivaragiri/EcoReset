import { useState, useEffect } from 'react';

export default function BatchProgress({ jobIds, originalPaths, onComplete }) {
    const [jobs, setJobs] = useState({});
    const [batchCert, setBatchCert] = useState(null);
    const [generating, setGenerating] = useState(false);
    const [completed, setCompleted] = useState(false);

    useEffect(() => {
        if (!jobIds.length || completed) return;

        const interval = setInterval(async () => {
            const updates = {};
            let allDone = true;
            for (const id of jobIds) {
                try {
                    const res = await fetch(`http://localhost:8000/status/${id}`);
                    const data = await res.json();
                    updates[id] = data;
                    if (data.status !== 'completed') allDone = false;
                } catch (err) { }
            }
            setJobs(prev => ({ ...prev, ...updates }));
            if (allDone && !batchCert && !generating && !completed) {
                clearInterval(interval);
                await generateBatchCertificate();
            }
        }, 1000);
        return () => clearInterval(interval);
    }, [jobIds]);

    const generateBatchCertificate = async () => {
        setGenerating(true);
        try {
            // ✅ IMPORTANT: Use the originalPaths prop (the user‑typed paths)
            const devicePaths = originalPaths || [];
            console.log('📤 Sending to /generate-batch-cert:', { job_ids: jobIds, device_paths: devicePaths });

            const response = await fetch('http://localhost:8000/generate-batch-cert', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    job_ids: jobIds,
                    device_paths: devicePaths
                })
            });

            if (response.ok) {
                const certData = await response.json();
                setBatchCert(certData);
                window.open(`http://localhost:8000/download/${certData.cert_id}`, '_blank');
                setCompleted(true);
                if (onComplete) onComplete();
            } else {
                console.error('Batch certificate generation failed');
            }
        } catch (err) {
            console.error('Error:', err);
        } finally {
            setGenerating(false);
        }
    };

    return (
        <div className="mt-6 space-y-3">
            <h3 className="font-bold text-teal-300">Batch Progress ({jobIds.length} devices)</h3>
            {jobIds.map((id, idx) => {
                const job = jobs[id];
                if (!job) return <div key={id}>Loading...</div>;
                const displayPath = (originalPaths && originalPaths[idx]) || id.slice(0, 8);
                return (
                    <div key={id} className="bg-black/40 p-3 rounded-lg border border-white/10">
                        <div className="flex justify-between text-sm">
                            <span className="font-mono">{displayPath}</span>
                            <span>{job.progress || 0}%</span>
                        </div>
                        <div className="w-full bg-gray-800 rounded-full h-1.5 mt-1">
                            <div className="bg-teal-500 h-1.5 rounded-full" style={{ width: `${job.progress || 0}%` }} />
                        </div>
                        <div className="flex justify-between text-xs text-gray-400 mt-2">
                            <span>📄 Files: {job.files_deleted || 0}</span>
                            <span>📁 Folders: {job.folders_deleted || 0}</span>
                        </div>
                        <div className="text-xs text-gray-500">{job.status}</div>
                    </div>
                );
            })}
            {generating && <div className="text-teal-300 text-sm mt-2">Generating combined certificate...</div>}
            {batchCert && (
                <div className="bg-teal-900/30 p-3 rounded-lg mt-2">
                    ✅ Combined certificate ready: <strong>{batchCert.cert_id}</strong>
                    <a href={`http://localhost:8000/download/${batchCert.cert_id}`} target="_blank" className="ml-2 underline text-teal-300">
                        Download PDF (includes all wiped devices)
                    </a>
                </div>
            )}
        </div>
    );
}