# assistant_core.py
# All stateless logic for Kareena VA.
# GUI callbacks are injected via set_gui_callbacks() so this module
# works whether run headless or through the Toga GUI.

import calendar
import datetime
import os
import re
import time as ti
import webbrowser
from time import sleep

import clipboard
import psutil
import pyautogui
import pyjokes
import pyttsx3
import requests
import speech_recognition as sr
import wikipedia
# pywhatkit does a network check on import, so we import it lazily
# inside the function that needs it to avoid startup failures.

import TimerApp
import StopWatchApp
import PhoneBookApp
import agent as _agent

# Conversation history for the agent — grows across calls within one session
_agent_history: list = []

# ---------------------------------------------------------------------------
# GUI callback hooks (injected by KareenaApp at startup)
# ---------------------------------------------------------------------------
_log_fn = print          # fn(text) — write a line to the chat log
_status_fn = print       # fn(text) — update the status label

def set_gui_callbacks(log_fn, status_fn):
    """Inject GUI callbacks so core functions can update the interface."""
    global _log_fn, _status_fn
    _log_fn = log_fn
    _status_fn = status_fn

# ---------------------------------------------------------------------------
# Shared state
# ---------------------------------------------------------------------------
user_name = ""

def set_user_name(name):
    global user_name
    user_name = name

# ---------------------------------------------------------------------------
# Output cleaning
# ---------------------------------------------------------------------------

def clean_for_speech(text: str) -> str:
    """
    Strip markdown and fix encoding so text sounds natural when spoken
    and displays correctly in the GUI.

    Handles:
    - Mojibake from UTF-8/Windows-1252 mismatch  (â€™ → ')
    - Markdown bold/italic  (**text** → text)
    - Markdown headers      (## Heading → Heading)
    - Markdown bullets      (- item → item)
    - Markdown code fences  (``` ... ```)
    - Excess blank lines
    """
    # ── Fix common mojibake sequences ────────────────────────────────────────
    replacements = {
        "\u00e2\u20ac\u2122": "'",    # â€™  right single quote
        "\u00e2\u20ac\u0153": '"',    # â€œ  left double quote
        "\u00e2\u20ac\x9d": '"',      # â€   right double quote
        "\u00e2\u20ac\u201c": "\u2014",  # â€"  em dash
        "\u00e2\u20ac\u201d": "\u2013",  # â€"  en dash
        "\u00e2\u20ac\xa2": "\u2022",    # â€¢  bullet
        "\u00e2\u20ac\xa6": "...",       # â€¦  ellipsis
        "\u00c3\xa9": "\u00e9",  # Ã©  e acute
        "\u00c3\xa8": "\u00e8",  # Ã¨  e grave
        "\u00c3\xa0": "\u00e0",  # Ã   a grave
        "\u00c3\xa2": "\u00e2",  # Ã¢  a circumflex
        "\u00c3\xae": "\u00ee",  # Ã®  i circumflex
        "\u00c3\xb4": "\u00f4",  # Ã´  o circumflex
        "\u00c3\xbb": "\u00fb",  # Ã»  u circumflex
        "\u00c3\xa7": "\u00e7",  # Ã§  c cedilla
        "\u00c3\xbc": "\u00fc",  # Ã¼  u umlaut
        "\u00c2\xb0": "\u00b0",  # Â°  degree sign
        "\u00c2\xa3": "\u00a3",  # Â£  pound sign
        "\u00c2\xa9": "(c)",     # Â©  copyright
        "\u00c2\xae": "(r)",     # Â®  registered
        "\u00e2\u0084\u00a2": "(tm)",  # â„¢  trademark
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)

    # Try re-encoding if mojibake is still present
    try:
        text = text.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass

    # Catch any remaining common stragglers after re-encode
    text = text.replace("\u00e2\u20ac\u201c", "\u2014")  # em dash
    text = text.replace("\u00e2\u20ac\u201d", "\u2013")  # en dash
    text = text.replace("\u00e2\u20ac\u2122", "'")       # right single quote
    # Replace dashes with a natural spoken pause
    text = text.replace("\u2014", ", ")   # em dash → comma pause
    text = text.replace("\u2013", " to ") # en dash → "to" (e.g. 2010-2020)

    # ── Strip markdown ────────────────────────────────────────────────────────
    # Code fences
    text = re.sub(r"```[\s\S]*?```", "", text)
    text = re.sub(r"`[^`]+`", "", text)
    # Headers (## Heading → Heading)
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    # Bold / italic
    text = re.sub(r"\*{1,3}([^*]+)\*{1,3}", r"\1", text)
    text = re.sub(r"_{1,3}([^_]+)_{1,3}", r"\1", text)
    # Bullet points (-, *, •) — replace with a pause comma
    text = re.sub(r"^\s*[-*•]\s+", "", text, flags=re.MULTILINE)
    # Numbered lists (1. item → item)
    text = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.MULTILINE)
    # Links [text](url) → text
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    # Horizontal rules
    text = re.sub(r"^[-*_]{3,}\s*$", "", text, flags=re.MULTILINE)
    # Collapse multiple blank lines into one
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


