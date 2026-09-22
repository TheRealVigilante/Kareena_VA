# mcp_tools.py
# ─────────────────────────────────────────────────────────────────────────────
#  All MCP-style tool implementations for Kareena's agent.
#  Each tool is a plain Python function.
#  TOOL_SCHEMAS is the list of OpenAI function-call schema dicts that gets
#  sent to the LLM so it knows what tools are available.
#  run_tool() dispatches a tool call by name and returns a string result.
# ─────────────────────────────────────────────────────────────────────────────

import ast
import datetime
import json
import math
import operator
import os
import re

import requests
from duckduckgo_search import DDGS

# ── Filesystem sandbox ────────────────────────────────────────────────────────
# Resolved once at import time from the env var AGENT_FS_ROOT.
# All file operations are restricted to this directory.
_FS_ROOT = os.path.realpath(
    os.getenv("AGENT_FS_ROOT") or
    os.path.dirname(os.path.abspath(__file__))
)

_MEMORY_FILE = os.path.join(_FS_ROOT, ".kareena_memory.json")


# ─────────────────────────────────────────────────────────────────────────────
#  1. Web Search  (DuckDuckGo, no API key)
# ─────────────────────────────────────────────────────────────────────────────

def duckduckgo_search(query: str, max_results: int = 5) -> str:
    """Return top DuckDuckGo results for *query* as a formatted string."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        if not results:
            return "No results found."
        lines = []
        for i, r in enumerate(results, 1):
            lines.append(f"{i}. {r.get('title', '')}\n   {r.get('href', '')}\n   {r.get('body', '')}")
        return "\n\n".join(lines)
    except Exception as e:
        return f"Search error: {e}"


# ─────────────────────────────────────────────────────────────────────────────
#  2. URL Fetch  (HTML → plain text)
# ─────────────────────────────────────────────────────────────────────────────

def fetch_url(url: str, max_chars: int = 3000) -> str:
    """Fetch *url* and return its readable text content (HTML stripped)."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (KareenaVA/1.0)"}
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        # Strip HTML tags simply — good enough for most pages
        text = re.sub(r"<[^>]+>", " ", resp.text)
        text = re.sub(r"\s+", " ", text).strip()
        return text[:max_chars] + ("…" if len(text) > max_chars else "")
    except Exception as e:
        return f"Fetch error: {e}"


