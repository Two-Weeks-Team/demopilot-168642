"use client";
import { CheckBadgeIcon } from '@heroicons/react/24/outline';

const beats = [
  { title: 'Problem', description: 'Clearly articulate the pain you solve.' },
  { title: 'Solution', description: 'Show the core product and its value.' },
  { title: 'Ask', description: 'State what you need from investors.' }
];

export default function DemoBeats() {
  return (
    <section className="card space-y-4">
      <h2 className="text-2xl font-semibold text-primary">Your 3‑Beat Pitch Framework</h2>
      <div className="grid md:grid-cols-3 gap-4">
        {beats.map((beat) => (
          <div key={beat.title} className="flex flex-col items-start p-4 bg-muted rounded-lg">
            <CheckBadgeIcon className="h-6 w-6 text-primary mb-2" />
            <h3 className="font-medium text-lg mb-1">{beat.title}</h3>
            <p className="text-sm text-foreground/80">{beat.description}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
