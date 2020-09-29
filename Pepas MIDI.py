"""
Pepas MIDI
Secuenciador aleatorio de notas musicales
Autor: Andres Chouhy
"""

# Por alguna razon, algunas notas quedan colgadas hasta que se las llama nuevamente, sucede al activar mas de una voz en simultaneo y mas de una octava de amplitud.

print("Pepas MIDI v0.00.003")
print("Cargando...")

import curses
import time
import threading
import rtmidi
import keyboard
import random
import math
import pathlib

bpm = 160 # F1: tempo, en BMP
probabilidad = 1.0 # F2: probabilidad de ejecucion de nota, 0: nunca, 1: siempre
cantVoces = 1 # F3: cantidad de voces simultaneas
stepsDiv = 1 # F4: cantidad de steps por beat
stepDuracion = 1.0 # F5: duracion de la nota relativa a la duracion del step
stepsCant = 4 # F6: cantidad de steps en las secuencias fijas
probMutacion = 0.0 # F7: probabilidad de mutacion de secuencias fijas, 0: no muta, 1: muta completamente
ampOct = 0 # F8: amplitud de octavas, las voces se distribuyen a lo largo de esta cantidad de octavas, valores aceptados 1-5
velRange = (127,127) # F9: rango de variacion en la intensidad de ejecucion de las notas, valores aceptados 1-127
delay = 0.0 # F10: retraso relativo de tiempo entre cada voz, esto genera que 2 o mas notas simultaneas se ejecuten con una minima diferencia de tiempo
secuenciar = False # BARRA ESPACIADORA: modo secuencia fija
octava = -2 # FLECHAS ARRIBA Y ABAJO: octava master

escala = []
secuencias = []
stepActual = 1
holdMode = False
controlando = False
controlCantVoces = False
controlBPM = False
proxCantVoces = cantVoces
maxVoces = 10
proxBPM = bpm
controlProb = False
controlStepsDiv = False
controlStepsDur = False
controlStepsCant = False
proxStepsCant = stepsCant
controlProbMut = False
controlAmpOct = False
proxAmpOct = ampOct
controlVelRange = False
controlDelay = False
controlGuardarPreset = False
controlCargarPreset = False
play = False
start = False
clockDiv = 24.0
presetPath = str(pathlib.Path(__file__).parent.absolute()) + "/presets.txt"

midiout = rtmidi.MidiOut()
available_ports = midiout.get_ports()

if available_ports:
	midiout.open_port(5)
else:
	midiout.open_virtual_port("Pepas MIDI")

def mapKeyToMIDI(k):
        dic = {
                "z": 60,
                "s": 61,
                "x": 62,
                "d": 63,
                "c": 64,
                "v": 65,
                "g": 66,
                "b": 67,
                "h": 68,
                "n": 69,
                "j": 70,
                "m": 71,
                ",": 72,
                "l": 73,
                ".": 74,
                ";": 75,
                "/": 76,
                "q": 72,
                "2": 73,
                "w": 74,
                "3": 75,
                "e": 76,
                "r": 77,
                "5": 78,
                "t": 79,
                "6": 80,
                "y": 81,
                "7": 82,
                "u": 83,
                "i": 84,
                "9": 85,
                "o": 86,
                "0": 87,
                "p": 88
                }
        return dic.get(k, None)

def mapKeyToNum(k):
        dic = {
                "1": 1.0,
                "2": 2.0,
                "3": 3.0,
                "4": 4.0,
                "5": 5.0,
                "6": 6.0,
                "7": 7.0,
                "8": 8.0,
                "9": 9.0,
                "0": 10.0,
                "q": 0.0,
                "w": 0.1,
                "e": 0.2,
                "r": 0.3,
                "t": 0.4,
                "y": 0.5,
                "u": 0.6,
                "i": 0.7,
                "o": 0.8,
                "p": 0.9,
                }
        return dic.get(k.name, None)

def noteOn(key):
        midiout.send_message([0x90, mapKeyToMIDI(key[0]) + key[1]*12, key[2]])

def noteOff(key):
        midiout.send_message([0x80, mapKeyToMIDI(key[0]) + key[1]*12, key[2]])

