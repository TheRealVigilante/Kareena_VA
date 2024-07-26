# Import necessary libraries
import calendar
import os
import re
import time as ti
import clipboard
from time import sleep

import pyaudio
import psutil
import pyautogui
import pyjokes
import pyttsx3
import pywhatkit

import requests
import speech_recognition as sr
import webbrowser
import datetime
import wikipedia
from colorama import Fore

# Import custom modules
import NameApp
import PhoneBookApp
import TimerApp
import StopWatchApp

user_name = ""

# Function to make the assistant speak
def speak(audio):
    engine = pyttsx3.init('sapi5')
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)
    engine.say(audio)
    engine.runAndWait()

# Function to take voice command from the user
def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print(Fore.GREEN + 'Listening')
        r.pause_threshold = 0.7
        audio = r.listen(source)
        try:
            print(Fore.BLUE + "Recognizing")
            Query = r.recognize_google(audio, language='en')
            print(Fore.LIGHTCYAN_EX + "the command is printed=", Query)
        except Exception as e:
            print(e)
            print(Fore.RED + "Say that again please")
            speak("Say that again please.")
            Query = None
        return Query

# Function to get weather information for a city
def weather(city):
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    response = requests.get(base_url, params={"q": city, "appid": "977723de4debbc6500552a5c66cd941c", "units": "metric"})
    if response.status_code == 200:
        data = response.json()
        current_temp = round(data['main']['temp'])
        feels_like = data['main']['feels_like']
        print(Fore.BLUE+f"Current temperature in {city}: {current_temp}°C but feels like {feels_like}°C with a current humidity "
              f"of {data['main']['humidity']}%")
        print(Fore.BLUE+f"{data['weather'][0]['description']} are the current weather condition.")
        speak(f"Current temperature in {city}: {current_temp}°C but feels like {feels_like}°C .. with a current humidity "
              f"of {data['main']['humidity']}%.. {data['weather'][0]['description']} are the current weather condition.")
    else:
        print(Fore.RED+f"Error retrieving weather information for {city}. Please try again.")

# Function to send a WhatsApp message
def sendWhatMsg():
    phone_number = PhoneBookApp.phone_main()
    try:
        speak("What is the message")
        message = takeCommand()
        webbrowser.open("https://web.whatsapp.com/send?phone=" + phone_number + '&text=' + message)
        speak("Please wait, I am sending the message")
        sleep(10)
        pyautogui.press('enter')
        speak("Message sent")
    except Exception as e:
        print(Fore.RED+e)
        speak("Unable to send the Message")

# Function to check if a URL exists
def url_exists(url):
    try:
        response = requests.get(url)
        return response.status_code // 100 == 2
    except requests.RequestException as e:
        print(Fore.RED+f"An error occurred: {e}")
        return False

# Function to get the current date
def getDate():
    now = datetime.datetime.now()
    my_date = datetime.datetime.today()
    weekday = calendar.day_name[my_date.weekday()]
    monthNum = now.month
    dayNum = now.day

    month_names = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
                   'November', 'December']

    ordinalNumbers = ['1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th', '10th', '11th', '12th', '13th',
                      '14th', '15th', '16th', '17th', '18th', '19th', '20th', '21st', '22nd', '23rd', '24th', '25th',
                      '26th', '27th', '28th', '29th', '30th', '31st']

    speak('Today is ' + weekday + ', ' + month_names[monthNum - 1] + ' the ' + ordinalNumbers[dayNum - 1])
    print(Fore.BLUE+f"Today is {weekday}, {month_names[monthNum - 1]} the {ordinalNumbers[dayNum - 1]}")

# Function to save a to-do item
def todo():
    speak("What is your to-do list?")
    data = takeCommand().title()
    speak("You told me to remember this idea: " + data)
    with open("data.txt", "a", encoding="utf-8") as r:
        print(Fore.BLUE+data, file=r)

# Function to greet the user based on the time of day
def greet():
    hour = datetime.datetime.now().hour
    if (hour >= 6) and (hour < 12):
        speak(f"Good Morning {user_name}, I hope you have a great day ahead")
    elif (hour >= 12) and (hour < 18):
        speak(f"Good afternoon {user_name}, I hope you had a great lunch")
    elif (hour >= 18) and (hour < 21):
        speak(f"Good Evening {user_name}, I hope you had a great day")
    else:
        speak(f"Hello {user_name}, It is getting late, you should go to bed; However, I am always happy to help you")

