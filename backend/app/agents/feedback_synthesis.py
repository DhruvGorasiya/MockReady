import json
import logging
import time

from anthropic import AsyncAnthropic

from app.agents.logging_utils import log_agent_invocation
from app.core.config import settings

logger = logging.getLogger(__name__)

_client: AsyncAnthropic | None = None


def _get_client() -> AsyncAnthropic:
    global _client
    if _client is None:
        _client = AsyncAnthropic(api_key=settings.anthropic_api_key)
    return _client


async def synthesize_feedback(
    question: str,
    answer: str,
    scores: dict,
    reasoning: dict,
    interview_type: str,
    role: str,
) -> dict:
    """Generate behavioral, actionable feedback based on scores and reasoning."""
    prompt = f"""You are an expert interview coach giving specific, behavioral feedback.

Interview Type: {interview_type}
Role: {role}
Question: {question}
Candidate's Answer: {answer}
Dimension Scores: {json.dumps(scores)}
Scoring Reasoning: {json.dumps(reasoning)}

Write feedback that:
- References specific things the candidate said or failed to say
- Is behavioral and actionable, not generic
- Never uses phrases like "good job" or "needs improvement" without specifics

Return ONLY this JSON object, no markdown:
{{
  "feedback_summary": "<2-3 sentence overall summary referencing the answer>",
  "dimension_feedback": {{
    "clarity": "<1-3 sentences of specific behavioral feedback>",
    "depth": "<1-3 sentences of specific behavioral feedback>",
    "structure": "<1-3 sentences of specific behavioral feedback>",
    "relevance": "<1-3 sentences of specific behavioral feedback>",
    "communication_quality": "<1-3 sentences of specific behavioral feedback>"
  }},
  "improvement_suggestion": "<one specific, actionable sentence the candidate can apply immediately>"
}}"""

    input_payload = {
        "interview_type": interview_type,
        "role": role,
        "question": question,
        "answer_length": len(answer),
        "scores": scores,
    }

    start = time.monotonic()
    try:
        message = await _get_client().messages.create(
            model=settings.claude_model,
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}],
        )
        latency_ms = (time.monotonic() - start) * 1000

        raw = message.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        result = json.loads(raw.strip())

        log_agent_invocation(
            logger=logger,
            agent_name="feedback_synthesis",
            model=settings.claude_model,
            input_payload=input_payload,
            output_payload=result,
            latency_ms=latency_ms,
            status="success",
        )
        return result
    except Exception as exc:
        latency_ms = (time.monotonic() - start) * 1000
        log_agent_invocation(
            logger=logger,
            agent_name="feedback_synthesis",
            model=settings.claude_model,
            input_payload=input_payload,
            output_payload=None,
            latency_ms=latency_ms,
            status="error",
            error=str(exc),
        )
        raise
