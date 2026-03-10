"use client";
import { DocumentIcon } from '@heroicons/react/24/outline';
import clsx from 'clsx';

interface Demo {
  demo_id: string;
  title: string;
  description: string;
}

interface CollectionPanelProps {
  demos: Demo[];
}

export default function CollectionPanel({ demos }: CollectionPanelProps) {
  if (demos.length === 0) {
    return (
      <section className="card">
        <h2 className="text-2xl font-semibold text-primary mb-2">Your Saved Pitches</h2>
        <p className="text-foreground/60">You haven’t saved any demos yet. After a rehearsal, you’ll see them here.</p>
      </section>
    );
  }

  return (
    <section className="card">
      <h2 className="text-2xl font-semibold text-primary mb-4">Your Saved Pitches</h2>
      <ul className="space-y-3">
        {demos.map((demo) => (
          <li key={demo.demo_id} className="flex items-start gap-3">
            <DocumentIcon className="h-6 w-6 text-primary mt-1" />
            <div>
              <h3 className="font-medium text-lg">{demo.title}</h3>
              <p className="text-sm text-foreground/70">{demo.description}</p>
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}
