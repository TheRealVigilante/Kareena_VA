# Kareena VA

A Python-based voice assistant that has evolved across three versions — from a simple rule-based chatbot to a full GUI-driven assistant with a local AI agent and tool-use capabilities.

---

## Version History

### v1 — Group Project (Rule-Based Chatbot)
The original version was built as a group project. It was a straightforward rule-based voice assistant that listened for a wake word ("hello") and matched spoken commands against a hardcoded list of actions — opening websites, telling the time, reading the clipboard, and so on. Everything ran in the terminal.

### v2 — Extended Features
Built individually on top of v1. This version added several new capabilities and companion modules:

- `NameApp` — a GUI window that asks for the user's name at startup
- `PhoneBookApp` — a persistent phonebook for storing and selecting contacts for WhatsApp messages
- `TimerApp` — a countdown timer with an alarm sound
- `StopWatchApp` — a functional stopwatch
- Weather lookup, Wikipedia search, YouTube playback, screenshot capture, CPU monitoring, and to-do note saving

All GUI components were built with `tkinter`.

### v3 — Agent, MCP Tools & New UI (Current)
This version is a significant architectural upgrade:

- **Full Toga (BeeWare) GUI** — the entire assistant now has a native desktop window with a live chat log, status indicator, and voice controls. All sub-app windows (Timer, Stopwatch, etc.) were migrated from `tkinter` to Toga.
- **Local AI Agent** — a ReAct-style tool-calling agent powered by a local LLM running in LM Studio. The agent handles any command that doesn't match the hardcoded rules, and can also be invoked explicitly.
- **Gemini API fallback** — if LM Studio is not running, the agent automatically falls back to Google's `gemma-4-31b-it` model via the Gemini API (free tier).
- **MCP-style tools** — the agent has access to a suite of tools it can call autonomously: web search (DuckDuckGo), URL fetching and summarisation, file read/write, time/timezone queries, and a persistent memory store.
- **Output cleaner** — agent responses are automatically stripped of markdown and encoding artifacts before being spoken aloud.
- **Voice retry loop** — if speech recognition fails, Kareena retries up to 3 times with spoken feedback instead of silently dropping the input.
- **To-do management** — saved to-dos can now be deleted individually or cleared in bulk.
- **Battery, calendar, and chat mode** — new built-in commands for battery status, the current month's calendar, and a free-chat mode that removes the wake-word requirement.
- **Startup chime** — a short sound plays after the name prompt to signal Kareena is ready.
- **Save Log button** — the GUI now has a 💾 button that exports the full chat log to the Desktop.

---

## Project Structure

```
Kareena_VA/
├── src/
│   ├── main.py               # Entry point — launches the Toga app
│   ├── KareenaApp.py         # Main Toga window (chat log, status, buttons)
│   ├── assistant_core.py     # All voice assistant logic and the command loop
│   ├── agent.py              # LLM agent — LM Studio primary, Gemini fallback
│   ├── mcp_tools.py          # Agent tools: search, fetch, files, time, memory
│   ├── NameApp.py            # Toga window — asks for the user's name at startup
│   ├── PhoneBookApp.py       # Toga window — phonebook for WhatsApp contacts
│   ├── TimerApp.py           # Toga window — countdown timer
│   ├── StopWatchApp.py       # Toga window — stopwatch
│   ├── data.txt              # Saved to-do notes
│   ├── phonebook.json        # Saved contacts
│   ├── .kareena_memory.json  # Persistent agent memory (auto-created)
│   ├── .env                  # Your local environment config (not committed)
│   ├── .env.example          # Environment variable template
│   └── archive/              # Previous versions kept for reference
├── requirements.txt          # All Python dependencies
└── README.md
```

---

## Setup

### 1. Prerequisites