def programarOn(nota):
        global notasAApagar
        noteOn(nota)
        notasAApagar.append(nota)
        t = threading.Timer(60/bpm/stepsDiv*stepDuracion + d, programarOff, [nota])
        t.start()

notasAApagar = []
def programarOff(nota):
        for i,val in enumerate(notasAApagar):
                if val[0] == nota[0]:
                        del notasAApagar[i]
                        break
        if notasAApagar.count(nota) == 0:
                noteOff(nota)

def translate(value, leftMin, leftMax, rightMin, rightMax):
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin
    valueScaled = float(value - leftMin) / float(leftSpan)
    return rightMin + (valueScaled * rightSpan)

def guardarPreset(_i):
        global presetPath, escala, secuencias, bpm, probabilidad, cantVoces, stepsDiv, stepDuracion, stepsCant, probMutacion, ampOct, velRange, delay
        try: presetFile = open(presetPath, "r")
        except: presetFile = open(presetPath, "w")
        try: lineas = presetFile.readlines()
        except: lineas = [""]
        presetFile.close()
        
        if _i >= 1: i = int(_i)
        else: i = int(((_i+.1)*10)+10)
        
        escalaEstado = False
        secuenciasEstado = False
        if len(escala) > 0: escalaEstado = True
        if len(secuencias) > 0: secuenciasEstado = True
        p = {"preset": i,
             "escala": (escalaEstado, escala),
             "secuencias": (secuenciasEstado, secuencias),
             "tempo": (True, bpm),
             "probabilidad": (True, probabilidad),
             "cantVoces": (True, cantVoces),
             "stepsDiv": (True, stepsDiv),
             "stepDuracion": (True, stepDuracion),
             "stepsCant": (True, stepsCant),
             "probMutacion": (True, probMutacion),
             "ampOct": (True, ampOct),
             "velRange": (True, velRange),
             "delay": (True, delay)}
        p = str(p)
        if len(lineas) <= i: lineas[-1] += "\n"
        while len(lineas) <= i-1: lineas.append("\n")
        if len(lineas) > i: p += "\n"
        lineas[i-1] = p
        presetFile = open(presetPath, "w")
        presetFile.writelines(lineas)
        presetFile.close()

def cargarPreset(_i):
        global presetPath, escala, secuencias, bpm, probabilidad, cantVoces, stepsDiv, stepDuracion, stepsCant, probMutacion, ampOct, velRange, delay
        try: presetFile = open(presetPath, "r")
        except:
                print("Archivo de presets inexistente")
                return
        lineas = presetFile.readlines()
        presetFile.close()

        if _i >= 1: i = int(_i)
        else: i = int(((_i+.1)*10)+10)

        if len(lineas) > i:
                p = eval(lineas[i-1])
                """try: p = eval(lineas[i-1])
                except:
                        print("Preset invalido")
                        return"""
        else:
                print("Preset inexistente")
                return

        if p.get("tempo")[0] == True: bpm = p.get("tempo")[1]
        #if p.get("tempo")[0] == True: bpm = p.get("tempo")[1]
        #if p.get("tempo")[0] == True: bpm = p.get("tempo")[1]
        #if p.get("tempo")[0] == True: bpm = p.get("tempo")[1]
        #if p.get("tempo")[0] == True: bpm = p.get("tempo")[1]
        #if p.get("tempo")[0] == True: bpm = p.get("tempo")[1]
        #if p.get("tempo")[0] == True: bpm = p.get("tempo")[1]
        #if p.get("tempo")[0] == True: bpm = p.get("tempo")[1]
        #if p.get("tempo")[0] == True: bpm = p.get("tempo")[1]
        #if p.get("tempo")[0] == True: bpm = p.get("tempo")[1]

