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
import tkinter as tk

#my own classes
import NameApp
import PhoneBookApp
import TimerApp
import StopWatchApp

user_name = ""


def speak(audio): # this method is used for speaking the audio
    engine = pyttsx3.init('sapi5')
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)
    engine.say(audio)
    engine.runAndWait()


# speak("before we start, please tell me what should i call you? ")
# user_name = NameApp.main_name_app()
user_name = "Deku"

def takeCommand(): # this method is used for taking command from the user
    r = sr.Recognizer()

    # from the speech_Recognition module we will use the Microphone module for listening the command
    with sr.Microphone() as source:
        print('Listening')

        # seconds of non-speaking audio before a phrase is considered complete.
        r.pause_threshold = 0.7
        audio = r.listen(source)

        # Now we will be using the try and except method so that if sound is recognized it is good else we will have
        # exception handling
        try:
            print("Recognizing")
            Query = r.recognize_google(audio, language='en')
            print("the command is printed=", Query)

        except Exception as e:
            print(e)
            print("Say that again please")
            speak("Say that again please.")
            Query = None

        return Query


def weather(city):  #editted by accepting paramter that will eventually store the city
    index = re.search("in ", city)  #finding the index number of the word "in "
    city = city[index.end():]
    res = requests.get(
        f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid=16f0afad2fd9e18b7aee9582e8ce650b&units=metric").json()
    temp1 = res["weather"][0]["description"]
    temp2 = res["main"]["temp"]
    print(f"Temperature is {format(temp2)} degree Celsius Weather is {format(temp1)}")
    speak(f"Temperature is {format(temp2)} degree Celsius Weather is {format(temp1)}")


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
        print(e)
        speak("Unable to send the Message")


def url_exists(url):
    try:
        response = requests.get(url)
        # Check if status code is in the range of successful responses (200-299)
        return response.status_code // 100 == 2
    except requests.RequestException as e:
        # Handle exceptions like network problems, invalid URLs, etc.
        print(f"An error occurred: {e}")
        return False

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
    print(f"Today is {weekday}, {month_names[monthNum - 1]} the {ordinalNumbers[dayNum - 1]}")


def todo():
    speak("What is your to-do list?")
    data = takeCommand().title()
    speak("You told me to remember this idea: " + data)
    with open("data.txt", "a", encoding="utf-8") as r:
        print(data, file=r)


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


def terminate():
    hours = datetime.datetime.now().hour
    if (hours >= 21) and (hours < 6):
        speak(f"Good Night {user_name}! Have a nice Sleep")
    else:
        speak(f"Bye {user_name}, Have a great day ahead")
    quit()


def tellTime():
    # This method will give the time
    time = str(datetime.datetime.now())

    # the time will be displayed  and then after slicing we can get time
    hour = time[11:13]
    min = time[14:16]
    print(f'The time is {hour}:{min}')
    speak(f'The time is {hour}:{min}')

def instructions():
    speak("Here are some instructions to use me:")
    speak("You can ask me to search anything on wikipedia but please phrase it as... 'from wikipedia search. x y z'")
    speak("You can ask me to open some websites like google, github, onedrive, facebook, instagram, twitter")
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


def intro():
    speak("Here are some instructions to use me, just in case: ")
    speak("Always say Hello to activate me. it is my activation word AND i will not answer you if you dont say hello so please dont forget")
    speak("I will try to help as much as I can, but if I am unable to help you, I will search it for you on google")

# greet()
# speak(f"I am Karina, your Virtual Assistant. How can I help you?")
# intro()
speak("Now please tell me your first command")


# this is where the fun start after you create every definition then here you specify all the word mapping you want
# to link with def, Then with while true we can make it a infinite loop on command
def Take_query():
    # This loop is infinite as it will take our queries continuously until and unless we  say bye to exit or
    # terminate program
    while True:

        try:
            query = takeCommand().lower() # Converting the query into lower case for better understanding
            if "hello" in query:
                if "instructions" in query:
                    instructions()
                    continue

                if "website" in query:
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
                    speak("Opening Google")
                    webbrowser.open("https://www.google.com")
                    continue

                elif "github" in query:
                    speak("Opening GitHub")
                    webbrowser.open("https://github.com")
                    continue

                elif "onedrive" in query:
                    speak("Opening onedrive")
                    webbrowser.open("https://onedrive.live.com/about/en-us/signin/")
                    continue

                elif "facebook" in query:
                    speak("Opening Facebook")
                    webbrowser.open("https://www.facebook.com")
                    continue

                elif "instagram" in query:
                    speak("Opening Insta gram")
                    webbrowser.open("https://www.instagram.com")
                    continue

                elif "twitter" in query:
                    speak("Opening Twitter")
                    webbrowser.open("https://www.twitter.com")
                    continue

                elif "day" in query:
                    getDate()
                    continue

                elif "what time" in query:
                    tellTime()
                    continue

                elif "from wikipedia" in query:

                    # if any one wants to have a information from wikipedia
                    print("Checking Wikipedia ")
                    speak("Checking Wikipedia ")
                    query = query.replace("wikipedia", "")
                    query = query.replace("hello", "")
                    query = query.replace("from", "")
                    query = query.replace("search", "")

                    # it will give the summary of 3 lines from wikipedia we can increase and decrease it also.
                    result = wikipedia.summary(query, sentences=3)
                    speak("According to wikipedia")
                    print(result)
                    speak(result)
                    continue

                elif "tell me your name" in query:
                    speak("I am Karina, your Virtual Assistant")
                    continue

                elif 'message' in query:
                    speak("Who do you want to send the message to?")
                    sendWhatMsg()
                    continue

                elif "youtube" in query:
                    speak("What do you want to search on Youtube?")
                    pywhatkit.playonyt(takeCommand())
                    continue

                elif 'weather' in query:
                    speak("In which city?")
                    weather(query)
                    continue

                elif "read my clipboard" in query:  # to read your current clipboard
                    print(clipboard.paste())
                    speak(clipboard.paste())
                    continue

                elif "joke" in query:
                    joke = pyjokes.get_joke()
                    print(joke)
                    speak(joke)
                    continue

                elif "to do" in query:
                    todo()
                    continue

                elif "saved" in query:
                    ideas = open("data.txt", "r")
                    speak(f"You told me to remember these to-do:\n{ideas.read()}")
                    continue

                elif "screenshot" in query:
                    speak("taking a screenshot.")
                    pyautogui.screenshot(str(ti.time()) + ".png").show()
                    continue

                elif "cpu" in query:
                    print(f" your Cpu is at {str(psutil.cpu_percent())} %")
                    speak(f" your Cpu is at {str(psutil.cpu_percent())} %")
                    continue

                elif "timer" in query:
                    speak("Please type in the amount of time in the form of hours then minutes then seconds?")
                    TimerApp.timer_main()
                    continue

                elif "stopwatch" in query:
                    speak("Just click start please")
                    StopWatchApp.stopwatch_main()
                    continue

                elif "exit" in query:
                    terminate()

                else:
                    query = query.replace("hello", "")
                    webbrowser.open(f"https://www.google.com/search?q= {query}")
                    speak(f"Here are the search results for {query}")
                    continue

        except AttributeError:
            continue


if __name__ == '__main__':
    clear = lambda: os.system('cls')
    clear()
    Take_query()
