import json

from anthropic import AsyncAnthropic

from app.core.config import settings

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

    message = await _get_client().messages.create(
        model=settings.claude_model,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()
    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())