# Function to terminate the assistant
def terminate():
    hours = datetime.datetime.now().hour
    if (hours >= 21) and (hours < 6):
        speak(f"Good Night {user_name}! Have a nice Sleep")
    else:
        speak(f"Bye {user_name}, Have a great day ahead")
    quit()

# Function to tell the current time
def tellTime():
    time = str(datetime.datetime.now())
    hour = time[11:13]
    min = time[14:16]
    print(Fore.BLUE+f'The time is {hour}:{min}')
    speak(f'The time is {hour}:{min}')

# Function to provide instructions to the user
def instructions():
    instructions = [
        "Here are some instructions to use me:",
        "You can ask me to search anything on wikipedia but please phrase it as... 'from wikipedia search. x y z'",
        "You can ask me to open some websites like google, git hub, onedrive, facebook, insta gram, twitter",
        "Or you can ask me to open any website by saying website at the end like saying youtube website",
        "You can ask me to tell you my name, just say tell me your name",
        "You can ask me to tell you the day, just say day",
        "You can ask me to tell you the time, just say what time",
        "You can ask me to play something on youtube",
        "You can ask me to send a message to someone on whatsapp, just say message",
        "You can ask me to tell you the weather in a city, just say weather",
        "You can ask me to read your clipboard, just say read my clipboard",
        "You can ask me to tell you a joke, just say joke",
        "You can ask me to remember a to-do, just say to do",
        "You can ask me to show you your saved to-do, just say saved",
        "You can ask me to take a screenshot, just say screenshot",
        "You can ask me to tell you your cpu usage, just say cpu",
        "You can ask me to set a timer, just say timer",
        "You can ask me to start a stopwatch, just say stopwatch",
        "You can ask me to exit, just say exit"
    ]

    for instruction in instructions:
        print(Fore.BLUE+instruction)
    speak("Here are some instructions to use me:")
    speak("You can ask me to search anything on wikipedia but please phrase it as... 'from wikipedia search. x y z'")
    speak("You can ask me to open some websites like google, git hub, onedrive, facebook, insta gram, twitter")
    speak("Or you can ask me to open any website by saying website at the end like saying youtube website")
    speak("You can ask me to tell you my name, just say tell me your name")
    speak("You can ask me to tell you the day, just say day")
    speak("You can ask me to tell you the time, just say what time")
    speak("You can ask me to play something on youtube")
    speak("You can ask me to send a message to someone on whatsapp, just say message")
    speak("You can ask me to tell you the weather in a city, just say weather")
    speak("You can ask me to read your clipboard, just say read my clipboard")
    speak("You can ask me to tell you a joke, just say joke")
    speak("You can ask me to remember a to-do, just say to do")
    speak("You can ask me to show you your saved to-do, just say saved")
    speak("You can ask me to take a screenshot, just say screenshot")
    speak("You can ask me to tell you your cpu usage, just say cpu")
    speak("You can ask me to set a timer, just say timer")
    speak("You can ask me to start a stopwatch, just say stopwatch")
    speak("You can ask me to exit, just say exit")

# Function to introduce the assistant
def intro():
    speak("Here are some instructions to use me, just in case: ")
    speak("Always say Hello to activate me. it is my activation word AND i will not answer you if you dont say hello "
          "so please dont forget")
    speak("I will try to help as much as I can, but if I am unable to help you, I will search it for you on google")
    speak("Say Instructions to get a list of instructions on how to use me")