presionadas = []
def presionando(key):
        global controlando, controlCantVoces, cantVoces, proxCantVoces, controlBPM, proxBPM, bpm, controlProb, probabilidad, controlStepsDiv, stepsDiv, controlStepsDur, stepDuracion, controlStepsCant, stepsCant, proxStepsCant, controlProbMut, probMutacion, controlAmpOct, proxAmpOct, controlVelRange, velRange, controlDelay, delay, controlGuardarPreset, controlCargarPreset
        if key.name not in presionadas:
                presionadas.append(key.name)
                if mapKeyToMIDI(key.name) is not None and controlando == False:
                        if ((holdMode == True) and (len(presionadas) == 1)):
                                global escala
                                escala.clear()
                        escala.append(key.name)
                if mapKeyToNum(key) is not None and controlando == True:
                        if controlBPM == True: proxBPM.append(int(mapKeyToNum(key)%10))
                        if controlProb == True: probabilidad = mapKeyToNum(key)/10.0
                        if controlCantVoces == True: proxCantVoces = int(mapKeyToNum(key))
                        if controlStepsDiv == True:
                                if mapKeyToNum(key) >= 1.0:
                                        stepsDiv = mapKeyToNum(key)
                                else:
                                        stepsDiv = 1.0/((mapKeyToNum(key)+0.1)*10.0)
                        if controlStepsDur == True: stepDuracion = mapKeyToNum(key)
                        if controlStepsCant == True: proxStepsCant.append(int(mapKeyToNum(key)%10))
                        if controlProbMut == True: probMutacion = mapKeyToNum(key)/10.0
                        if controlAmpOct == True: proxAmpOct = int(min(mapKeyToNum(key),5))
                        if controlVelRange == True:
                                if mapKeyToNum(key) < 1.0:
                                        v = int(translate(mapKeyToNum(key), 0.0, 0.9, 1, 127))
                                        velRange = (v, max(velRange[1], v))
                                else:
                                        v = int(translate(mapKeyToNum(key), 1.0, 10.0, 1, 127))
                                        velRange = (min(velRange[0], v), v)
                        if controlDelay == True: delay = mapKeyToNum(key)/10.0
                        if controlGuardarPreset: guardarPreset(mapKeyToNum(key))
                        if controlCargarPreset: cargarPreset(mapKeyToNum(key))
                if key.name == "f1":
                        proxBPM = []
                        controlBPM = True
                        controlando = True
                if key.name == "f2":
                        controlProb = True
                        controlando = True
                if key.name == "f3":
                        controlCantVoces = True
                        controlando = True
                if key.name == "f4":
                        controlStepsDiv = True
                        controlando = True
                if key.name == "f5":
                        controlStepsDur = True
                        controlando = True
                if key.name == "f6":
                        proxStepsCant = []
                        controlStepsCant = True
                        controlando = True
                if key.name == "f7":
                        controlProbMut = True
                        controlando = True
                if key.name == "f8":
                        controlAmpOct = True
                        controlando = True
                if key.name == "f9":
                        controlVelRange = True
                        controlando = True
                if key.name == "f10":
                        controlDelay = True
                        controlando = True
                if key.name == "f11":
                        controlGuardarPreset = True
                        controlando = True
                if key.name == "f12":
                        controlCargarPreset = True
                        controlando = True

def soltando(key):
        global controlando, controlCantVoces, cantVoces, proxCantVoces, controlBPM, proxBPM, bpm, controlProb, controlStepsDiv, controlStepsDur, controlStepsCant, proxStepsCant, stepsCant, controlProbMut, controlAmpOct, controlVelRange, controlDelay, controlGuardarPreset, controlCargarPreset
        if key.name in presionadas:
                presionadas.remove(key.name)
                if mapKeyToMIDI(key.name) and controlando == False:
                        if not holdMode:
                                for i in escala:
                                        if i.name == key: escala.remove(i)
                if key.name == "f1":
                        b = sum(d * 10**i for i, d in enumerate(proxBPM[::-1]))
                        if b > 0: bpm = b
                        controlBPM = False
                        controlando = False
                if key.name == "f2":
                        controlProb = False
                        controlando = False
                if key.name == "f3":
                        controlCantVoces = False
                        controlando = False
                if key.name == "f4":
                        controlStepsDiv = False
                        controlando = False
                if key.name == "f5":
                        controlStepsDur = False
                        controlando = False
                if key.name == "f6":
                        s = sum(d * 10**i for i, d in enumerate(proxStepsCant[::-1]))
                        if s > 0: stepsCant = s
                        resetearSecuencia(None)
                        controlStepsCant = False
                        controlando = False
                if key.name == "f7":
                        controlProbMut = False
                        controlando = False
                if key.name == "f8":
                        controlAmpOct = False
                        controlando = False
                if key.name == "f9":
                        controlVelRange = False
                        controlando = False
                if key.name == "f10":
                        controlDelay = False
                        controlando = False
                if key.name == "f11":
                        controlGuardarPreset = False
                        controlando = False
                if key.name == "f12":
                        controlCargarPreset = False
                        controlando = False

