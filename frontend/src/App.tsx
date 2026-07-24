import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { JobForm } from './components/JobForm';
import { ProgressView } from './components/ProgressView';
import { ResultsView } from './components/ResultsView';
import { Footer } from './components/Footer';
import type { JobResponse, JobDownloadsResponse, QualityOption } from './types/job';
import { createSplitJob, fetchJobStatus, fetchJobDownloads, cancelSplitJob } from './services/api';

const ACTIVE_JOB_KEY = 'splittube_active_job_id';

export const App: React.FC = () => {
  const [currentJob, setCurrentJob] = useState<JobResponse | null>(null);
  const [downloads, setDownloads] = useState<JobDownloadsResponse | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Restore Active Job State from LocalStorage on Page Reload
  useEffect(() => {
    const savedJobId = localStorage.getItem(ACTIVE_JOB_KEY);
    if (!savedJobId) return;

    const restoreJob = async () => {
      try {
        const job = await fetchJobStatus(savedJobId);
        setCurrentJob(job);

        if (job.status === 'completed') {
          const downloadData = await fetchJobDownloads(savedJobId);
          setDownloads(downloadData);
        } else if (job.status === 'failed') {
          localStorage.removeItem(ACTIVE_JOB_KEY);
        }
      } catch (err) {
        console.warn('Could not restore saved job:', err);
        localStorage.removeItem(ACTIVE_JOB_KEY);
      }
    };

    restoreJob();
  }, []);

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
        } else if (updated.status === 'failed') {
          localStorage.removeItem(ACTIVE_JOB_KEY);
        }
      } catch (err: any) {
        console.error('Polling error:', err);
      }
    }, 1500);

    return () => clearInterval(interval);
  }, [currentJob]);

  const handleCreateJob = async (url: string, parts: number, quality: QualityOption, channel?: string) => {
    setIsSubmitting(true);
    setError(null);
    try {
      const job = await createSplitJob(url, parts, quality, channel);
      setCurrentJob(job);
      setDownloads(null);
      localStorage.setItem(ACTIVE_JOB_KEY, job.job_id);
    } catch (err: any) {
      setError(err.message || 'Failed to submit YouTube video for splitting');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCancelJob = async () => {
    if (!currentJob) return;
    try {
      await cancelSplitJob(currentJob.job_id);
    } catch (err) {
      console.warn('Error cancelling job:', err);
    } finally {
      localStorage.removeItem(ACTIVE_JOB_KEY);
      setCurrentJob(null);
      setDownloads(null);
      setError(null);
    }
  };

  const handleReset = () => {
    localStorage.removeItem(ACTIVE_JOB_KEY);
    setCurrentJob(null);
    setDownloads(null);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-gray-100 flex flex-col justify-between selection:bg-rose-500 selection:text-white">
      <div>
        <Header />

        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 sm:pt-12 pb-16">
          {!currentJob && (
            <JobForm onSubmit={handleCreateJob} isLoading={isSubmitting} error={error} />
          )}

          {currentJob && currentJob.status !== 'completed' && (
            <ProgressView job={currentJob} onCancel={handleCancelJob} />
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
