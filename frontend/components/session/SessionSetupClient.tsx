"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { createSession } from "@/lib/api/sessions";
import type { InterviewType, InterviewRole } from "@/lib/types/session";

const INTERVIEW_TYPES: { value: InterviewType; label: string }[] = [
  { value: "behavioral", label: "Behavioral" },
  { value: "technical", label: "Technical" },
  { value: "system_design", label: "System Design" },
];

const ROLES: { value: InterviewRole; label: string }[] = [
  { value: "SWE", label: "Software Engineer" },
  { value: "PM", label: "Product Manager" },
  { value: "DS", label: "Data Scientist" },
];

export default function SessionSetupClient() {
  const router = useRouter();
  const [interviewType, setInterviewType] = useState<InterviewType | "">("");
  const [role, setRole] = useState<InterviewRole | "">("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const canStart = interviewType !== "" && role !== "";

  async function handleStart() {
    if (!canStart) return;
    setLoading(true);
    setError(null);
    try {
      const token = process.env.NEXT_PUBLIC_API_TOKEN ?? "";
      const session = await createSession(
        { interview_type: interviewType, role: role as InterviewRole, question_count: 3 },
        token,
      );
      router.push(`/sessions/${session.id}/interview`);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to start session");
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-lg px-4 py-16">
      <h1 className="text-2xl font-bold text-gray-900 mb-2">Start a Practice Session</h1>
      <p className="text-gray-500 mb-10 text-sm">
        Choose your interview type and target role to get relevant questions.
      </p>

      {/* Interview Type */}
      <div className="mb-8">
        <p className="text-sm font-semibold text-gray-700 mb-3">Interview Type</p>
        <div className="grid grid-cols-3 gap-3">
          {INTERVIEW_TYPES.map((t) => (
            <button
              key={t.value}
              onClick={() => setInterviewType(t.value)}
              className={`rounded-lg border px-4 py-3 text-sm font-medium transition-colors ${
                interviewType === t.value
                  ? "border-indigo-600 bg-indigo-50 text-indigo-700"
                  : "border-gray-200 bg-white text-gray-700 hover:border-indigo-300"
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>
      </div>

      {/* Role */}
      <div className="mb-10">
        <p className="text-sm font-semibold text-gray-700 mb-3">Target Role</p>
        <div className="grid grid-cols-3 gap-3">
          {ROLES.map((r) => (
            <button
              key={r.value}
              onClick={() => setRole(r.value)}
              className={`rounded-lg border px-4 py-3 text-sm font-medium transition-colors ${
                role === r.value
                  ? "border-indigo-600 bg-indigo-50 text-indigo-700"
                  : "border-gray-200 bg-white text-gray-700 hover:border-indigo-300"
              }`}
            >
              {r.label}
            </button>
          ))}
        </div>
      </div>

      {error && (
        <p className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
          {error}
        </p>
      )}

      <button
        onClick={handleStart}
        disabled={!canStart || loading}
        className="w-full rounded-lg bg-indigo-600 px-6 py-3 text-sm font-semibold text-white disabled:opacity-40 hover:bg-indigo-700 transition-colors"
      >
        {loading ? "Generating questions…" : "Start Session"}
      </button>
    </div>
  );
}
