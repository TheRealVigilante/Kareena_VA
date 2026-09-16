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
# Speech
# ---------------------------------------------------------------------------

def speak(audio):
    """Synthesise speech and log the text to the GUI."""
    _log_fn(f"Kareena: {audio}")
    engine = pyttsx3.init('sapi5')
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)
    engine.say(audio)
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
        "Exit — say 'exit'",
    ]
    for line in lines:
        _log_fn(line)
    speak("Here are some instructions to use me. Check the chat log for the full list.")


def intro():
    speak("Always say 'hello' to activate me — it is my wake word.")
    speak("Say 'instructions' to get a full list of commands.")


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

            elif "exit" in query:
                terminate()
                stop_event.set()

            else:
                q = query.replace("hello", "").strip()
                webbrowser.open(f"https://www.google.com/search?q={q}")
                speak(f"Here are the search results for {q}")

        except AttributeError:
            continue
