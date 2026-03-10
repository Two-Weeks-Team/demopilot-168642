"use client";
import { ChartBarIcon } from '@heroicons/react/24/outline';

export default function StatsStrip() {
  // Placeholder static metrics; in real app they'd come from an API.
  const metrics = [
    { label: 'Clarity', value: '8.2', color: 'bg-success' },
    { label: 'Engagement', value: '7.5', color: 'bg-primary' },
    { label: 'Persuasion', value: '8.0', color: 'bg-accent' }
  ];

  return (
    <div className="flex gap-4 overflow-x-auto pb-2">
      {metrics.map((m) => (
        <div
          key={m.label}
          className={`flex items-center gap-2 px-4 py-2 rounded-md ${m.color} text-white shadow`}
        >
          <ChartBarIcon className="h-5 w-5" />
          <span className="font-medium">{m.label}: {m.value}/10</span>
        </div>
      ))}
    </div>
  );
}
