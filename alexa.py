import speech_recognition as sr
import pyttsx3
import pywhatkit
import datetime
import wikipedia
import pyjokes
import schedule
import time
import threading
import json
import spacy
import requests
import os
import re  # for regex parsing time from commands

# ----------------------------
# Setup
# ----------------------------
listener = sr.Recognizer()
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

DATA_FILE = "data.json"

# ----------------------------
# Storage
# ----------------------------
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"reminders": [], "alarms": [], "shopping_list": []}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

data = load_data()
reminders = data["reminders"]
alarms = data["alarms"]
shopping_list = data["shopping_list"]

# ----------------------------
# Context + User
# ----------------------------
context_memory = {}
def update_context(intent, entities):
    context_memory["intent"] = intent
    context_memory["entities"] = entities

user = "default user"

# ----------------------------
# NLP
# ----------------------------
nlp = spacy.load("en_core_web_sm")

def parse_command(command: str):
    doc = nlp(command)
    intent = None
    entities = []

    if "play" in command:
        intent = "play"
    elif "time" in command:
        intent = "time"
    elif "weather" in command:
        intent = "weather"
    elif "news" in command:
        intent = "news"
    elif "remind" in command or "reminder" in command:
        intent = "reminder"
    elif "alarm" in command and ("dismiss" in command or "stop" in command or "cancel" in command):
        intent = "alarm_dismiss"
    elif "alarm" in command:
        intent = "alarm"
    elif "shopping" in command and "add" in command:
        intent = "shopping_add"
    elif "shopping" in command and "list" in command:
        intent = "shopping_read"
    elif "joke" in command:
        intent = "joke"
    elif "who is" in command or "information about" in command or "tell me about" in command:
        intent = "who"
    elif "stop" in command or "exit" in command or "quit" in command:
        intent = "stop"
    else:
        intent = "unknown"

    for ent in doc.ents:
        entities.append({"text": ent.text, "label": ent.label_})

    return {"intent": intent, "entities": entities}

# ----------------------------
# Talking Function
# ----------------------------
def talk(text):
    print("Assistant:", text)
    engine.say(text)
    engine.runAndWait()

# ----------------------------
# Features
# ----------------------------
def set_reminder(task, reminder_time):
    reminders.append((task, reminder_time))
    save_data({"reminders": reminders, "alarms": alarms, "shopping_list": shopping_list})
    talk(f"Reminder set for {reminder_time}: {task}")

def set_alarm(alarm_time):
    alarms.append(alarm_time)
    save_data({"reminders": reminders, "alarms": alarms, "shopping_list": shopping_list})
    talk(f"Alarm set for {alarm_time}")

def dismiss_alarms(command=""):
    # If user specifies a time, remove that alarm
    time_match = re.search(r"(\d{1,2}(:\d{2})?\s?(AM|PM)?)", command, re.IGNORECASE)
    if time_match:
        alarm_time = time_match.group(0).upper()
        if alarm_time in alarms:
            alarms.remove(alarm_time)
            save_data({"reminders": reminders, "alarms": alarms, "shopping_list": shopping_list})
            talk(f"Alarm {alarm_time} dismissed.")
        else:
            talk(f"No alarm set for {alarm_time}.")
    else:
        if alarms:
            alarms.clear()
            save_data({"reminders": reminders, "alarms": alarms, "shopping_list": shopping_list})
            talk("All alarms dismissed.")
        else:
            talk("You have no alarms set.")

def add_to_shopping(item):
    shopping_list.append(item)
    save_data({"reminders": reminders, "alarms": alarms, "shopping_list": shopping_list})
    talk(f"Added {item} to your shopping list.")

def read_shopping():
    if shopping_list:
        talk("Your shopping list: " + ", ".join(shopping_list))
    else:
        talk("Your shopping list is empty.")

def get_weather(city):
    api_key = "41fe9468a47119af37c50361460fab85"
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            temp = data['main']['temp']
            desc = data['weather'][0]['description']
            talk(f"The weather in {city} is {desc} with a temperature of {temp}°C.")
        else:
            talk("Sorry, I could not get the weather information.")
    except Exception as e:
        talk(f"Error fetching weather: {e}")

def get_news():
    api_key = "79c061922cfd4dfbb971998937e5c67a"
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            articles = data["articles"][:5]
            for article in articles:
                talk(article["title"])
        else:
            talk("Sorry, I could not fetch the news.")
    except Exception as e:
        talk(f"Error fetching news: {e}")

# ----------------------------
# Scheduler
# ----------------------------
def check_reminders():
    now = datetime.datetime.now().strftime("%I:%M %p")
    for task, reminder_time in reminders:
        if now == reminder_time:
            talk(f"Reminder: {task}")

def check_alarms():
    now = datetime.datetime.now().strftime("%I:%M %p")
    for alarm_time in alarms:
        if now == alarm_time:
            talk(f"Alarm! {alarm_time}")

schedule.every(1).minute.do(check_reminders)
schedule.every(1).minute.do(check_alarms)

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

threading.Thread(target=run_scheduler, daemon=True).start()

# ----------------------------
# Main Function
# ----------------------------
def run_alexa():
    while True:
        command = take_command()
        if not command:
            continue
        intent_result = parse_command(command)
        intent = intent_result["intent"]
        entities = intent_result["entities"]
        update_context(intent, entities)

        if intent == "play":
            talk(f"Playing {command.replace('play', '')}")
            pywhatkit.playonyt(command.replace("play", ""))

        elif intent == "time":
            now = datetime.datetime.now().strftime("%I:%M %p")
            talk("Current time is " + now)

        elif intent == "who":
            if "who is" in command:
                person = command.replace("who is", "").strip()
            elif "information about" in command:
                person = command.replace("give me some information about", "").strip()
            elif "tell me about" in command:
                person = command.replace("tell me about", "").strip()
            else:
                person = command
            try:
                info = wikipedia.summary(person, 1)
                talk(info)
            except Exception:
                talk("Sorry, I couldn’t find information.")

        elif intent == "joke":
            talk(pyjokes.get_joke())

        elif intent == "reminder":
            set_reminder("some task", "10:00 AM")  # placeholder

        elif intent == "alarm":
            set_alarm("10:05 AM")  # placeholder

        elif intent == "alarm_dismiss":
            dismiss_alarms(command)

        elif intent == "shopping_add":
            add_to_shopping("milk")  # placeholder

        elif intent == "shopping_read":
            read_shopping()

        elif intent == "weather":
            city = next((e["text"] for e in entities if e["label"] == "GPE"), None)
            if not city:
                # fallback to word after "in"
                if "in" in command:
                    words = command.split()
                    try:
                        in_index = words.index("in")
                        if in_index + 1 < len(words):
                            city = words[in_index + 1]
                    except:
                        pass
            if city:
                get_weather(city)
            else:
                talk("Please specify a city for the weather.")

        elif intent == "news":
            get_news()

        elif intent == "stop":
            talk("Goodbye!")
            break

        else:
            talk("Please say the command again.")
            
# ----------------------------
# Speech Recognition
# ----------------------------
def take_command():
    try:
        with sr.Microphone() as source:
            print("Listening...")
            voice = listener.listen(source)
            command = listener.recognize_google(voice)
            print("You said:", command)
            return command.lower()
    except Exception as e:
        print("Speech error:", e)
        return ""

# ----------------------------
# Run
# ----------------------------
if __name__ == "__main__":
    try:
        run_alexa()
    except KeyboardInterrupt:
        talk("Goodbye!")