def summarise_url(url: str, focus: str = "") -> str:
    """Fetch *url* and return a rich text extract suitable for LLM summarisation.

    Unlike fetch_url this function:
    - Uses a larger character budget (6000 chars) so the LLM has enough context.
    - Accepts an optional *focus* hint (e.g. 'key findings', 'release date')
      which is prepended to the result so the model knows what to extract.
    - Strips scripts and style blocks before general HTML removal for cleaner text.
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0 (KareenaVA/1.0)"}
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        html = resp.text
        # Remove <script> and <style> blocks entirely
        html = re.sub(r"<(script|style)[^>]*>[\s\S]*?</\1>", " ", html, flags=re.IGNORECASE)
        # Strip remaining HTML tags
        text = re.sub(r"<[^>]+>", " ", html)
        text = re.sub(r"\s+", " ", text).strip()
        extract = text[:6000] + ("…" if len(text) > 6000 else "")
        if focus:
            return f"[Focus: {focus}]\n\n{extract}"
        return extract
    except Exception as e:
        return f"Summarise error: {e}"


# ─────────────────────────────────────────────────────────────────────────────
#  3. Filesystem  (sandboxed to _FS_ROOT)
# ─────────────────────────────────────────────────────────────────────────────

def _safe_path(filename: str) -> str:
    """Resolve *filename* inside _FS_ROOT and raise if it escapes the sandbox."""
    full = os.path.realpath(os.path.join(_FS_ROOT, filename))
    if not full.startswith(_FS_ROOT):
        raise ValueError(f"Access denied: '{filename}' is outside the allowed directory.")
    return full


def read_file(filename: str) -> str:
    """Read a file inside the sandbox and return its contents."""
    try:
        path = _safe_path(filename)
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Read error: {e}"


def write_file(filename: str, content: str) -> str:
    """Write *content* to *filename* inside the sandbox (creates or overwrites)."""
    try:
        path = _safe_path(filename)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Written {len(content)} characters to '{filename}'."
    except Exception as e:
        return f"Write error: {e}"


def list_files(subdirectory: str = "") -> str:
    """List files in *subdirectory* (relative to sandbox root)."""
    try:
        target = _safe_path(subdirectory) if subdirectory else _FS_ROOT
        entries = os.listdir(target)
        if not entries:
            return "Directory is empty."
        return "\n".join(sorted(entries))
    except Exception as e:
        return f"List error: {e}"


# ─────────────────────────────────────────────────────────────────────────────
#  4. Time  (timezone-aware)
# ─────────────────────────────────────────────────────────────────────────────

def get_time(timezone: str = "local") -> str:
    """Return the current date and time. Pass an IANA timezone name or 'local'."""
    try:
        if timezone.lower() == "local":
            now = datetime.datetime.now().astimezone()
        else:
            import zoneinfo
            tz = zoneinfo.ZoneInfo(timezone)
            now = datetime.datetime.now(tz)
        return now.strftime("%A, %d %B %Y  %H:%M:%S %Z")
    except Exception as e:
        return f"Time error: {e}"


# ─────────────────────────────────────────────────────────────────────────────
#  5. Memory  (persistent JSON store across sessions)
# ─────────────────────────────────────────────────────────────────────────────

def _load_memory() -> dict:
    if os.path.exists(_MEMORY_FILE):
        with open(_MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_memory(mem: dict) -> None:
    with open(_MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(mem, f, indent=2)


def remember(key: str, value: str) -> str:
    """Store *value* under *key* in persistent memory."""
    mem = _load_memory()
    mem[key] = value
    _save_memory(mem)
    return f"Remembered: {key} = {value}"


def recall(key: str = "") -> str:
    """Retrieve a memory by *key*, or list all keys if *key* is empty."""
    mem = _load_memory()
    if not mem:
        return "Memory is empty."
    if key:
        return mem.get(key, f"Nothing stored under '{key}'.")
    return "\n".join(f"{k}: {v}" for k, v in mem.items())


def forget(key: str) -> str:
    """Delete a memory entry by *key*."""
    mem = _load_memory()
    if key in mem:
        del mem[key]
        _save_memory(mem)
        return f"Forgot '{key}'."
    return f"No memory found for '{key}'."


# ─────────────────────────────────────────────────────────────────────────────
#  6. Math  (safe expression evaluator)
# ─────────────────────────────────────────────────────────────────────────────

# Safe whitelist of AST node types and operators
_SAFE_NODES = (
    ast.Expression, ast.BinOp, ast.UnaryOp, ast.Call, ast.Constant, ast.Name,
    ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod,
    ast.Pow, ast.USub, ast.UAdd,
)

_SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

# Allowed math functions and constants
_MATH_ENV = {
    name: getattr(math, name)
    for name in (
        "sqrt", "cbrt", "exp", "log", "log2", "log10",
        "sin", "cos", "tan", "asin", "acos", "atan", "atan2",
        "sinh", "cosh", "tanh",
        "ceil", "floor", "factorial", "gcd", "lcm",
        "degrees", "radians", "hypot", "isqrt",
        "pi", "e", "tau", "inf", "nan",
    )
    if hasattr(math, name)
}
_MATH_ENV["abs"] = abs
_MATH_ENV["round"] = round
_MATH_ENV["pow"] = pow


def _safe_eval(node):
    """Recursively evaluate a whitelisted AST node."""
    if not isinstance(node, _SAFE_NODES):
        raise ValueError(f"Unsafe expression: {ast.dump(node)}")
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body)
    if isinstance(node, ast.Constant):
        if not isinstance(node.value, (int, float, complex)):
            raise ValueError(f"Unsupported literal type: {type(node.value).__name__}")
        return node.value
    if isinstance(node, ast.Name):
        val = _MATH_ENV.get(node.id)
        if val is None or callable(val):
            raise ValueError(f"Unknown name: '{node.id}'")
        return val
    if isinstance(node, ast.BinOp):
        op_fn = _SAFE_OPERATORS.get(type(node.op))
        if op_fn is None:
            raise ValueError(f"Unsupported binary operator: {type(node.op).__name__}")
        return op_fn(_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp):
        op_fn = _SAFE_OPERATORS.get(type(node.op))
        if op_fn is None:
            raise ValueError(f"Unsupported unary operator: {type(node.op).__name__}")
        return op_fn(_safe_eval(node.operand))
    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise ValueError("Only named function calls are allowed.")
        fn = _MATH_ENV.get(node.func.id)
        if fn is None:
            raise ValueError(f"Unknown function: '{node.func.id}'")
        args = [_safe_eval(a) for a in node.args]
        if node.keywords:
            raise ValueError("Keyword arguments are not supported.")
        return fn(*args)
    raise ValueError(f"Unsupported node type: {type(node).__name__}")


def calculate(expression: str) -> str:
    """Safely evaluate a mathematical expression and return the result.

    Supports arithmetic operators (+, -, *, /, //, %, **) and common math
    functions from the ``math`` module (sqrt, sin, cos, log, etc.) as well
    as the constants pi, e, and tau.

    Examples::

        calculate("2 ** 10")              # 1024
        calculate("sqrt(144)")            # 12.0
        calculate("sin(pi / 2)")          # 1.0
        calculate("log(e ** 3)")          # 3.0
        calculate("(3 + 4) * 2 - 1")     # 13
    """
    try:
        tree = ast.parse(expression.strip(), mode="eval")
        result = _safe_eval(tree)
        # Return a clean representation
        if isinstance(result, float) and result.is_integer():
            return str(int(result))
        return str(result)
    except (SyntaxError, ValueError, TypeError, ZeroDivisionError) as e:
        return f"Math error: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"


# ─────────────────────────────────────────────────────────────────────────────
#  Tool registry
# ─────────────────────────────────────────────────────────────────────────────

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "duckduckgo_search",
            "description": "Search the web using DuckDuckGo. Returns top results with titles, URLs, and snippets. Use for current events, facts, or anything requiring up-to-date information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query."},
                    "max_results": {"type": "integer", "description": "Number of results to return (default 5, max 10).", "default": 5},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_url",
            "description": "Fetch the content of a web page and return it as plain text. Use after a search when you need the full content of a specific URL.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "The full URL to fetch."},
                    "max_chars": {"type": "integer", "description": "Maximum characters to return (default 3000).", "default": 3000},
                },
                "required": ["url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "summarise_url",
            "description": "Fetch a web page and return a rich text extract (up to 6000 chars, scripts/styles removed) for you to summarise in natural language. Prefer this over fetch_url when the user asks you to summarise, explain, or describe the content of a URL. Optionally pass a focus hint to steer the summary.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "The full URL to summarise."},
                    "focus": {"type": "string", "description": "Optional topic to focus the summary on, e.g. 'main argument', 'release date', 'pricing'.", "default": ""},
                },
                "required": ["url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a file from the local filesystem. Only files inside the project directory are accessible.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "Relative path to the file (e.g. 'data.txt' or 'notes/todo.txt')."},
                },
                "required": ["filename"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write text content to a file on the local filesystem. Creates the file if it does not exist.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "Relative path to the file to write."},
                    "content": {"type": "string", "description": "The text content to write."},
                },
                "required": ["filename", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List the files in a directory inside the project folder.",
            "parameters": {
                "type": "object",
                "properties": {
                    "subdirectory": {"type": "string", "description": "Relative subdirectory to list (leave empty for root).", "default": ""},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_time",
            "description": "Get the current date and time, optionally in a specific timezone.",
            "parameters": {
                "type": "object",
                "properties": {
                    "timezone": {"type": "string", "description": "IANA timezone name (e.g. 'America/New_York') or 'local' for system time.", "default": "local"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "remember",
            "description": "Store a piece of information in persistent memory so it can be recalled in future sessions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "A short label for the memory (e.g. 'user_birthday')."},
                    "value": {"type": "string", "description": "The value to store."},
                },
                "required": ["key", "value"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "recall",
            "description": "Retrieve a stored memory by key, or list all stored memories if no key is given.",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "The key to look up. Leave empty to list all memories.", "default": ""},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "forget",
            "description": "Delete a memory entry by key.",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "The key of the memory to delete."},
                },
                "required": ["key"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": (
                "Evaluate a mathematical expression and return the numeric result. "
                "Supports arithmetic operators (+, -, *, /, //, %, **) and common "
                "math functions such as sqrt(), sin(), cos(), tan(), log(), log2(), "
                "log10(), exp(), ceil(), floor(), factorial(), degrees(), radians(), "
                "hypot(), abs(), round(), and pow(). Also recognises the constants "
                "pi, e, and tau. Use this for any calculation instead of reasoning "
                "through arithmetic yourself."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": (
                            "A valid mathematical expression string, e.g. "
                            "'sqrt(2) * pi', '2 ** 10', or 'log(e ** 3)'."
                        ),
                    },
                },
                "required": ["expression"],
            },
        },
    },
]

# Maps tool name → callable
_TOOL_MAP = {
    "duckduckgo_search": duckduckgo_search,
    "fetch_url": fetch_url,
    "summarise_url": summarise_url,
    "read_file": read_file,
    "write_file": write_file,
    "list_files": list_files,
    "get_time": get_time,
    "remember": remember,
    "recall": recall,
    "forget": forget,
    "calculate": calculate,
}


def run_tool(name: str, arguments: dict) -> str:
    """Dispatch a tool call by name. Returns the result as a string."""
    fn = _TOOL_MAP.get(name)
    if fn is None:
        return f"Unknown tool: '{name}'"
    try:
        return str(fn(**arguments))
    except Exception as e:
        return f"Tool '{name}' raised an error: {e}"
