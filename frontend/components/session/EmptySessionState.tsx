import Link from "next/link";

export default function EmptySessionState() {
  return (
    <div className="flex flex-col items-center justify-center rounded-lg border border-dashed border-gray-300 bg-white px-8 py-16 text-center">
      <div className="mb-4 text-4xl">🎯</div>
      <h2 className="mb-2 text-lg font-semibold text-gray-800">
        No sessions yet
      </h2>
      <p className="mb-6 max-w-sm text-sm text-gray-500">
        Practice a mock interview to start tracking your progress and get
        dimensional feedback on your answers.
      </p>
      <Link
        href="/sessions/new"
        className="rounded-md bg-indigo-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-indigo-700"
      >
        Start your first session
      </Link>
    </div>
  );
}
