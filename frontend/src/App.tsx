import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { JobForm } from './components/JobForm';
import { ProgressView } from './components/ProgressView';
import { ResultsView } from './components/ResultsView';
import { Footer } from './components/Footer';
import type { JobResponse, JobDownloadsResponse, QualityOption } from './types/job';
import { createSplitJob, fetchJobStatus, fetchJobDownloads } from './services/api';

export const App: React.FC = () => {
  const [currentJob, setCurrentJob] = useState<JobResponse | null>(null);
  const [downloads, setDownloads] = useState<JobDownloadsResponse | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Status Polling Loop
  useEffect(() => {
    if (!currentJob) return;
    if (currentJob.status === 'completed' || currentJob.status === 'failed') return;

    const interval = setInterval(async () => {
      try {
        const updated = await fetchJobStatus(currentJob.job_id);
        setCurrentJob(updated);

        if (updated.status === 'completed') {
          const downloadData = await fetchJobDownloads(updated.job_id);
          setDownloads(downloadData);
        }
      } catch (err: any) {
        console.error('Polling error:', err);
      }
    }, 1500);

    return () => clearInterval(interval);
  }, [currentJob]);

  const handleCreateJob = async (url: string, parts: number, quality: QualityOption) => {
    setIsSubmitting(true);
    setError(null);
    try {
      const job = await createSplitJob(url, parts, quality);
      setCurrentJob(job);
      setDownloads(null);
    } catch (err: any) {
      setError(err.message || 'Failed to submit YouTube video for splitting');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReset = () => {
    setCurrentJob(null);
    setDownloads(null);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-gray-100 flex flex-col justify-between selection:bg-rose-500 selection:text-white">
      <div>
        <Header />

        <main className="max-w-6xl mx-auto px-4 sm:px-6 pt-10 pb-16">
          {!currentJob && (
            <JobForm onSubmit={handleCreateJob} isLoading={isSubmitting} error={error} />
          )}

          {currentJob && currentJob.status !== 'completed' && (
            <ProgressView job={currentJob} />
          )}

          {currentJob && currentJob.status === 'completed' && downloads && (
            <ResultsView downloads={downloads} onReset={handleReset} />
          )}
        </main>
      </div>

      <Footer />
    </div>
  );
};

export default App;
