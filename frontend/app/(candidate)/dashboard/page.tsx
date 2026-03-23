import DashboardClient from "@/components/session/DashboardClient";

export const metadata = { title: "Dashboard — MockReady" };

export default function DashboardPage() {
  return (
    <main className="mx-auto max-w-3xl px-4 py-10">
      <h1 className="mb-8 text-2xl font-bold text-gray-900">
        Session History
      </h1>
      <DashboardClient />
    </main>
  );
}
