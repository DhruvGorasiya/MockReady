"""Shared structured logging helper for AI agent invocations."""
import json
import logging
from datetime import datetime, timezone
from uuid import uuid4


def log_agent_invocation(
    logger: logging.Logger,
    agent_name: str,
    model: str,
    input_payload: dict,
    output_payload: dict | None,
    latency_ms: float,
    status: str,
    error: str | None = None,
) -> None:
    """Emit a single structured JSON log record for an agent call."""
    record: dict = {
        "agent_id": str(uuid4()),
        "agent_name": agent_name,
        "model": model,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "latency_ms": round(latency_ms, 2),
        "status": status,
        "input_payload": input_payload,
    }
    if output_payload is not None:
        record["output_payload"] = output_payload
    if error is not None:
        record["error"] = error

    if status == "error":
        logger.error(json.dumps(record))
    else:
        logger.info(json.dumps(record))
