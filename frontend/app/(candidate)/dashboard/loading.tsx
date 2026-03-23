export default function DashboardLoading() {
  return (
    <main className="mx-auto max-w-3xl px-4 py-10">
      <div className="mb-8 h-8 w-48 animate-pulse rounded bg-gray-200" />
      <div className="mb-8 h-48 animate-pulse rounded-lg bg-gray-100" />
      <div className="space-y-3">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-16 animate-pulse rounded-lg bg-gray-100" />
        ))}
      </div>
    </main>
  );
}
