export type Health = {
  status: string;
  components?: Record<string, { status: string }>;
};

export async function fetchHealth(): Promise<Health> {
  // A short timeout keeps the screen responsive while the database is down.
  const response = await fetch("/api/health", { signal: AbortSignal.timeout(5000) });
  // 503 is a valid answer here: the API replied, reporting something inside it is down.
  if (response.status !== 200 && response.status !== 503) {
    throw new Error(`response ${response.status}`);
  }
  return (await response.json()) as Health;
}
