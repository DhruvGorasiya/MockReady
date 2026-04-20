import Link from "next/link";
import DashboardClient from "@/components/session/DashboardClient";

export const metadata = { title: "Dashboard — MockReady" };

export default function DashboardPage() {
  return (
    <main className="mx-auto max-w-3xl px-4 py-10">
      <div className="mb-8 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Session History</h1>
        <Link
          href="/sessions/new"
          className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 transition-colors"
        >
          + New Session
        </Link>
      </div>
      <DashboardClient />
    </main>
  );
}
