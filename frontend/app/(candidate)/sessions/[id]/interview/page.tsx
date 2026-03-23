import InterviewSessionClient from "@/components/session/InterviewSessionClient";

export default function InterviewSessionPage({
  params,
}: {
  params: { id: string };
}) {
  return (
    <main className="mx-auto max-w-2xl px-4 py-10">
      <InterviewSessionClient sessionId={params.id} />
    </main>
  );
}
