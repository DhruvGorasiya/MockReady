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


async def evaluate_answer(
    question: str,
    answer: str,
    interview_type: str,
    role: str,
) -> dict:
    """Score the candidate's answer on 5 dimensions (1-10) with per-dimension reasoning."""
    prompt = f"""You are an expert interviewer evaluating a candidate's response.

Interview Type: {interview_type}
Role: {role}
Question: {question}
Candidate's Answer: {answer}

Score each dimension 1-10 (integer). Reasoning must reference specific content from the answer.

Return ONLY this JSON object, no markdown:
{{
  "clarity": <int>,
  "depth": <int>,
  "structure": <int>,
  "relevance": <int>,
  "communication_quality": <int>,
  "reasoning": {{
    "clarity": "<1 sentence referencing the answer>",
    "depth": "<1 sentence referencing the answer>",
    "structure": "<1 sentence referencing the answer>",
    "relevance": "<1 sentence referencing the answer>",
    "communication_quality": "<1 sentence referencing the answer>"
  }}
}}"""

    input_payload = {
        "interview_type": interview_type,
        "role": role,
        "question": question,
        "answer_length": len(answer),
    }

    start = time.monotonic()
    try:
        message = await _get_client().messages.create(
            model=settings.claude_model,
            max_tokens=1024,
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
            agent_name="answer_evaluation",
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
            agent_name="answer_evaluation",
            model=settings.claude_model,
            input_payload=input_payload,
            output_payload=None,
            latency_ms=latency_ms,
            status="error",
            error=str(exc),
        )
        raise
