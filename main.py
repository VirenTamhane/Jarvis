import speech_recognition as sr
from datetime import datetime
import playsound
import os
import random
import winshell
from gtts import gTTS
import webbrowser
import psutil
import requests
import win32api
import cv2
import subprocess
import wikipedia
import pyjokes

raw = sr.Recognizer()

def record_audio(ask=False):
    with sr.Microphone() as source:  # source is a variable in which user speech is stored
        if ask:
            bot_speak(ask)

        raw.adjust_for_ambient_noise(source)
        audio = raw.listen(source)

        try:
            voice_data = raw.recognize_google(audio)

        except sr.UnknownValueError:
            bot_speak("SORRY I DIDN'T GET THAT PLEASE TRY AGAIN")
            voice_data = record_audio()
            respond(voice_data)

        except sr.RequestError:
            bot_speak("SORRY MY SPEECH SERVICE IS DOWN")
        return voice_data


def bot_speak(audio_string):
    tts = gTTS(text=audio_string, lang='en')
    f_name = random.randint(1, 10000000)
    audio_file = 'audio-' + str(f_name) + '.mp3'
    tts.save(audio_file)
    playsound.playsound(audio_file)
    print(audio_string)
    os.remove(audio_file)


def respond(voice_data):
    salutation = {'hello': 'HI', 'hi': 'HELLO', 'how are you': 'I\'M FINE ', 'what is your name': 'ALEXA'}
    if voice_data in salutation:
        bot_speak(salutation[voice_data])

    if "what" and "time" in voice_data:
        now = datetime.now()
        bot_speak(now.strftime("%I:%M %p"))

    if "search" and ("web" or "internet") in voice_data:
        search = record_audio("WHAT DO YOU WANT TO SEARCH")
        url = "https://google.com/search?q=" + search
        webbrowser.get().open(url)
        bot_speak("HERE IS WHAT I FOUND FOR " + search)

    if "location" in voice_data:
        location = record_audio("WHAT LOCATION WOULD YOU LIKE TO SEARCH")
        url = "https://google.nl/maps/place/" + location + "/&amp;"
        webbrowser.get().open(url)
        bot_speak(" HERE IT IS ON GOOGLE MAP " + location)

    if ("battery" or "power") and ("status" or "source") in voice_data:
        battery = psutil.sensors_battery()
        bat_status = battery.power_plugged
        bat_percentage = str(battery.percent)
        status = "PLUGGED IN " + bat_percentage + " PERCENT CHARGED AND RUNNING " if bat_status else " DEVICE IS RUNNING ON BATTERY BACKUP CURRENTLY AT " + bat_percentage + " PERCENT "
        bot_speak(status)

    if "weather" in voice_data:
        city_name = record_audio("WHAT IS YOUR CITY")
        api_key = "35769c7f686c3686a4bbb5ae1c621052"
        complete_url = "http://api.openweathermap.org/data/2.5/weather?q={0}&appid={1}".format(city_name, api_key)
        api_link = requests.get(complete_url)
        api_data = api_link.json()
        temp = api_data["main"]
        temp1 = temp["temp"]
        temperature = str(int(int(temp1) - 273.15))
        weather_desc = api_data["weather"][0]["description"]
        bot_speak("TODAY'S TEMPERATURE IS " + temperature + " DEGREE CELSIUS AND WEATHER LOOKS " + weather_desc)

    if "CPU" and ("usage" or "status") in voice_data:
        usage = str(psutil.cpu_percent(4) / psutil.cpu_count())
        bot_speak("THE CURRENT CPU USAGE IS: " + usage + "PERCENT")

    if "enable" and "bluetooth" in voice_data:
        os.system("Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser")
        os.system("powershell -command ./bluetooth.ps1 -BluetoothStatus On")
        bot_speak("BLUETOOTH ENABLED")

    if "disable" and "bluetooth" in voice_data:
        os.system("Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser")
        os.system("powershell -command ./bluetooth.ps1 -BluetoothStatus Off")
        bot_speak('BLUETOOTH DISABLED')

    if "open" and "file" in voice_data:
        extensions = {"python": ".py", "text": ".txt", "executable": ".exe", "java": ".java", "image": ".jpg"}
        flag = 0
        drives = win32api.GetLogicalDriveStrings()
        drives = drives.split('\000')[:-1]
        search_file = record_audio("WHAT FILE DOU YOU WANT TO SEARCH")
        buff = search_file
        for extension in extensions:
            search_file = buff
            search_file = search_file + extensions[extension]
            print(search_file)
            bot_speak("SEARCHING")
            for drive in drives:
                listing = os.walk(drive)
                for root_path, directories, files in listing:
                    if search_file in files:
                        path = os.path.join(root_path, search_file)
                        bot_speak("FILE FOUND AT: " + path)
                        flag = 1
                        os.startfile(path)
                        break
        if flag == 0:
            bot_speak("FILE NOT FOUND AT: " + path)

    if "open" and "camera" in voice_data:
        cam = cv2.VideoCapture(0)
        capture_success = 0
        while capture_success == 0:
            ret, frame = cam.read()
            bot_speak("CAMERA OPENED")
            cv2.imshow("CAMERA", frame)
            task = record_audio()
            if capture_success == 1:
                break
            elif not ret:
                capture_success = 1
                break
            if "close" in task:
                cam.release()
                cv2.destroyAllWindows()
                capture_success = 1
                bot_speak("CLOSING CAMERA")
                break
            elif "capture" in task:
                file = record_audio("WHAT IS YOU/'R FILE NAME")
                file = file.lower()
                file = "E:/Python/" + file + ".jpg"
                cv2.imwrite(file, frame)
                bot_speak("CAPTURE SUCCESSFUL")
                capture_success = 1

    if "restart" in voice_data:
        bot_speak("RESTARTING DEVICE")
        subprocess.call(["shutdown", "/r"])

    if "shutdown" in voice_data:
        bot_speak("SHUTTING DOWN DEVICE IN 10 SECONDS")
        subprocess.call(["shutdown", "/s", "/t", "10"])

    if "wikipedia" in voice_data:
        search_var = record_audio("WHICH ARTICLE WOULD YOU LIKE TO OPEN ON WIKIPEDIA")
        bot_speak("OPENING WIKIPEDIA FOR ")
        bot_speak(search_var)
        webbrowser.get().open(wikipedia.page(search_var).url)
        bot_speak("HERE IS A SUMMARY FOR YOU")
        bot_speak(wikipedia.summary(search_var, 1))

    if "joke" in voice_data:
        bot_speak("HERE ARE SOME JOKES FOR YOU")
        bot_speak(pyjokes.get_joke())

    if "news" in voice_data:
        webbrowser.open('https://theprint.in/')
        bot_speak("HERE IS SOME NEWS FOR YOU")

    if "empty recycle bin" in voice_data:
        try:
            winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=True)
            bot_speak("RECYCLE BIN EMPTIED")
        except:
            bot_speak("RECYCLE BIN IS EMPTY")

    if "open" and "website" in voice_data:
        ser = record_audio("WHAT WEBSITE DO YOU WANT TO OPEN")
        ser = str(ser.lower()) + ".com"
        webbrowser.open(ser)

    if "open" and "mail" in voice_data:
        bot_speak("OPENING MAIL")
        webbrowser.open("www.gmail.com")

    if "open" and ("whatsapp" or "whatsapp web") in voice_data:
        bot_speak("OPENING WHATS APP")
        webbrowser.open("https://web.whatsapp.com")

    if "open" and "youtube" in voice_data:
        bot_speak("OPENING YOUTUBE")
        webbrowser.open("https://www.youtube.com/")

    if "open" and "github" in voice_data:
        bot_speak("OPENING GITHUB")
        webbrowser.open("https://github.com/")

    if "open" and "notepad" in voice_data:
        bot_speak("OPENING NOTEPAD")
        os.system("notepad.exe")

    if "exit" in voice_data:
        exit()

while 1:
    bot_speak("LISTENING")
    voice_data = record_audio()
    voice_data = voice_data.lower()
    print(voice_data)
    respond(voice_data)
