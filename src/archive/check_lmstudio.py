"""
check_lmstudio.py
Quick sanity check for LM Studio local server.
Run with: conda run -n dawn python check_lmstudio.py
"""

import sys
from openai import OpenAI

# Force UTF-8 so ✓ ✗ ⚠ render correctly on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_URL = "http://localhost:1234/v1/"
API_KEY  = "lm-studio"

client = OpenAI(base_url=BASE_URL, api_key=API_KEY)

# ── 1. Server reachable? ──────────────────────────────────────────────────────
print("1. Checking server connection...")
try:
    models = client.models.list()
    print(f"   ✓ Server is running at {BASE_URL}")
except Exception as e:
    print(f"   ✗ Cannot reach LM Studio: {e}")
    print("   Make sure LM Studio is open and the Local Server is started.")
    sys.exit(1)

# ── 2. Simple chat completion ─────────────────────────────────────────────────
model_to_test = "spark-x2.5-4b"
print(f"\n2. Sending a test message to '{model_to_test}'...")
try:
    response = client.chat.completions.create(
        model=model_to_test,
        messages=[{"role": "user", "content": "What can you do"}],
        temperature=0
    )
    reply = response.choices[0].message.content.strip()
    print(f"   ✓ Response: {reply}")
except Exception as e:
    print(f"   ✗ Chat completion failed: {e}")
    sys.exit(1)

# ── 3. Tool calling support ───────────────────────────────────────────────────
print("\n3. Checking tool-calling support...")
tool = {
    "type": "function",
    "function": {
        "name": "get_answer",
        "description": "Returns the answer.",
        "parameters": {
            "type": "object",
            "properties": {
                "answer": {"type": "string"}
            },
            "required": ["answer"],
        },
    },
}
try:
    response = client.chat.completions.create(
        model=model_to_test,
        messages=[{"role": "user", "content": "What is 2 + 2? Use the get_answer tool."}],
        tools=[tool],
        tool_choice="auto",
        temperature=0,
        max_tokens=100,
    )
    choice = response.choices[0]
    if choice.message.tool_calls:
        fn = choice.message.tool_calls[0].function
        print(f"   ✓ Tool call received: {fn.name}({fn.arguments})")
    else:
        print(f"   ⚠ No tool call made — model replied directly: {choice.message.content}")
        print("     Tool calling may not be supported by this model.")
except Exception as e:
    print(f"   ✗ Tool calling failed: {e}")

print("\n─── Done ───")
