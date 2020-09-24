print("Pepas MIDI v0.00.001")
print("Cargando...")

import curses
import time
import threading
import rtmidi
import keyboard
import random

bpm = 160 # F1: tempo, en BMP
probabilidad = 1.0 # F2: probabilidad de ejecucion de nota, 0: nunca, 1: siempre
cantVoces = 1 # F3: cantidad de voces simultaneas
stepsDiv = 2 # F4: cantidad de steps por beat
stepDuracion = 1.0 # F5: duracion de la nota relativa al beat
stepsCant = 4 # F6: cantidad de steps en las secuencias fijas
probMutacion = 0.0 # F7: probabilidad de mutacion de secuencias fijas, 0: no muta, 1: muta completamente
ampOct = 0 # F8: amplitud de octavas, las voces se distribuyen a lo largo de esta cantidad de octavas, valores aceptados 0-5
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
        return dic.get(k.name, None)

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
        noteOn(nota)

notasAApagar = []
def programarOff(nota):
        for i,val in enumerate(notasAApagar):
                if val[0] == nota[0]:
                        del notasAApagar[i]
                        break
        if notasAApagar.count(nota) == 0:
                noteOff(nota)

def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)

presionadas = []
def presionando(key):
        global controlando, controlCantVoces, cantVoces, proxCantVoces, controlBPM, proxBPM, bpm, controlProb, probabilidad, controlStepsDiv, stepsDiv, controlStepsDur, stepDuracion, controlStepsCant, stepsCant, proxStepsCant, controlProbMut, probMutacion, controlAmpOct, proxAmpOct, controlVelRange, velRange, controlDelay, delay
        if key.name not in presionadas:
                presionadas.append(key.name)
                if mapKeyToMIDI(key) is not None and controlando == False:
                        if ((holdMode == True) and (len(presionadas) == 1)):
                                global escala
                                escala.clear()
                        escala.append(key)
                if mapKeyToNum(key) is not None and controlando == True:
                        if controlBPM == True: proxBPM.append(int(mapKeyToNum(key)%10))
                        if controlProb == True: probabilidad = mapKeyToNum(key)/10.0
                        if controlCantVoces == True: proxCantVoces = int(mapKeyToNum(key))
                        if controlStepsDiv == True: stepsDiv = mapKeyToNum(key)
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
                        # aun sin uso
                        controlando = True
                if key.name == "f12":
                        # aun sin uso
                        controlando = True

def soltando(key):
        global controlando, controlCantVoces, cantVoces, proxCantVoces, controlBPM, proxBPM, bpm, controlProb, controlStepsDiv, controlStepsCant, proxStepsCant, stepsCant, controlProbMut, controlAmpOct, controlVelRange, controlDelay
        if key.name in presionadas:
                presionadas.remove(key.name)
                if mapKeyToMIDI(key) and controlando == False:
                        if not holdMode:
                                for i in escala:
                                        if i.name == key.name: escala.remove(i)
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
                        # aun sin uso
                        controlando = False
                if key.name == "f12":
                        # aun sin uso
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

keyboard.on_press(presionando, suppress=False)
keyboard.on_release(soltando, suppress=True)
keyboard.on_press_key('esc', salir, suppress=True)
keyboard.on_press_key('up', octavaSubir, suppress=True)
keyboard.on_press_key('down', octavaBajar, suppress=True)
keyboard.on_press_key('`', toggleHold, suppress=True)
keyboard.on_press_key('space', toggleSecuencia, suppress=True)
keyboard.on_press_key('backspace', resetearSecuencia, suppress=True)

print("Arrancamo!")
stdscr = curses.initscr()
curses.noecho()
curses.cbreak()
corriendo=True
while(corriendo==True):
        cantVoces = proxCantVoces
        ampOct = proxAmpOct
        if len(escala) > 0:
                for i in range(cantVoces):
                        if secuenciar:
                                s = secuencias[i]
                                if s[stepActual][1] == True:
                                        n = s[stepActual][0]
                                        nota = (escala[n % len(escala)], octava + int(ampOct / cantVoces * i), s[stepActual][2])
                                        d = 60/bpm/stepsDiv*delay/cantVoces*i
                                        t = threading.Timer(d, programarOn, [nota])
                                        t.start()
                                        notasAApagar.append(nota)
                                        t = threading.Timer(60/bpm/stepsDiv*stepDuracion + d, programarOff, [nota])
                                        t.start()
                        else:
                                if random.random() <= probabilidad:
                                        nota = (escala[random.randint(0,len(escala)-1)], octava  + int(ampOct / cantVoces * i), random.randint(velRange[0],velRange[1]))
                                        d = 60/bpm/stepsDiv*delay/cantVoces*i
                                        t = threading.Timer(d, programarOn, [nota])
                                        t.start()
                                        notasAApagar.append(nota)
                                        t = threading.Timer(60/bpm/stepsDiv*stepDuracion + d, programarOff, [nota])
                                        t.start()
                if secuenciar: mutar(stepActual)
                stepActual += 1
                stepActual = stepActual % stepsCant
        time.sleep(60/bpm/stepsDiv)
        pass
curses.flushinp()
curses.nocbreak()
curses.echo()
curses.endwin()
exit()
