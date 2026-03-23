import json

from anthropic import AsyncAnthropic

from app.core.config import settings

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

    message = await _get_client().messages.create(
        model=settings.claude_model,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())
