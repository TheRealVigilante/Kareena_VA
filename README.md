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
- **Local AI Agent** — a ReAct-style tool-calling agent powered by a local LLM running in LM Studio (Spark X2.5 4B). The agent handles any command that doesn't match the hardcoded rules, and can also be invoked explicitly.
- **Gemini API fallback** — if LM Studio is not running, the agent automatically falls back to Google's `gemma-4-31b-it` model via the Gemini API.
- **MCP-style tools** — the agent has access to a suite of tools it can call autonomously: web search (DuckDuckGo), URL fetching, file read/write, time/timezone queries, and a persistent memory store.

---

## Project Structure

```
Rule-Based Chatbot VA/
├── main.py               # Entry point — launches the Toga app
├── KareenaApp.py         # Main Toga window (chat log, status, buttons)
├── assistant_core.py     # All voice assistant logic and the command loop
├── agent.py              # LLM agent — LM Studio primary, Gemini fallback
├── mcp_tools.py          # Agent tools: search, fetch, files, time, memory
├── NameApp.py            # Toga window — asks for the user's name at startup
├── PhoneBookApp.py       # Toga window — phonebook for WhatsApp contacts
├── TimerApp.py           # Toga window — countdown timer
├── StopWatchApp.py       # Toga window — stopwatch
├── data.txt              # Saved to-do notes
├── phonebook.json        # Saved contacts
├── .env.example          # Environment variable template (copy to .env)
└── requirements.txt      # All Python dependencies
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

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Open `.env` and set:

```env
# LM Studio — load "Spark X2.5 4B GGUF Q4_K_M" and start the local server
LM_STUDIO_BASE_URL=http://localhost:1234/v1
LM_STUDIO_API_KEY=lm-studio
LM_STUDIO_MODEL=spark-x2.5-4b

# Gemini API — get a free key at https://aistudio.google.com/apikey
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemma-4-31b-it
```

The Gemini key is optional but recommended as a fallback when LM Studio is not running.

### 5. Set up LM Studio (for the local agent)

1. Download and open [LM Studio](https://lmstudio.ai/)
2. Search for and download `Spark X2.5 4B GGUF Q4_K_M`
3. Go to **Local Server** → click **Start Server**
4. The server runs at `http://localhost:1234` by default

### 6. Run the assistant

```bash
conda run -n dawn python main.py
```

Or with the environment activated:

```bash
python main.py
```

---

## How It Works

Kareena starts by opening a native desktop window and asking for your name. After that, she greets you and begins listening for voice commands.

**Wake word:** every command must start with **"hello"**.

The command loop works in order:

1. Hardcoded rules are checked first (fast, offline, no LLM needed)
2. If you say **"hello agent ..."**, the agent is invoked directly
3. If nothing matches, the agent is used as a smart fallback

The agent runs a ReAct loop — it decides which tools to call, executes them, and synthesises a spoken answer. LM Studio is tried first; if it's unreachable, Gemini is used instead.

---

## Voice Command Reference

### Built-in commands

| Say this | What happens |
|---|---|
| `hello google` | Opens Google |
| `hello github` | Opens GitHub |
| `hello facebook` | Opens Facebook |
| `hello instagram` | Opens Instagram |
| `hello twitter` | Opens Twitter |
| `hello onedrive` | Opens OneDrive |
| `hello [site] website` | Opens `https://www.[site].com` |
| `hello from wikipedia search [topic]` | Reads a Wikipedia summary |
| `hello tell me your name` | Kareena introduces herself |
| `hello what time` | Tells the current time |
| `hello day` | Tells today's date |
| `hello weather` | Asks for a city then fetches weather |
| `hello youtube` | Asks what to play then opens YouTube |
| `hello message` | Opens phonebook → sends a WhatsApp message |
| `hello joke` | Tells a random programming joke |
| `hello to do` | Saves a to-do note |
| `hello saved` | Reads all saved to-dos |
| `hello clipboard` | Reads current clipboard content |
| `hello screenshot` | Takes a screenshot |
| `hello cpu` | Reports CPU usage |
| `hello timer` | Opens the countdown timer window |
| `hello stopwatch` | Opens the stopwatch window |
| `hello instructions` | Lists all available commands |
| `hello exit` | Says goodbye and closes the assistant |

### Agent commands

| Say this | What happens |
|---|---|
| `hello agent [any question]` | Sends the question directly to the AI agent |
| `hello agent` | Kareena asks what you need, then routes it |
| Any unrecognised command | Automatically falls back to the agent |

### Agent tool examples

The agent can use its tools autonomously. Some examples of what you can say:

```
"hello agent search for the latest news about Python 3.14"
"hello agent what time is it in Tokyo right now?"
"hello agent remember my favourite colour is blue"
"hello agent what do you remember about me?"
"hello agent fetch the content of https://example.com"
"hello agent write my shopping list to a file called shopping.txt"
"hello agent read the file data.txt"
```

---

## Agent Tools

The agent has access to the following tools, which it picks and calls automatically based on your request:

| Tool | Description |
|---|---|
| `duckduckgo_search` | Web search — no API key required |
| `fetch_url` | Fetches and reads the text content of any URL |
| `read_file` | Reads a file from the project directory |
| `write_file` | Writes text to a file in the project directory |
| `list_files` | Lists files in the project directory |
| `get_time` | Returns current date and time, supports any timezone |
| `remember` | Stores a key-value pair in persistent memory |
| `recall` | Retrieves a stored memory by key, or lists all memories |
| `forget` | Deletes a memory entry |

File access is sandboxed — the agent can only read and write inside the project folder.

---

## Notes

- The `pywhatkit` library makes a network request on import. If you see an SSL error on startup, this is a known issue with some Anaconda environments. It does not affect the rest of the assistant.
- The Gemini API is used only as a fallback. If you don't add a key, the agent will tell you when it can't reach LM Studio rather than crashing.
- Memory is stored in `.kareena_memory.json` in the project folder and persists across sessions.
- Screenshots are saved as `.png` files in the project folder with a timestamp as the filename.

---

## License

Open for personal and educational use. Attribution appreciated.
