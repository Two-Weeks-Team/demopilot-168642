"use client";
import { ArrowPathIcon, ExclamationTriangleIcon, InformationCircleIcon } from '@heroicons/react/24/outline';

interface StatePanelProps {
  state: 'loading' | 'empty' | 'error' | 'success';
  message?: string;
}

export default function StatePanel({ state, message }: StatePanelProps) {
  const config = {
    loading: {
      icon: ArrowPathIcon,
      title: 'Loading…',
      color: 'text-primary'
    },
    empty: {
      icon: InformationCircleIcon,
      title: 'Nothing here yet',
      color: 'text-muted'
    },
    error: {
      icon: ExclamationTriangleIcon,
      title: 'Oops! Something went wrong',
      color: 'text-warning'
    },
    success: {
      icon: ArrowPathIcon,
      title: 'Success',
      color: 'text-success'
    }
  }[state];

  const Icon = config.icon;

  return (
    <div className="card flex flex-col items-center justify-center py-12">
      <Icon className={`h-12 w-12 ${config.color} mb-4`} />
      <h3 className={`text-xl font-medium ${config.color}`}>{config.title}</h3>
      {message && <p className="mt-2 text-center text-foreground/70">{message}</p>}
    </div>
  );
}
