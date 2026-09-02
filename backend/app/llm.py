from __future__ import annotations

import time
from functools import lru_cache
from typing import TypeVar

from loguru import logger
from pydantic import BaseModel

from app.config import get_settings

T = TypeVar("T", bound=BaseModel)


class LLMUnavailableError(RuntimeError):
    """Raised when no usable LLM credential is configured."""


@lru_cache(maxsize=1)
def _get_chat_model():
    settings = get_settings()

    if settings.llm_provider == "anthropic":
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(model=settings.anthropic_model, api_key=settings.anthropic_api_key, temperature=0)

    if settings.llm_provider == "featherless":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=settings.featherless_model,
            api_key=settings.featherless_api_key,
            base_url=settings.featherless_base_url,
            # Small open-source models under greedy decoding (temperature=0) can
            # enter a token-repetition loop during tool-call generation instead
            # of terminating -- observed directly against this model/gateway: a
            # trivial prompt produced 13 duplicate tool calls in one response.
            # A touch of randomness breaks the loop tendency, and max_tokens
            # caps the blast radius if it happens anyway (our schemas are all
            # small, so a genuine response never needs anywhere near this).
            temperature=0.2,
            max_tokens=800,
        )

    if settings.llm_provider == "openai":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(model=settings.openai_model, api_key=settings.openai_api_key, temperature=0)

    raise LLMUnavailableError("Neither ANTHROPIC_API_KEY nor OPENAI_API_KEY is set.")


def _structured_output_method() -> str | None:
    # OpenAI-compatible gateways (Featherless in particular, and any other
    # third-party endpoint) don't reliably implement OpenAI's native
    # `response_format: json_schema` structured-output mode -- it can return a
    # malformed response that crashes the OpenAI SDK's own parser. Plain
    # function-calling is far more broadly supported, so force it for every
    # OpenAI-compatible provider. Anthropic's tool-calling path doesn't hit
    # this and uses langchain_anthropic's own (working) default.
    if get_settings().llm_provider in ("openai", "featherless"):
        return "function_calling"
    return None


def structured_completion(
    *,
    agent_name: str,
    system_prompt: str,
    user_prompt: str,
    schema: type[T],
) -> T | None:
    """Call the configured LLM and parse its response into `schema`.

    Returns None (never raises) on any failure -- missing/invalid credentials, API
    errors, or a response that fails Pydantic validation -- so a single agent's LLM
    call can never take down the pipeline. Callers must treat None as "this agent
    has no opinion" and degrade accordingly (e.g. low confidence, neutral stance).

    Retries on failure (3 attempts total). Smaller open-source models (e.g. via
    Featherless) intermittently emit an empty or malformed tool call even with
    function-calling forced and temperature 0 -- confirmed non-deterministic by
    direct testing, not a schema incompatibility, so retrying is the correct
    mitigation rather than simplifying the schema. This doesn't mask a genuinely
    broken schema or a real auth/network failure -- those fail identically every
    attempt and still return None.
    """
    method = _structured_output_method()
    kwargs = {"method": method} if method else {}

    last_error: Exception | None = None
    for attempt in range(3):
        try:
            model = _get_chat_model().with_structured_output(schema, **kwargs)
            result = model.invoke(
                [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ]
            )
        except Exception as exc:  # noqa: BLE001 - any LLM/network/auth failure degrades gracefully
            last_error = exc
            logger.warning(
                "{} LLM call failed on attempt {} ({}): {}",
                agent_name,
                attempt + 1,
                type(exc).__name__,
                exc,
            )
            time.sleep(1.5 * (attempt + 1))
            continue

        if not isinstance(result, schema):
            logger.warning("{} LLM call returned unexpected type {}", agent_name, type(result))
            last_error = TypeError(f"unexpected type {type(result)}")
            continue

        return result

    logger.warning("{} LLM call failed after retry, last error: {}", agent_name, last_error)
    return None