- Python 3.10+
- [Anaconda](https://www.anaconda.com/) or any virtual environment manager
- [LM Studio](https://lmstudio.ai/) — for the local AI agent
- A microphone connected to your machine

### 2. Create and activate the environment

```bash
conda create -n dawn python=3.10
conda activate dawn
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> `pyaudio` can be tricky on Windows. If it fails, install it via conda:
> ```bash
> conda install -c conda-forge pyaudio
> ```

### 4. Configure environment variables

Copy `src/.env.example` to `src/.env` and fill in your values:

```bash
cp src/.env.example src/.env
```

Open `src/.env` and set:

```env
# LM Studio — load a model and start the local server
LM_STUDIO_BASE_URL=http://localhost:1234/v1/
LM_STUDIO_API_KEY=lm-studio
LM_STUDIO_MODEL=your-model-name-here

# Gemini API — get a free key at https://aistudio.google.com/apikey
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemma-4-31b-it
```

The Gemini key is optional but recommended as a fallback when LM Studio is not running.

### 5. Set up LM Studio (for the local agent)

1. Download and open [LM Studio](https://lmstudio.ai/)
2. Search for and download a model with tool-calling support. Recommended options:
   - `Qwen2.5-7B-Instruct GGUF Q4_K_M` — best tool-calling at this size
   - `Qwen2.5-3B-Instruct GGUF Q4_K_M` — lighter, still reliable
   - `Llama-3.2-3B-Instruct GGUF` — good general use
   - `spark-x2.5-4b` - New and decent results on multiple benchmarks
3. Load the model and go to **Local Server** → click **Start Server**
4. The server runs at `http://localhost:1234/v1/` by default
5. Copy the exact model identifier shown in LM Studio into `LM_STUDIO_MODEL` in your `.env`

> To verify LM Studio is working correctly, run:
> ```bash
> conda run -n dawn python src/check_lmstudio.py
> ```
> This checks the server connection, lists loaded models, tests a basic chat response, and confirms tool-calling support.

### 6. Run the assistant

```bash
conda run -n dawn python src/main.py
```

Or with the environment activated:

```bash
python src/main.py
```

---

## How It Works

Kareena starts by opening a native desktop window and asking for your name. After that, she greets you and begins listening for voice commands.

The command loop works in order:

1. Hardcoded rules are checked first — fast, offline, no LLM needed
2. If you say **"agent ..."**, the agent is invoked directly
3. If nothing matches, the agent is used as a smart fallback

The agent runs a ReAct loop — it decides which tools to call, executes them, and synthesises a spoken answer. LM Studio is tried first; if it is unreachable, Gemini is used automatically instead.

---

## Voice Command Reference

### Built-in commands

| Say this | What happens |
|---|---|
| `google` | Opens Google |
| `github` | Opens GitHub |
| `facebook` | Opens Facebook |
| `instagram` | Opens Instagram |
| `twitter` | Opens Twitter |
| `onedrive` | Opens OneDrive |
| `[site] website` | Opens `https://www.[site].com` |
| `from wikipedia search [topic]` | Reads a Wikipedia summary |
| `tell me your name` | Kareena introduces herself |
| `what time` | Tells the current time |
| `day` | Tells today's date |
| `calendar` | Displays and announces the current month's calendar |
| `weather` | Asks for a city then fetches weather |
| `youtube` | Asks what to play then opens YouTube |
| `message` | Opens phonebook and sends a WhatsApp message |
| `joke` | Tells a random programming joke |
| `to do` | Saves a to-do note |
| `saved` | Reads all saved to-dos |
| `delete to do` | Lists to-dos by number and deletes the chosen one |
| `clear to dos` | Confirms then wipes the entire to-do list |
| `battery` | Reports battery percentage, charging state, and time remaining |
| `clipboard` | Reads current clipboard content |
| `screenshot` | Takes a screenshot |
| `cpu` | Reports CPU usage |
| `timer` | Opens the countdown timer window |
| `stopwatch` | Opens the stopwatch window |
| `chat` | Enters free-chat mode — bypasses all built-in rules until you say "exit chat" |
| `instructions` | Lists all available commands |
| `exit` | Says goodbye and closes the assistant |

### Agent commands

| Say this | What happens |
|---|---|
| `agent [any question]` | Sends the question directly to the AI agent |
| `agent` | Kareena asks what you need, then routes it to the agent |
| Any unrecognised command | Automatically falls back to the agent |

### Agent tool examples

```
"agent search for the latest news about Python"
"agent what time is it in Tokyo right now?"
"agent remember my favourite colour is blue"
"agent what do you remember about me?"
"agent fetch the content of https://example.com"
"agent write my shopping list to a file called shopping.txt"
"agent read the file data.txt"
"agent forget my favourite colour"
```

---

## Agent Tools

The agent picks and calls these tools automatically based on your request:

| Tool | Description |
|---|---|
| `duckduckgo_search` | Web search — no API key required |
| `fetch_url` | Fetches and reads the text content of any URL |
| `summarise_url` | Fetches a URL, strips scripts/styles, and returns up to 6000 chars for the LLM to summarise. Accepts an optional focus hint (e.g. "pricing", "release date") |
| `read_file` | Reads a file from the project directory |
| `write_file` | Writes text to a file in the project directory |
| `list_files` | Lists files in the project directory |
| `get_time` | Returns current date and time, supports any timezone |
| `remember` | Stores a key-value pair in persistent memory |
| `recall` | Retrieves a stored memory by key, or lists all memories |
| `forget` | Deletes a memory entry |

File access is sandboxed — the agent can only read and write inside the `src/` folder.

---

## GUI Features

| Button / Indicator | Description |
|---|---|
| 🎤 **Start Listening** | Starts the voice command loop |
| 🔇 **Stop** | Pauses the voice loop (resume with Start Listening) |
| 💾 **Save Log** | Exports the full chat log to a timestamped `.txt` file on your Desktop |
| ✕ **Exit** | Says goodbye and closes the assistant |
| **Status bar** | Shows current state: Idle / Listening / Recognising / Agent thinking… / Chat Mode |

### Startup chime
A short sound plays automatically after you enter your name to signal Kareena is ready. Place a `startup.mp3` in `src/` to use a custom chime; otherwise `Alarm.mp3` is used at low volume.

### Voice retry
If speech recognition fails, Kareena retries up to **3 times** with a spoken countdown ("Attempt 2 of 3 — please try again") before giving up, instead of silently dropping the input.

### Chat mode
Say **`chat`** to enter a mode where all built-in rules are bypassed. Every utterance is sent directly to the AI agent. Say **"exit chat"** or **"goodbye"** to return to normal command mode.

---

## Notes

- **LM Studio model compatibility** — not all GGUF models support tool calling. If the agent responds but never calls a tool, try a different model. Qwen2.5 is the most reliable for function calling at small sizes.
- **Gemini fallback** — if no `GEMINI_API_KEY` is set, Kareena will tell you when it can't reach LM Studio rather than crashing silently.
- **pywhatkit SSL error** — this library makes a network request at import time and may show an SSL warning on some Anaconda setups. It does not affect the rest of the assistant.
- **Memory** — stored in `src/.kareena_memory.json` and persists across sessions.
- **Screenshots** — saved as `.png` files in `src/` with a Unix timestamp as the filename.

---

## License

Open for personal and educational use. Attribution appreciated.