# ---------------------------------------------------------------------------
# Speech
# ---------------------------------------------------------------------------

def speak(audio: str) -> None:
    """Clean, log, and synthesise speech."""
    cleaned = clean_for_speech(audio)
    _log_fn(f"Kareena: {cleaned}")
    engine = pyttsx3.init('sapi5')
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)
    engine.say(cleaned)
    engine.runAndWait()

def takeCommand():
    """Listen for a voice command, update status, return the recognised text."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        _status_fn("Listening...")
        r.pause_threshold = 0.7
        audio = r.listen(source)
    try:
        _status_fn("Recognising...")
        query = r.recognize_google(audio, language='en')
        _log_fn(f"You: {query}")
        _status_fn("Idle")
        return query
    except Exception:
        _status_fn("Idle")
        speak("Say that again please.")
        return None

# ---------------------------------------------------------------------------
# Feature functions
# ---------------------------------------------------------------------------

def weather(city):
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    response = requests.get(
        base_url,
        params={"q": city, "appid": "977723de4debbc6500552a5c66cd941c", "units": "metric"}
    )
    if response.status_code == 200:
        data = response.json()
        current_temp = round(data['main']['temp'])
        feels_like = data['main']['feels_like']
        humidity = data['main']['humidity']
        description = data['weather'][0]['description']
        msg = (f"Current temperature in {city}: {current_temp}°C but feels like {feels_like}°C "
               f"with a current humidity of {humidity}%. {description} are the current weather condition.")
        _log_fn(f"Weather: {msg}")
        speak(msg)
    else:
        speak(f"Error retrieving weather information for {city}. Please try again.")


def sendWhatMsg():
    phone_number = PhoneBookApp.phone_main()
    try:
        speak("What is the message?")
        message = takeCommand()
        webbrowser.open("https://web.whatsapp.com/send?phone=" + phone_number + '&text=' + message)
        speak("Please wait, I am sending the message")
        sleep(10)
        pyautogui.press('enter')
        speak("Message sent")
    except Exception as e:
        _log_fn(f"Error: {e}")
        speak("Unable to send the message")


def url_exists(url):
    try:
        response = requests.get(url, timeout=5)
        return response.status_code // 100 == 2
    except requests.RequestException:
        return False


def getDate():
    now = datetime.datetime.now()
    my_date = datetime.datetime.today()
    weekday = calendar.day_name[my_date.weekday()]
    month_names = ['January','February','March','April','May','June',
                   'July','August','September','October','November','December']
    ordinals = ['1st','2nd','3rd','4th','5th','6th','7th','8th','9th','10th',
                '11th','12th','13th','14th','15th','16th','17th','18th','19th','20th',
                '21st','22nd','23rd','24th','25th','26th','27th','28th','29th','30th','31st']
    msg = f"Today is {weekday}, {month_names[now.month - 1]} the {ordinals[now.day - 1]}"
    _log_fn(msg)
    speak(msg)


def todo():
    speak("What is your to-do?")
    data = takeCommand()
    if data:
        data = data.title()
        speak(f"You told me to remember: {data}")
        with open("data.txt", "a", encoding="utf-8") as f:
            print(data, file=f)


def tellTime():
    now = datetime.datetime.now()
    msg = f"The time is {now.strftime('%H:%M')}"
    _log_fn(msg)
    speak(msg)


def greet():
    hour = datetime.datetime.now().hour
    if 6 <= hour < 12:
        speak(f"Good morning {user_name}, I hope you have a great day ahead")
    elif 12 <= hour < 18:
        speak(f"Good afternoon {user_name}, I hope you had a great lunch")
    elif 18 <= hour < 21:
        speak(f"Good evening {user_name}, I hope you had a great day")
    else:
        speak(f"Hello {user_name}, it is getting late — you should go to bed. However, I am always happy to help")


def terminate():
    hour = datetime.datetime.now().hour
    if hour >= 21 or hour < 6:
        speak(f"Good night {user_name}! Have a nice sleep")
    else:
        speak(f"Bye {user_name}, have a great day ahead")


def instructions():
    lines = [
        "Here are some things you can ask me:",
        "Search Wikipedia — say 'from wikipedia search ...'",
        "Open a website — say the site name followed by 'website', e.g. 'youtube website'",
        "Open Google, GitHub, OneDrive, Facebook, Instagram, Twitter",
        "Tell me your name — say 'tell me your name'",
        "What day is it — say 'day'",
        "What time is it — say 'what time'",
        "Play a YouTube video — say 'youtube'",
        "Send a WhatsApp message — say 'message'",
        "Get the weather — say 'weather'",
        "Read clipboard — say 'read my clipboard'",
        "Tell a joke — say 'joke'",
        "Save a to-do — say 'to do'",
        "Show saved to-dos — say 'saved'",
        "Take a screenshot — say 'screenshot'",
        "CPU usage — say 'cpu'",
        "Set a timer — say 'timer'",
        "Start a stopwatch — say 'stopwatch'",
        "Ask the AI agent anything — say 'agent' followed by your question",
        "Exit — say 'exit'",
    ]
    for line in lines:
        _log_fn(line)
    speak("Here are some instructions to use me. Check the chat log for the full list.")


def intro():
    speak("Always say 'hello' to activate me — it is my wake word.")
    speak("Say 'instructions' to get a full list of commands.")


def _run_agent(query: str) -> None:
    """Send *query* to the agent, speak and log the response."""
    global _agent_history
    _status_fn("Agent thinking...")
    _log_fn(f"[Agent] ← {query}")
    try:
        answer = _agent.run(query, conversation_history=_agent_history)
        # Keep last 10 turns in history so the agent has context
        _agent_history.append({"role": "user",      "content": query})
        _agent_history.append({"role": "assistant",  "content": answer})
        _agent_history = _agent_history[-20:]   # cap at 20 messages (10 turns)
        _log_fn(f"[Agent] → {answer}")
        speak(answer)
    except Exception as e:
        _log_fn(f"[Agent] Error: {e}")
        speak("Sorry, the agent ran into a problem. Please try again.")
    finally:
        _status_fn("Idle")


# ---------------------------------------------------------------------------
# Main query loop  (runs in a background thread)
# ---------------------------------------------------------------------------

def take_query(stop_event):
    """
    Main voice command loop.
    stop_event: threading.Event — set it to stop the loop gracefully.
    """
    while not stop_event.is_set():
        try:
            query = takeCommand()
            if not query:
                continue
            query = query.lower()

            if "hello" not in query:
                continue

            if "instructions" in query:
                instructions()

            elif "website" in query:
                q = re.sub(r'website|open|hello', '', query).strip().replace(' ', '')
                url = f"https://www.{q}.com"
                if url_exists(url):
                    speak(f"Opening {q}")
                    webbrowser.open(url)
                else:
                    speak(f"Sorry, I could not open that. Here are Google results for {q}")
                    webbrowser.open(f"https://www.google.com/search?q={q}")

            elif "google" in query:
                speak("Opening Google")
                webbrowser.open("https://www.google.com")

            elif "github" in query:
                speak("Opening GitHub")
                webbrowser.open("https://github.com")

            elif "onedrive" in query:
                speak("Opening OneDrive")
                webbrowser.open("https://onedrive.live.com/about/en-us/signin/")

            elif "facebook" in query:
                speak("Opening Facebook")
                webbrowser.open("https://www.facebook.com")

            elif "instagram" in query:
                speak("Opening Instagram")
                webbrowser.open("https://www.instagram.com")

            elif "twitter" in query:
                speak("Opening Twitter")
                webbrowser.open("https://www.twitter.com")

            elif "day" in query:
                getDate()

            elif "what time" in query:
                tellTime()

            elif "from wikipedia" in query:
                speak("Checking Wikipedia")
                q = re.sub(r'wikipedia|hello|from|search', '', query).strip()
                result = wikipedia.summary(q, sentences=3)
                _log_fn(f"Wikipedia: {result}")
                speak(f"According to Wikipedia: {result}")

            elif "tell me your name" in query:
                speak("I am Kareena, your virtual assistant")

            elif "message" in query:
                speak("Who do you want to send the message to?")
                sendWhatMsg()

            elif "youtube" in query:
                speak("What do you want to search on YouTube?")
                import pywhatkit
                pywhatkit.playonyt(takeCommand())

            elif "weather" in query:
                speak("Which city do you want the weather for?")
                city = takeCommand()
                if city:
                    weather(city)

            elif "clipboard" in query:
                content = clipboard.paste()
                _log_fn(f"Clipboard: {content}")
                speak(content)

            elif "joke" in query:
                joke = pyjokes.get_joke()
                _log_fn(f"Joke: {joke}")
                speak(joke)

            elif "to do" in query:
                todo()

            elif "saved" in query:
                if os.path.exists("data.txt"):
                    with open("data.txt", "r") as f:
                        content = f.read()
                    _log_fn(f"Saved to-dos:\n{content}")
                    speak(f"You told me to remember: {content}")
                else:
                    speak("You have no saved to-dos yet.")

            elif "screenshot" in query:
                speak("Taking a screenshot")
                pyautogui.screenshot(str(ti.time()) + ".png").show()

            elif "cpu" in query:
                usage = str(psutil.cpu_percent())
                _log_fn(f"CPU usage: {usage}%")
                speak(f"Your CPU is at {usage} percent")

            elif "timer" in query:
                speak("Opening the timer")
                TimerApp.timer_main()

            elif "stopwatch" in query:
                speak("Opening the stopwatch")
                StopWatchApp.stopwatch_main()

            elif "agent" in query:
                # Explicit agent invocation — strip wake words and pass rest to agent
                q = re.sub(r'\bhello\b|\bagent\b', '', query).strip()
                if not q:
                    speak("Sure, what would you like me to help with?")
                    q = takeCommand()
                    if not q:
                        continue
                _run_agent(q)

            elif "exit" in query:
                terminate()
                stop_event.set()

            else:
                # Nothing matched — pass to the agent as a smart fallback
                q = query.replace("hello", "").strip()
                _run_agent(q)

        except AttributeError:
            continue
