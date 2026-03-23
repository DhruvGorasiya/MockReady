import type { SessionSummary } from "@/lib/types/session";

interface Props {
  session: SessionSummary;
}

const INTERVIEW_TYPE_LABEL: Record<string, string> = {
  behavioral: "Behavioral",
  technical: "Technical",
  system_design: "System Design",
};

const STATUS_STYLES: Record<string, string> = {
  completed: "bg-green-100 text-green-800",
  reviewed: "bg-blue-100 text-blue-800",
  in_progress: "bg-yellow-100 text-yellow-800",
  created: "bg-gray-100 text-gray-600",
  abandoned: "bg-red-100 text-red-700",
};

export default function SessionCard({ session }: Props) {
  const date = new Date(session.created_at).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });

  const statusStyle = STATUS_STYLES[session.status] ?? "bg-gray-100 text-gray-600";
  const typeLabel = INTERVIEW_TYPE_LABEL[session.interview_type] ?? session.interview_type;

  return (
    <div className="flex items-center justify-between rounded-lg border border-gray-200 bg-white px-5 py-4 shadow-sm">
      <div className="flex flex-col gap-1">
        <div className="flex items-center gap-2">
          <span className="font-medium text-gray-900">{typeLabel}</span>
          <span className="text-gray-400">·</span>
          <span className="text-gray-700">{session.role}</span>
        </div>
        <span className="text-sm text-gray-500">{date}</span>
      </div>

      <div className="flex items-center gap-3">
        <span
          className={`rounded-full px-2.5 py-0.5 text-xs font-medium capitalize ${statusStyle}`}
        >
          {session.status}
        </span>
        <span className="w-14 text-right text-lg font-semibold text-gray-900">
          {session.composite_score !== null ? session.composite_score : (
            <span className="text-sm font-normal text-gray-400">Pending</span>
          )}
        </span>
      </div>
    </div>
  );
}