def octavaSubir(key):
        global octava
        octava = min(octava + 1, 4)

def octavaBajar(key):
        global octava
        octava = max(octava - 1, -5)

def salir(k):
        print("Chau!")
        global corriendo
        corriendo=False

def toggleHold(k):
        global holdMode
        holdMode = not holdMode
        if holdMode == False:
                global escala
                escala.clear()

def toggleSecuencia(k):
        global secuenciar
        secuenciar = not secuenciar
        if secuenciar == True:
                resetearSecuencia(k)

def resetearSecuencia(k):
        global secuencia, stepActual
        stepActual = 0
        secuencias.clear()
        for v in range(maxVoces):
                secuencias.append(list())
                for i in range(stepsCant):
                        if random.random() <= probabilidad: s = True
                        else: s = False
                        secuencias[v].append(((random.randint(0, 256)), s, random.randint(velRange[0],velRange[1])))

def mutar(step):
        if random.random() <= probMutacion:
                for v in range(maxVoces):
                        if random.random() <= probabilidad: s = True
                        else: s = False
                        sec = secuencias[v]
                        sec[step] = ((random.randint(0, 256)), s, random.randint(velRange[0],velRange[1]))

def startStopClock(k):
        global start, play
        if play == False:
                start = True
                play = True
        else:
                midiout.send_message([252])
                play = False

keyboard.on_press(presionando, suppress=False)
keyboard.on_release(soltando, suppress=True)
keyboard.on_press_key('esc', salir, suppress=True)
keyboard.on_press_key('up', octavaSubir, suppress=True)
keyboard.on_press_key('down', octavaBajar, suppress=True)
keyboard.on_press_key('`', toggleHold, suppress=True)
keyboard.on_press_key('space', toggleSecuencia, suppress=True)
keyboard.on_press_key('backspace', resetearSecuencia, suppress=True)
keyboard.on_press_key('enter', startStopClock, suppress=True)

print("Arrancamo!")
stdscr = curses.initscr()
curses.noecho()
curses.cbreak()
corriendo=True
tiempo = 0
tiempoTemp = 0
tick = 0
while(corriendo==True):
        cantVoces = proxCantVoces
        ampOct = proxAmpOct
        tiempoTemp = tiempo
        tiempo = time.time() % (60/bpm/clockDiv)
        if tiempo < tiempoTemp:
                if len(escala) > 0 and tick == 0:
                        for i in range(cantVoces):
                                if secuenciar:
                                        s = secuencias[i]
                                        if s[stepActual][1] == True:
                                                n = s[stepActual][0]
                                                nota = (escala[n % len(escala)], octava + int(ampOct / cantVoces * i), s[stepActual][2])
                                                d = 60/bpm/stepsDiv*delay/cantVoces*i
                                                t = threading.Timer(d, programarOn, [nota])
                                                t.start()
                                else:
                                        if random.random() <= probabilidad:
                                                nota = (escala[random.randint(0,len(escala)-1)], octava  + int(ampOct / cantVoces * i), random.randint(velRange[0],velRange[1]))
                                                d = 60/bpm/stepsDiv*delay/cantVoces*i
                                                t = threading.Timer(d, programarOn, [nota])
                                                t.start()
                        if secuenciar: mutar(stepActual)
                        stepActual += 1
                        stepActual = stepActual % stepsCant
                        if play == True:
                                if start == True:
                                        midiout.send_message([250])
                                        start = False
                if play == True: midiout.send_message([248])
                tick = tick+1
                tick = tick%(clockDiv/stepsDiv)
                tick = math.floor(tick)
midiout.send_message([252])
curses.flushinp()
curses.nocbreak()
curses.echo()
curses.endwin()
exit()
