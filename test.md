# Kareena VA - Test Guide

This document provides a comprehensive list of commands and features you can try to test all the capabilities of Kareena VA.

## 1. Built-in Commands (Fast, Offline)
Try saying these exact phrases:

- **"tell me your name"** (Kareena will introduce herself)
- **"what time"** (Tells the current time)
- **"day"** (Tells today's date)
- **"battery"** (Reports battery percentage and charging state)
- **"cpu"** (Reports CPU usage)
- **"calendar"** (Displays the current month's calendar)
- **"to do"** (Prompts you to save a to-do note)
- **"saved"** (Reads all saved to-dos)
- **"delete to do"** (Deletes a specific to-do note)
- **"timer"** (Opens the countdown timer window)
- **"stopwatch"** (Opens the stopwatch window)
- **"weather"** (Asks for a city, then fetches weather)
- **"joke"** (Tells a random programming joke)

## 2. Agent Commands (LLM Powered)
To test the ReAct agent, say "agent" followed by your request, or just speak naturally (unrecognised commands fall back to the agent).

**General Knowledge & Web Search (`duckduckgo_search`):**
- *"agent search for the latest news about Python 3.12"*
- *"agent who won the last Formula 1 race?"*

**Memory (`remember`, `recall`, `forget`):**
- *"agent remember my favourite colour is blue"*
- *"agent what do you remember about me?"*
- *"agent forget my favourite colour"*

**Timezones (`get_time`):**
- *"agent what time is it in Tokyo right now?"*

**File System (`read_file`, `write_file`, `list_files`):**
- *"agent list files in the project"*
- *"agent write a short poem to a file called poem.txt"*
- *"agent read the file poem.txt"*

**URL Fetching (`fetch_url`, `summarise_url`):**
- *"agent fetch the content of https://example.com"*
- *"agent summarise the url https://en.wikipedia.org/wiki/Python_(programming_language) focusing on history"*

## 3. Special Modes

**Chat Mode:**
Say **"chat"** to enter free-chat mode. You no longer need to say "agent" or wait for rule checks — every utterance goes directly to the AI.
When finished, say **"exit chat"** to return to normal mode.

**Voice Retry Loop:**
Try mumbling or staying silent when Kareena is listening. She should say "Attempt 2 of 3 — please try again" instead of silently dropping out.

## 4. GUI Features
- **Save Log:** Click the 💾 button to export your current conversation to your Desktop.
- **Stop/Start:** Use the 🔇 and 🎤 buttons to pause and resume the listening loop.
- **Startup Chime:** Listen for the chime right after you input your name at startup.
