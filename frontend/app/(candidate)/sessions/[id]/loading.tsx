export default function SessionDetailLoading() {
  return (
    <main className="mx-auto max-w-3xl px-4 py-10">
      <div className="space-y-4">
        <div className="h-6 w-40 animate-pulse rounded bg-gray-200" />
        <div className="h-24 animate-pulse rounded-lg bg-gray-100" />
        <div className="h-32 animate-pulse rounded-lg bg-gray-100" />
        <div className="h-48 animate-pulse rounded-lg bg-gray-100" />
      </div>
    </main>
  );
}
