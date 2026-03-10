"use client";
import { Inter } from 'next/font/google';
import { ArrowRightIcon } from '@heroicons/react/24/solid';
import { useRouter } from 'next/navigation';

const inter = Inter({ subsets: ['latin'], weight: ['400', '600', '700'] });

export default function Hero() {
  const router = useRouter();

  const goToDemo = () => {
    // In a full app we'd navigate; for demo we just scroll.
    const el = document.getElementById('demo-section');
    el?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <section className={`${inter.className} py-16 text-center bg-primary/5`}>
      <h1 className="text-4xl md:text-5xl font-bold text-primary mb-4">
        DemoPilot
      </h1>
      <p className="text-lg text-foreground/80 mb-6 max-w-2xl mx-auto">
        Transform your pitch with AI‑driven rehearsal and feedback, ensuring confidence and success in high‑stakes presentations.
      </p>
      <button
        onClick={goToDemo}
        className="inline-flex items-center gap-2 bg-primary text-white px-6 py-3 rounded-md hover:bg-primary/90 transition"
      >
        <span>Start Your First Rehearsal</span>
        <ArrowRightIcon className="h-5 w-5" />
      </button>
    </section>
  );
}
