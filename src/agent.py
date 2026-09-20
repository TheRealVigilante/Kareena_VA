# agent.py
# ─────────────────────────────────────────────────────────────────────────────
#  Kareena VA — Agent layer
#
#  Primary model : LM Studio (local, Spark X2.5 4B GGUF Q4_K_M)
#                  OpenAI-compatible API at http://localhost:1234/v1
#
#  Fallback model: Gemini API  (gemma-4-31b-it, free tier)
#                  Also exposed as an OpenAI-compatible endpoint by Google.
#
#  Tool loop     : ReAct-style — the LLM can call any tool in mcp_tools.py,
#                  we execute it and feed the result back until the model
#                  produces a plain-text final answer (no more tool calls).
#
#  Usage (from assistant_core.py):
#      from agent import run as agent_run
#      answer = agent_run("what is the weather in Cairo right now?")
# ─────────────────────────────────────────────────────────────────────────────

import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from mcp_tools import TOOL_SCHEMAS, run_tool

load_dotenv()

# ── Configuration ─────────────────────────────────────────────────────────────

_LM_BASE_URL   = os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1/")
_LM_API_KEY    = os.getenv("LM_STUDIO_API_KEY",  "lm-studio")
_LM_MODEL      = os.getenv("LM_STUDIO_MODEL",    "spark-x2.5-4b")

_GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
_GEMINI_MODEL   = os.getenv("GEMINI_MODEL",   "gemma-4-31b-it")
_GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

_MAX_ITERATIONS = int(os.getenv("AGENT_MAX_ITERATIONS", "5"))

# ── OpenAI clients ────────────────────────────────────────────────────────────

_lm_client = OpenAI(
    base_url=_LM_BASE_URL,
    api_key=_LM_API_KEY,
)

_gemini_client: OpenAI | None = None
if _GEMINI_API_KEY:
    _gemini_client = OpenAI(
        base_url=_GEMINI_BASE_URL,
        api_key=_GEMINI_API_KEY,
    )

# ── System prompt ─────────────────────────────────────────────────────────────

_SYSTEM_PROMPT = """You are Kareena, a helpful voice assistant.
You have access to a set of tools. Use them whenever you need current information,
need to read or write files, or need to remember something for later.

Rules:
- Always respond in plain, conversational English — your answer will be spoken aloud.
- Keep answers concise (2–4 sentences is ideal unless the user asks for more).
- If you use a tool, wait for its result before forming your final answer.
- Never make up facts. If you are unsure, say so and offer to search.
- Do not mention tool names in your final spoken answer.
"""

# ── Internal helpers ──────────────────────────────────────────────────────────

def _chat(client: OpenAI, model: str, messages: list, use_tools: bool = True) -> object:
    """Send a chat completion request, optionally with tools."""
    kwargs = dict(model=model, messages=messages, temperature=0.7)
    if use_tools:
        kwargs["tools"] = TOOL_SCHEMAS
        kwargs["tool_choice"] = "auto"
    return client.chat.completions.create(**kwargs)


def _is_lm_studio_running() -> bool:
    """Quick check whether LM Studio's server is reachable."""
    import urllib.request
    try:
        # Probe the models endpoint — works regardless of trailing slash
        probe = _LM_BASE_URL.rstrip("/") + "/models"
        urllib.request.urlopen(probe, timeout=2)
        return True
    except Exception:
        return False


def _tool_loop(client: OpenAI, model: str, messages: list) -> str:
    """
    Run the ReAct tool-calling loop.

    Sends messages to the model. If it returns tool calls, execute them,
    append results, and call again — up to _MAX_ITERATIONS times.
    Returns the final plain-text answer.
    """
    for iteration in range(_MAX_ITERATIONS):
        response = _chat(client, model, messages)
        choice = response.choices[0]
        msg = choice.message

        # No tool calls → we have a final answer
        if not msg.tool_calls:
            return (msg.content or "").strip()

        # Append the assistant's tool-call message to history
        messages.append(msg)

        # Execute every tool the model requested
        for tc in msg.tool_calls:
            fn_name = tc.function.name
            try:
                fn_args = json.loads(tc.function.arguments)
            except json.JSONDecodeError:
                fn_args = {}

            result = run_tool(fn_name, fn_args)

            # Feed result back as a tool message
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result,
            })

    # Exceeded max iterations — ask for a plain answer without tools
    messages.append({
        "role": "user",
        "content": "Please give me your final answer now based on what you have found.",
    })
    response = _chat(client, model, messages, use_tools=False)
    return (response.choices[0].message.content or "").strip()


# ── Public API ────────────────────────────────────────────────────────────────

def run(query: str, conversation_history: list | None = None) -> str:
    """
    Run the agent on *query* and return a plain-text answer.

    conversation_history: optional list of previous {role, content} dicts
    so the agent has context from earlier in the conversation.

    Tries LM Studio first; falls back to Gemini if LM Studio is unreachable
    or raises an error.
    """
    messages = [{"role": "system", "content": _SYSTEM_PROMPT}]
    if conversation_history:
        messages.extend(conversation_history)
    messages.append({"role": "user", "content": query})

    # ── Try LM Studio (primary) ───────────────────────────────────────────────
    if _is_lm_studio_running():
        try:
            return _tool_loop(_lm_client, _LM_MODEL, messages)
        except Exception as e:
            print(f"[Agent] LM Studio error: {e}. Falling back to Gemini.")
    else:
        print("[Agent] LM Studio not reachable. Falling back to Gemini.")

    # ── Try Gemini (fallback) ─────────────────────────────────────────────────
    if _gemini_client is None:
        return (
            "I'm sorry, I couldn't reach my local model and no Gemini API key "
            "is configured. Please start LM Studio or add your GEMINI_API_KEY to the .env file."
        )
    try:
        # Rebuild messages — Gemini's OpenAI-compat layer needs a fresh list
        messages = [{"role": "system", "content": _SYSTEM_PROMPT}]
        if conversation_history:
            messages.extend(conversation_history)
        messages.append({"role": "user", "content": query})
        return _tool_loop(_gemini_client, _GEMINI_MODEL, messages)
    except Exception as e:
        return f"I encountered an error with both models: {e}"
