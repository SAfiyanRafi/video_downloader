import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { JobForm } from './components/JobForm';
import { ProgressView } from './components/ProgressView';
import { ResultsView } from './components/ResultsView';
import { Footer } from './components/Footer';
import { HistoryDrawer } from './components/HistoryDrawer';
import { StudioDashboard } from './components/studio/StudioDashboard';
import type { HistoryItem } from './components/HistoryDrawer';
import type {
  JobResponse, JobDownloadsResponse, QualityOption, AspectRatioOption,
  ExportPreset, PaddingMode, NamingTemplate
} from './types/job';
import { createSplitJob, fetchJobStatus, fetchJobDownloads, cancelSplitJob } from './services/api';

const ACTIVE_JOB_KEY = 'splittube_active_job_id';
const HISTORY_KEY = 'splittube_job_history';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'splitter' | 'studio'>('splitter');
  const [currentJob, setCurrentJob] = useState<JobResponse | null>(null);
  const [downloads, setDownloads] = useState<JobDownloadsResponse | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // History Drawer State
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);
  const [history, setHistory] = useState<HistoryItem[]>([]);

  // Load Saved History on Startup
  useEffect(() => {
    try {
      const raw = localStorage.getItem(HISTORY_KEY);
      if (raw) {
        setHistory(JSON.parse(raw));
      }
    } catch (e) {
      console.warn('Could not parse saved history:', e);
    }
  }, []);

  const saveToHistory = (job: JobResponse) => {
    setHistory((prev) => {
      const filtered = prev.filter((item) => item.job.job_id !== job.job_id);
      const updated = [{ job, timestamp: new Date().toISOString() }, ...filtered].slice(0, 20);
      try {
        localStorage.setItem(HISTORY_KEY, JSON.stringify(updated));
      } catch (e) {
        console.warn('Could not save history:', e);
      }
      return updated;
    });
  };

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
          saveToHistory(job);
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
          saveToHistory(updated);
        } else if (updated.status === 'failed') {
          localStorage.removeItem(ACTIVE_JOB_KEY);
        }
      } catch (err: any) {
        console.error('Polling error:', err);
      }
    }, 1500);

    return () => clearInterval(interval);
  }, [currentJob]);

  const handleCreateJob = async (
    url: string,
    parts: number,
    quality: QualityOption,
    aspectRatio: AspectRatioOption,
    exportPreset: ExportPreset,
    paddingMode: PaddingMode,
    namingTemplate: NamingTemplate,
    cropFill: boolean,
    channel?: string
  ) => {
    setIsSubmitting(true);
    setError(null);
    try {
      const job = await createSplitJob(
        url, parts, quality, aspectRatio,
        exportPreset, paddingMode, namingTemplate, cropFill, channel
      );
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
        <Header
          onOpenHistory={() => setIsHistoryOpen(true)}
          activeTab={activeTab}
          onTabChange={(tab) => setActiveTab(tab)}
        />

        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 sm:pt-12 pb-16">
          {activeTab === 'studio' ? (
            <StudioDashboard />
          ) : (
            <>
              {!currentJob && (
                <JobForm onSubmit={handleCreateJob} isLoading={isSubmitting} error={error} />
              )}

              {currentJob && currentJob.status !== 'completed' && (
                <ProgressView job={currentJob} onCancel={handleCancelJob} />
              )}

              {currentJob && currentJob.status === 'completed' && downloads && (
                <ResultsView downloads={downloads} onReset={handleReset} />
              )}
            </>
          )}
        </main>
      </div>

      <HistoryDrawer
        isOpen={isHistoryOpen}
        onClose={() => setIsHistoryOpen(false)}
        history={history}
        onSelectJob={(j) => {
          setCurrentJob(j);
          fetchJobDownloads(j.job_id).then((d) => setDownloads(d)).catch(() => {});
        }}
        onClearHistory={() => {
          setHistory([]);
          localStorage.removeItem(HISTORY_KEY);
        }}
      />

      <Footer />
    </div>
  );
};

export default App;
