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


async def generate_questions(
    interview_type: str,
    role: str,
    question_count: int = 3,
) -> list[dict]:
    """Call Claude to generate interview questions. Returns list of {text} dicts."""
    prompt = f"""Generate {question_count} interview questions for a {role} candidate in a {interview_type} interview.

Rules:
- behavioral: use STAR-method prompts ("Tell me about a time when...")
- technical: {role}-specific technical concepts and problem solving
- system_design: designing systems relevant to a {role}
- Questions must be realistic and substantive

Return ONLY a JSON array, no markdown, no extra text:
[{{"text": "question text"}}]"""

    input_payload = {
        "interview_type": interview_type,
        "role": role,
        "question_count": question_count,
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
        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        result = json.loads(raw.strip())

        log_agent_invocation(
            logger=logger,
            agent_name="question_generation",
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
            agent_name="question_generation",
            model=settings.claude_model,
            input_payload=input_payload,
            output_payload=None,
            latency_ms=latency_ms,
            status="error",
            error=str(exc),
        )
        raise
