import SessionDetailClient from "@/components/session/SessionDetailClient";

export default function SessionDetailPage({
  params,
}: {
  params: { id: string };
}) {
  return (
    <main className="mx-auto max-w-3xl px-4 py-10">
      <SessionDetailClient sessionId={params.id} />
    </main>
  );
}
