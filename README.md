# 🤖 Karina - Your Virtual Voice Assistant in Python

**Karina** is a voice-controlled virtual assistant built with Python that can perform a wide variety of tasks using voice commands — from telling jokes, weather reports, setting timers, searching Wikipedia, managing to-do lists, sending WhatsApp messages, and more!

---

## 🌟 Features

* 🗣️ Voice recognition and natural interaction
* 💬 Text-to-speech response (pyttsx3)
* 🌐 Web browsing and Wikipedia search
* 📩 WhatsApp messaging (via web)
* 📅 Tells current time and date
* ⛅ Fetches weather information for any city
* 📋 Reads from clipboard
* 😂 Tells random programming jokes
* 🧠 To-do note saving and reading
* 🧪 CPU usage monitoring
* ⏱️ Built-in stopwatch and timer (with GUI)
* 📸 Screenshot capturing
* 📂 Custom modules: `NameApp`, `PhoneBookApp`, `TimerApp`, `StopWatchApp`

---

## 🔧 Requirements

* Python 3.x
* Packages:

  ```bash
  pip install pyttsx3 speechrecognition pyautogui pyjokes wikipedia pywhatkit clipboard requests psutil colorama pyaudio
  ```

> 💡 `pyaudio` installation can be tricky on some systems. Use precompiled wheels or system package managers if needed.

---

## 🚀 How to Run

1. Clone/download the project and ensure all required modules (including `NameApp.py`, `PhoneBookApp.py`, etc.) are in the same directory.
2. Run the main file:

```bash
python main.py
```

3. Karina will ask for your name and greet you. Say "hello" to activate commands.

---

## 🧠 Activation Word

Say **"hello"** at the start of your command. It activates Karina’s listening logic.
Examples:

* `"hello play some music on youtube"`
* `"hello tell me a joke"`
* `"hello what is the weather"`

---

## 🎤 Example Voice Commands

| Task                 | Voice Command Example                         |
| -------------------- | --------------------------------------------- |
| Open Google          | "hello google"                                |
| Search on Wikipedia  | "hello from wikipedia search Albert Einstein" |
| Play a YouTube video | "hello play coding tutorials on youtube"      |
| Tell a joke          | "hello joke"                                  |
| Set a timer          | "hello timer"                                 |
| Use the stopwatch    | "hello stopwatch"                             |
| Read clipboard       | "hello clipboard"                             |
| CPU usage            | "hello cpu"                                   |
| Save to-do           | "hello to do"                                 |
| Show saved to-dos    | "hello saved"                                 |
| Take a screenshot    | "hello screenshot"                            |
| WhatsApp message     | "hello message"                               |
| Exit assistant       | "hello exit"                                  |

---

## 📁 File Structure

```
main.py                 # Main assistant script (Karina)
NameApp.py                   # Module for getting user's name
PhoneBookApp.py              # Module for retrieving phone numbers
TimerApp.py                  # Module for timer GUI
StopWatchApp.py              # Module for stopwatch GUI
data.txt                     # File to store to-do notes
```

---

## 🛠️ Customization Ideas

* Add hotkey activation (e.g., "Ctrl + Shift + K")
* Integrate with OpenAI or LLMs for smarter responses
* Add emotion/sentiment detection
* Improve speech recognition using deep learning
* Save user preferences/settings in a config file

---

## 🔐 Security Note

This assistant sends WhatsApp messages via the web client and reads from the clipboard. Avoid sharing personal/sensitive data.

---

## 📜 License

This project is open for educational and personal use. Attribution is appreciated.

---

## 👋 Final Note

Karina is a friendly and functional assistant for Python learners who want to mix voice interaction, automation, and Python GUI capabilities. Enhance her. Train her. Make her yours. 💡
