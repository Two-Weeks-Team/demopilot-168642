async function throwApiError(res: Response, fallback: string): Promise<never> {
  const raw = await res.text();
  const parsed = raw ? safeParseJson(raw) : null;
  const message = parsed?.error?.message ?? parsed?.detail ?? parsed?.message ?? raw ?? fallback;
  throw new Error(message || fallback);
}

function safeParseJson(raw: string): any {
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export interface DemoDTO {
  demo_id: string;
  title: string;
  description: string;
}

export interface FeedbackDTO {
  feedback_id: string;
  clarity: { score: number; suggestions: string[] };
  engagement: { score: number; suggestions: string[] };
  persuasion: { score: number; suggestions: string[] };
}

const API_BASE = '/api';

export async function fetchDemos(): Promise<DemoDTO[]> {
  const res = await fetch(`${API_BASE}/demos`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include'
  });
  if (!res.ok) throw new Error('Network response was not ok');
  const data = await res.json();
  return data as DemoDTO[];
}

export async function fetchFeedback(payload: { rehearsal_id: string }): Promise<FeedbackDTO> {
  const res = await fetch(`${API_BASE}/feedback`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify(payload)
  });
  if (!res.ok) {
    await throwApiError(res, "Failed to fetch feedback");
  }
  const data = await res.json();
  return data as FeedbackDTO;
}
