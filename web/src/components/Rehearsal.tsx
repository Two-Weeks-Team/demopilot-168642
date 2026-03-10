"use client";
import { useState } from "react";
import { MicrophoneIcon, CloudUploadIcon } from '@heroicons/react/24/solid';
import clsx from 'clsx';

interface RehearsalProps {
  onStart: () => Promise<void>;
  loading: boolean;
}

export default function Rehearsal({ onStart, loading }: RehearsalProps) {
  const [recorded, setRecorded] = useState(false);

  const handleClick = async () => {
    setRecorded(true);
    await onStart();
    setRecorded(false);
  };

  return (
    <div className={clsx('card w-full md:w-80', { 'opacity-50 pointer-events-none': loading })}>
      <h2 className="text-xl font-semibold mb-4 text-primary">Rehearsal Mode</h2>
      <button
        onClick={handleClick}
        disabled={loading}
        className="w-full flex items-center justify-center gap-2 bg-primary text-white py-2 rounded-md hover:bg-primary/90 transition"
      >
        {loading ? (
          <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"></path>
          </svg>
        ) : (
          <MicrophoneIcon className="h-5 w-5" />
        )}
        {loading ? 'Processing…' : recorded ? 'Uploading…' : 'Start Rehearsal'}
      </button>
      <p className="mt-2 text-sm text-foreground/60">Your AI feedback will appear on the right.</p>
    </div>
  );
}
