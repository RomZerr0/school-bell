import vlc
import time
import json
import threading
import datetime
import os

def init():
    global sound
    global sched
    global presoundalarm
    global lastsched
    global schedule
    global defaultsound
    global days
    global day
    global exp
    global current
    global volume
    volume = 0
    defaultsound = "default.mp3"
    sound = defaultsound
    presoundalarm = "presound.mp3"
    sched = importjson()
    days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    day = datetime.datetime.today().weekday()+1
    schedule = sched.get('schd'+str(day))
    print("Today is "+days[day-1])
    lastsched = os.stat("sched.json")[8]
    exp = sched.get('exeptions')
    print("Initialization completed!")
    

def importjson():
    global sched
    try:
        with open ("sched.json", "r") as schedfile:
            schedjson = schedfile.read().rstrip()
            sched = json.loads(schedjson)
        return sched
    except:
        print("Ошибка импорта JSON, файл не найден или что-то подобное.")

def play(sound, calllength):
    global volume
    try:
        p = vlc.MediaPlayer(sound)
        p.audio_set_volume(0) 
        volume = 0
        p.play()
        if volume == 0:
            for n in range(1, 101): #fadein
                p.audio_set_volume(n)
                volume = n               
                time.sleep(0.01)
        time.sleep(calllength-1)
        if volume > 50:
            for n in range(1, volume): #fadeout
                p.audio_set_volume(volume-n-1)
                volume = volume - n
                time.sleep(0.01)
        p.stop()
    except:
        print("Ошибка воспроизведения")

def playT(sound = "default.mp3", calllength = 30):
    global defaultsound
    if os.path.isfile(sound):
        try:
            thrd1 = threading.Thread(target = play, args = (sound, calllength)).start()
            print("Playing "+sound+" on thread 1 for "+str(calllength)+" seconds")
        except:
            print("Ошибка воспроизведения в отдельном потоке")
    else:
        print("Can't find "+sound+" playing default for "+str(calllength)+" seconds")
        try:
            sound = defaultsound
            thr1 = threading.Thread(target = play, args = (sound, calllength)).start()
        except:
            print("Ошибка воспроизведения в отдельном потоке")

def timecheck():
    for t in schedule:
        global current
        if t[0] == datetime.datetime.now().strftime("%H:%M:%S" ):
            current = t
            return(True)

def daycheck():
    global exp
    for t in exp:
        if t[0] == datetime.datetime.now().strftime("%H:%M:%S" ):
            if t[3] == datetime.datetime.now().strftime("%d/%m/%Y" ):
                time.sleep(1)
                return(True)

def mainLoop():
    global sched
    global schedule
    global lastsched
    global current
    global day
    global exp
    global volume
    while True: #Циклецикл
        if lastsched == os.stat("sched.json")[8]: #Если не менялся файл начинаем веселье
            dateSTR = datetime.datetime.now().strftime("%H:%M:%S" )
            if os.path.isfile("alarm.mp3"):
                try:
                    os.popen('copy alarm.mp3 play.mp3')
                    print(dateSTR+" PLAYING ALARM!")
                    time.sleep(1)
                    p = vlc.MediaPlayer("play.mp3")
                    p.audio_set_volume(100)
                    p.play()
                    os.remove("alarm.mp3")
                except:
                    print("Ошибка воспроизведения файла сообщения")
            elif timecheck():
                if daycheck() != True:
                    print(dateSTR+" its high noon!")
                    playT(current[1], int(current[2]))
                    time.sleep(1)
                else:
                    print(datetime.datetime.now().strftime("%d/%m/%Y" )+" "+dateSTR+" Not today!")
            elif dateSTR == "00:00:01":
                time.sleep(1)
                day = datetime.datetime.today().weekday()
                schedule = sched.get('schd'+str(day))
                print("Today is "+days[day-1])
            else:
                time.sleep(1) #Тикаем времечко
                print(dateSTR+" === "+str(volume), end="\r")
                pass
        else:
            try:
                sched = importjson()
                schedule = sched.get('schd'+str(day))
                exp = sched.get('exeptions')
                print(dateSTR+" JSON updated!")
                lastsched = os.stat("sched.json")[8]
            except:
                print("Ошибка при обновлении JSON файла")


init()
thread = threading.Thread(target = mainLoop, daemon = True)
thread.start()
while True:
    time.sleep(43200)
    init()
