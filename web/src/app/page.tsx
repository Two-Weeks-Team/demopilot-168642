"use client";
import { useState } from "react";
import Hero from '@/components/Hero';
import DemoBeats from '@/components/DemoBeats';
import Rehearsal from '@/components/Rehearsal';
import InsightPanel from '@/components/InsightPanel';
import StatePanel from '@/components/StatePanel';
import CollectionPanel from '@/components/CollectionPanel';
import StatsStrip from '@/components/StatsStrip';
import { fetchFeedback } from '@/lib/api';

interface Demo {
  demo_id: string;
  title: string;
  description: string;
}

interface Feedback {
  feedback_id: string;
  clarity: { score: number; suggestions: string[] };
  engagement: { score: number; suggestions: string[] };
  persuasion: { score: number; suggestions: string[] };
}

export default function HomePage() {
  const [feedback, setFeedback] = useState<Feedback | null>(null);
  const [loadingFeedback, setLoadingFeedback] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const demos: Demo[] = [];

  const startRehearsal = async () => {
    // In a real app we would capture a recording and upload it first.
    // For the demo we simulate by creating a dummy rehearsal_id.
    const dummyRehearsalId = crypto.randomUUID();
    setLoadingFeedback(true);
    setError(null);
    try {
      const fb = await fetchFeedback({ rehearsal_id: dummyRehearsalId });
      setFeedback(fb);
    } catch (e) {
      setError('AI feedback generation failed');
    } finally {
      setLoadingFeedback(false);
    }
  };

  return (
    <main className="flex-1 container mx-auto p-4 space-y-8">
      <Hero />
      <DemoBeats />
      <StatsStrip />
      <section id="demo-section" className="flex flex-col md:flex-row gap-6">
        <Rehearsal onStart={startRehearsal} loading={loadingFeedback} />
        <div className="flex-1">
          {loadingFeedback && <StatePanel state="loading" />}
          {error && <StatePanel state="error" message={error} />}
          {feedback && <InsightPanel feedback={feedback} />}
          {!loadingFeedback && !feedback && !error && (
            <StatePanel state="empty" message="Run a rehearsal to see AI feedback here." />
          )}
        </div>
      </section>
      <CollectionPanel demos={demos} />
    </main>
  );
}
