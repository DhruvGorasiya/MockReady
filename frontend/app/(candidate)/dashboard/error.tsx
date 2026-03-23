"use client";

export default function DashboardError({
  error,
  reset,
}: {
  error: Error;
  reset: () => void;
}) {
  return (
    <main className="mx-auto max-w-3xl px-4 py-10">
      <div className="rounded-lg border border-red-200 bg-red-50 p-8 text-center">
        <p className="font-medium text-red-700">Something went wrong</p>
        <p className="mt-1 text-sm text-red-500">{error.message}</p>
        <button
          onClick={reset}
          className="mt-4 rounded-md bg-red-600 px-4 py-2 text-sm text-white hover:bg-red-700"
        >
          Try again
        </button>
      </div>
    </main>
  );
}