# Function to take and process user queries
def Take_query():
    while True:
        try:
            query = takeCommand().lower()
            if "hello" in query:
                if "instructions" in query:
                    # Provide instructions to the user
                    instructions()
                    continue

                if "website" in query:
                    # Open a specified website
                    query = query.replace("website", "")
                    query = query.replace("open", "")
                    query = query.replace("hello", "")
                    query = query.replace(" ", "")
                    url = f"https://www.{query}.com"
                    if url_exists(url):
                        speak(f"Opening {query}")
                        webbrowser.open(url)
                    else:
                        speak(f"Sorry I can not open it for you so here is google search results for {query}")
                        webbrowser.open(f"https://www.google.com/search?q={query}")
                    continue

                if "google" in query:
                    # Open Google
                    speak("Opening Google")
                    webbrowser.open("https://www.google.com")
                    continue

                elif "github" in query:
                    # Open GitHub
                    speak("Opening GitHub")
                    webbrowser.open("https://github.com")
                    continue

                elif "onedrive" in query:
                    # Open OneDrive
                    speak("Opening onedrive")
                    webbrowser.open("https://onedrive.live.com/about/en-us/signin/")
                    continue

                elif "facebook" in query:
                    # Open Facebook
                    speak("Opening Facebook")
                    webbrowser.open("https://www.facebook.com")
                    continue

                elif "instagram" in query:
                    # Open Instagram
                    speak("Opening Insta gram")
                    webbrowser.open("https://www.instagram.com")
                    continue

                elif "twitter" in query:
                    # Open Twitter
                    speak("Opening Twitter")
                    webbrowser.open("https://www.twitter.com")
                    continue

                elif "day" in query:
                    # Tell the current date
                    getDate()
                    continue

                elif "what time" in query:
                    # Tell the current time
                    tellTime()
                    continue

                elif "from wikipedia" in query:
                    # Search and read a summary from Wikipedia
                    print(Fore.BLUE+"Checking Wikipedia ")
                    speak("Checking Wikipedia ")
                    query = query.replace("wikipedia", "")
                    query = query.replace("hello", "")
                    query = query.replace("from", "")
                    query = query.replace("search", "")
                    result = wikipedia.summary(query, sentences=3)
                    speak("According to wikipedia")
                    print(Fore.BLUE+result)
                    speak(result)
                    continue

                elif "tell me your name" in query:
                    # Tell the assistant's name
                    speak("I am Karina, your Virtual Assistant")
                    continue

                elif 'message' in query:
                    # Send a WhatsApp message
                    speak("Who do you want to send the message to?")
                    sendWhatMsg()
                    continue

                elif "youtube" in query:
                    # Search and play a video on YouTube
                    speak("What do you want to search on Youtube?")
                    pywhatkit.playonyt(takeCommand())
                    continue

                elif 'weather' in query:
                    # Get weather information for a specified city
                    speak("Please write on the terminal which city you want the weather for:")
                    weather(city= input(Fore.YELLOW+ "Enter the city name: "))

                elif "clipboard" in query:
                    # Read the current clipboard content
                    print(Fore.BLUE+clipboard.paste())
                    speak(clipboard.paste())
                    continue

                elif "joke" in query:
                    # Tell a joke
                    joke = pyjokes.get_joke()
                    print(Fore.BLUE+joke)
                    speak(joke)
                    continue

                elif "to do" in query:
                    # Save a to-do item
                    todo()
                    continue

                elif "saved" in query:
                    # Read saved to-do items
                    ideas = open("data.txt", "r")
                    speak(f"You told me to remember these to-do:\n{ideas.read()}")
                    continue

                elif "screenshot" in query:
                    # Take a screenshot
                    speak("taking a screenshot.")
                    pyautogui.screenshot(str(ti.time()) + ".png").show()
                    continue

                elif "cpu" in query:
                    # Tell the current CPU usage
                    print(Fore.BLUE+f"your Cpu is at {str(psutil.cpu_percent())} %")
                    speak(f"your Cpu is at {str(psutil.cpu_percent())} %")
                    continue

                elif "timer" in query:
                    # Set a timer
                    speak("Please type in the amount of time in the form of hours then minutes then seconds?")
                    TimerApp.timer_main()
                    continue

                elif "stopwatch" in query:
                    # Start a stopwatch
                    speak("Just click start please")
                    StopWatchApp.stopwatch_main()
                    continue

                elif "exit" in query:
                    # Terminate the assistant
                    terminate()

                else:
                    # Perform a Google search for the query
                    query = query.replace("hello", "")
                    webbrowser.open(f"https://www.google.com/search?q= {query}")
                    speak(f"Here are the search results for {query}")
                    continue

        except AttributeError:
            continue


if __name__ == '__main__':
    clear = lambda: os.system('cls')
    clear()
    speak("before we start, please tell me what should I call you")
    user_name = NameApp.main_name_app()
    greet()
    speak("I am your Virtual Assistant, Karina, How can I help you")
    intro()
    speak("Now, Please tell me your first command")
    Take_query()
