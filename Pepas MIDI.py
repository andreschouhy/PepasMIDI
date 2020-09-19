print("Pepas MIDI v0.00.001")
print("Cargando...")

import curses
import time
import threading
import rtmidi
import keyboard
import random

bpm = 120.0
stepsDiv = 2
stepDuracion = 2.0
escala = []
probabilidad = 0.125
cantVoces = 8
octava = -2
ampOct = 4
stepsCant = 16
secuencias = []
secuenciar = False
stepActual = 1
velRange = (0,127)
delay = 0.2 / cantVoces
probMutacion = 0.3

holdMode = False

midiout = rtmidi.MidiOut()
available_ports = midiout.get_ports()

if available_ports:
	midiout.open_port(0)
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
        return dic.get(k.name)

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

presionadas = []
def presionando(key):
        if key.name not in presionadas:
                presionadas.append(key.name)
                if mapKeyToMIDI(key):
                        if ((holdMode == True) and (len(presionadas) == 1)):
                                global escala
                                escala.clear()
                        escala.append(key)

def soltando(key):
        if key.name in presionadas:
                presionadas.remove(key.name)
                if mapKeyToMIDI(key):
                        if not holdMode:
                                for i in escala:
                                        if i.name == key.name: escala.remove(i)

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
        global secuencia
        global stepActual
        stepActual = 0
        secuencias.clear()
        for v in range(cantVoces):
                secuencias.append(list())
                for i in range(stepsCant):
                        if random.random() <= probabilidad: s = True
                        else: s = False
                        secuencias[v].append(((random.randint(0, 256)), s, random.randint(velRange[0],velRange[1])))

def mutar(step):
        if random.random() <= probMutacion:
                for v in range(cantVoces):
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
        if len(escala) > 0:
                for i in range(cantVoces):
                        if secuenciar:
                                s = secuencias[i]
                                if s[stepActual][1] == True:
                                        n = s[stepActual][0]
                                        nota = (escala[n % len(escala)], octava + int(ampOct / cantVoces * i), s[stepActual][2])
                                        d = 60/bpm/stepsDiv*delay*i
                                        t = threading.Timer(d, programarOn, [nota])
                                        t.start()
                                        notasAApagar.append(nota)
                                        t = threading.Timer(60/bpm/stepsDiv*stepDuracion + d, programarOff, [nota])
                                        t.start()
                        else:
                                if random.random() <= probabilidad:
                                        nota = (escala[random.randint(0,len(escala)-1)], octava  + int(ampOct / cantVoces * i), random.randint(velRange[0],velRange[1]))
                                        d = 60/bpm/stepsDiv*delay*i
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
