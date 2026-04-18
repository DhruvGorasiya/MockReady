"""
Tests for agent invocation logging — TDD red phase.

Verifies that all three agents emit a structured log record on every invocation
containing the required fields: agent_id, agent_name, model, timestamp,
latency_ms, input_payload, output_payload, status.
On failure the record must also contain an 'error' field.
"""
import json
import logging
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.agents.answer_evaluation import evaluate_answer
from app.agents.feedback_synthesis import synthesize_feedback
from app.agents.question_generation import generate_questions

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_EVAL_OUTPUT = json.dumps(
    {
        "clarity": 7,
        "depth": 6,
        "structure": 8,
        "relevance": 7,
        "communication_quality": 7,
        "reasoning": {
            "clarity": "The candidate explained the concept clearly.",
            "depth": "Moderate depth with some gaps.",
            "structure": "Well-structured response.",
            "relevance": "Directly answered the question.",
            "communication_quality": "Good pacing and vocabulary.",
        },
    }
)

_FEEDBACK_OUTPUT = json.dumps(
    {
        "feedback_summary": "Overall solid answer.",
        "dimension_feedback": {
            "clarity": "You opened with a clear statement.",
            "depth": "Add more examples.",
            "structure": "Good use of signposting.",
            "relevance": "Stayed on topic throughout.",
            "communication_quality": "Confident delivery.",
        },
        "improvement_suggestion": "Start with a one-line summary next time.",
    }
)

_QUESTIONS_OUTPUT = json.dumps([{"text": "Tell me about a time you led a project."}])


def _mock_message(text: str):
    content = MagicMock()
    content.text = text
    msg = MagicMock()
    msg.content = [content]
    return msg


# ---------------------------------------------------------------------------
# answer_evaluation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_evaluate_answer_logs_on_success(caplog):
    with patch("app.agents.answer_evaluation._get_client") as mock_get_client:
        client = AsyncMock()
        client.messages.create = AsyncMock(return_value=_mock_message(_EVAL_OUTPUT))
        mock_get_client.return_value = client

        with caplog.at_level(logging.INFO, logger="app.agents.answer_evaluation"):
            await evaluate_answer("What is X?", "My answer...", "behavioral", "SWE")

    assert len(caplog.records) == 1
    data = json.loads(caplog.records[0].message)
    assert data["agent_name"] == "answer_evaluation"
    assert "agent_id" in data
    assert "model" in data
    assert "timestamp" in data
    assert "latency_ms" in data
    assert data["status"] == "success"
    assert "input_payload" in data
    assert "output_payload" in data


@pytest.mark.asyncio
async def test_evaluate_answer_logs_on_failure(caplog):
    with patch("app.agents.answer_evaluation._get_client") as mock_get_client:
        client = AsyncMock()
        client.messages.create = AsyncMock(side_effect=RuntimeError("API timeout"))
        mock_get_client.return_value = client

        with caplog.at_level(logging.ERROR, logger="app.agents.answer_evaluation"):
            with pytest.raises(RuntimeError):
                await evaluate_answer("What is X?", "My answer...", "behavioral", "SWE")

    assert len(caplog.records) == 1
    data = json.loads(caplog.records[0].message)
    assert data["agent_name"] == "answer_evaluation"
    assert data["status"] == "error"
    assert "error" in data
    assert "latency_ms" in data


# ---------------------------------------------------------------------------
# feedback_synthesis
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_synthesize_feedback_logs_on_success(caplog):
    with patch("app.agents.feedback_synthesis._get_client") as mock_get_client:
        client = AsyncMock()
        client.messages.create = AsyncMock(return_value=_mock_message(_FEEDBACK_OUTPUT))
        mock_get_client.return_value = client

        with caplog.at_level(logging.INFO, logger="app.agents.feedback_synthesis"):
            await synthesize_feedback(
                "What is X?",
                "My answer...",
                {"clarity": 7},
                {"clarity": "Clear."},
                "behavioral",
                "SWE",
            )

    assert len(caplog.records) == 1
    data = json.loads(caplog.records[0].message)
    assert data["agent_name"] == "feedback_synthesis"
    assert "agent_id" in data
    assert "model" in data
    assert "timestamp" in data
    assert "latency_ms" in data
    assert data["status"] == "success"
    assert "input_payload" in data
    assert "output_payload" in data


@pytest.mark.asyncio
async def test_synthesize_feedback_logs_on_failure(caplog):
    with patch("app.agents.feedback_synthesis._get_client") as mock_get_client:
        client = AsyncMock()
        client.messages.create = AsyncMock(side_effect=RuntimeError("API timeout"))
        mock_get_client.return_value = client

        with caplog.at_level(logging.ERROR, logger="app.agents.feedback_synthesis"):
            with pytest.raises(RuntimeError):
                await synthesize_feedback(
                    "What is X?",
                    "My answer...",
                    {},
                    {},
                    "behavioral",
                    "SWE",
                )

    assert len(caplog.records) == 1
    data = json.loads(caplog.records[0].message)
    assert data["agent_name"] == "feedback_synthesis"
    assert data["status"] == "error"
    assert "error" in data
    assert "latency_ms" in data


# ---------------------------------------------------------------------------
# question_generation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_generate_questions_logs_on_success(caplog):
    with patch("app.agents.question_generation._get_client") as mock_get_client:
        client = AsyncMock()
        client.messages.create = AsyncMock(return_value=_mock_message(_QUESTIONS_OUTPUT))
        mock_get_client.return_value = client

        with caplog.at_level(logging.INFO, logger="app.agents.question_generation"):
            await generate_questions("behavioral", "SWE", question_count=1)

    assert len(caplog.records) == 1
    data = json.loads(caplog.records[0].message)
    assert data["agent_name"] == "question_generation"
    assert "agent_id" in data
    assert "model" in data
    assert "timestamp" in data
    assert "latency_ms" in data
    assert data["status"] == "success"
    assert "input_payload" in data
    assert "output_payload" in data


@pytest.mark.asyncio
async def test_generate_questions_logs_on_failure(caplog):
    with patch("app.agents.question_generation._get_client") as mock_get_client:
        client = AsyncMock()
        client.messages.create = AsyncMock(side_effect=RuntimeError("API timeout"))
        mock_get_client.return_value = client

        with caplog.at_level(logging.ERROR, logger="app.agents.question_generation"):
            with pytest.raises(RuntimeError):
                await generate_questions("behavioral", "SWE", question_count=1)

    assert len(caplog.records) == 1
    data = json.loads(caplog.records[0].message)
    assert data["agent_name"] == "question_generation"
    assert data["status"] == "error"
    assert "error" in data
    assert "latency_ms" in data
