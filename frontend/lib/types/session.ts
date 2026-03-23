// Mirrors backend Pydantic schemas in backend/app/schemas/session.py

export type InterviewType = "behavioral" | "technical" | "system_design";
export type InterviewRole = "SWE" | "PM" | "DS";
export type SessionStatus =
  | "created"
  | "in_progress"
  | "completed"
  | "reviewed"
  | "abandoned";

export interface DimensionScores {
  clarity: number;
  depth: number;
  structure: number;
  relevance: number;
  communication_quality: number;
}

export interface QuestionResult {
  id: string;
  question_text: string;
  candidate_answer: string | null;
  order_index: number;
  ai_scores: DimensionScores | null;
  coach_scores: DimensionScores | null;
  feedback: Record<string, string> | null;
}

export interface SessionSummary {
  id: string;
  interview_type: InterviewType;
  role: InterviewRole;
  status: SessionStatus;
  /** Authoritative composite: coach score when present, else AI score */
  composite_score: number | null;
  created_at: string;
}

export interface SessionDetail extends SessionSummary {
  questions: QuestionResult[];
}

export interface SessionHistoryResponse {
  sessions: SessionSummary[];
  total: number;
}

export interface TrendPoint {
  session_id: string;
  created_at: string;
  composite_score: number;
  dimension_scores: DimensionScores;
}

export interface TrendResponse {
  points: TrendPoint[];
}

// --- Session creation ---

export interface QuestionInSession {
  id: string;
  question_text: string;
  order_index: number;
}

export interface CreateSessionRequest {
  interview_type: InterviewType;
  role: InterviewRole;
  question_count?: number;
}

export interface SessionCreatedResponse {
  id: string;
  interview_type: InterviewType;
  role: InterviewRole;
  status: SessionStatus;
  questions: QuestionInSession[];
}

// --- Answer submission ---

export interface SubmitAnswerRequest {
  answer: string;
}

export interface DimensionFeedback {
  clarity: string;
  depth: string;
  structure: string;
  relevance: string;
  communication_quality: string;
}

export interface AnswerFeedbackResponse {
  session_question_id: string;
  ai_scores: DimensionScores;
  composite_score: number;
  feedback_summary: string;
  dimension_feedback: DimensionFeedback;
  improvement_suggestion: string;
  is_session_complete: boolean;
}
