"use client";
import { CheckCircleIcon, XCircleIcon } from '@heroicons/react/24/outline';

interface InsightPanelProps {
  feedback: {
    feedback_id: string;
    clarity: { score: number; suggestions: string[] };
    engagement: { score: number; suggestions: string[] };
    persuasion: { score: number; suggestions: string[] };
  };
}

export default function InsightPanel({ feedback }: InsightPanelProps) {
  const sections = [
    { name: 'Clarity', data: feedback.clarity, icon: CheckCircleIcon },
    { name: 'Engagement', data: feedback.engagement, icon: CheckCircleIcon },
    { name: 'Persuasion', data: feedback.persuasion, icon: CheckCircleIcon }
  ];

  return (
    <div className="card space-y-4">
      <h2 className="text-2xl font-semibold text-primary">AI Feedback</h2>
      {sections.map((sec) => (
        <div key={sec.name} className="space-y-2">
          <div className="flex items-center gap-2">
            <sec.icon className="h-5 w-5 text-success" />
            <h3 className="font-medium text-lg">{sec.name} (Score: {sec.data.score}/10)</h3>
          </div>
          <ul className="list-disc list-inside text-sm text-foreground/80 ml-4">
            {sec.data.suggestions.map((s, i) => (
              <li key={i}>{s}</li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}
