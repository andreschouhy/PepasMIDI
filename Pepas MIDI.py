"""
Pepas MIDI
Secuenciador aleatorio de notas musicales
Autor: Andres Chouhy
"""

print("Pepas MIDI v0.00.008")
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
velRange = (127, 127) # F9: rango de variacion en la intensidad de ejecucion de las notas, valores aceptados 1-127
delay = 0.0 # F10: retraso relativo de tiempo entre cada voz, esto genera que 2 o mas notas simultaneas se ejecuten con una minima diferencia de tiempo
secuenciar = False # BARRA ESPACIADORA: modo secuencia fija
octava = -2 # FLECHAS ARRIBA Y ABAJO: octava master

notasAApagar = []
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
presetActual = 1

midiout = rtmidi.MidiOut()
midiin = rtmidi.MidiIn()

# available_ports_out = midiout.get_ports()
#available_ports_in = midiin.get_ports()

# if available_ports_out:
# 	midiout.open_port(0)
# else:
# 	midiout.open_virtual_port("Pepas MIDI Out")
midiout.open_virtual_port("Pepas MIDI Out")

# if available_ports_in:
# 	midiin.open_port(0)
# else:
# 	midiin.open_virtual_port("Pepas MIDI In")
midiin.open_virtual_port("Pepas MIDI In")

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
    midiout.send_message([0x90, mapKeyToMIDI(key[0]) + key[1] * 12, key[2]])

def noteOff(key):
    midiout.send_message([0x80, mapKeyToMIDI(key[0]) + key[1] * 12, key[2]])

def programarOn(nota):
    global notasAApagar
        
    #noteOn(nota)
    midiout.send_message([0x90, mapKeyToMIDI(nota[0]) + nota[1] * 12, nota[2]])
        
    n = mapKeyToMIDI(nota[0]) + nota[1] * 12
    notasAApagar.append(n)
    t = threading.Timer(60 / bpm / stepsDiv * stepDuracion + d, programarOff, [n])
    t.start()

def programarOff(n):
    global notasAApagar

    notasAApagar.remove(n)

    if notasAApagar.count(n) == 0:
        #noteOff(nota)
        midiout.send_message([0x80, n, 127])

def translate(value, leftMin, leftMax, rightMin, rightMax):
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin
    valueScaled = float(value - leftMin) / float(leftSpan)
    return rightMin + (valueScaled * rightSpan)

def guardarPreset(_i):
    global presetPath, escala, secuencias, bpm, probabilidad, cantVoces, stepsDiv, stepDuracion, stepsCant, probMutacion, ampOct, velRange, delay, presetActual

    try: 
        presetFile = open(presetPath, "r")
    except: 
        presetFile = open(presetPath, "w")

    try: 
        lineas = presetFile.readlines()
    except: 
        lineas = [""]

    presetFile.close()
        
    if _i >= 1: 
        i = int(_i)
    else: 
        i = int(((_i + .1) * 10) + 10)
        
    escalaEstado = False
    secuenciasEstado = False

    if len(escala) > 0: 
        escalaEstado = True
    if len(secuencias) > 0: 
        secuenciasEstado = True

    p = {
        "preset": i,
        "escala": (escalaEstado, escala), # unico activado por defecto
        "secuencias": (False, secuencias), 
        "tempo": (False, bpm), 
        "probabilidad": (False, probabilidad), 
        "cantVoces": (False, cantVoces), 
        "stepsDiv": (False, stepsDiv), 
        "stepDuracion": (False, stepDuracion), 
        "stepsCant": (False, stepsCant), 
        "probMutacion": (False, probMutacion), 
        "ampOct": (False, ampOct), 
        "velRange": (False, velRange),
        "delay": (False, delay)
        }

    presetActual = i

    p = str(p)

    if len(lineas) <= i: 
        lineas[-1] += "\n"

    while len(lineas) <= i - 1: 
        lineas.append("\n")

    if len(lineas) > i: 
        p += "\n"

    lineas[i-1] = p
    presetFile = open(presetPath, "w")
    presetFile.writelines(lineas)
    presetFile.close()

def cargarPreset(_i):
    global presetPath, escala, secuencias, bpm, probabilidad, cantVoces, stepsDiv, stepDuracion, stepsCant, probMutacion, ampOct, velRange, delay, proxCantVoces, proxStepsCant, proxAmpOct, presetActual

    try: 
        presetFile = open(presetPath, "r")
    except:
        print("Archivo de presets inexistente")
        return

    lineas = presetFile.readlines()
    presetFile.close()

    if _i >= 1: 
        i = int(_i)
    else: 
        i = int(((_i + .1) * 10) + 10)

    if len(lineas) > i:
        try: 
            p = eval(lineas[i-1])
        except:
            print("Preset invalido")
            return
    else:
        print("Preset inexistente")
        return

    presetActual = i

    if p.get("escala")[0] == True: 
        escala = p.get("escala")[1]
    
    if p.get("secuencias")[0] == True: 
        secuencias = p.get("secuencias")[1]
    
    if p.get("tempo")[0] == True: 
        bpm = p.get("tempo")[1]
    
    if p.get("probabilidad")[0] == True: 
        probabilidad = p.get("probabilidad")[1]
    
    if p.get("cantVoces")[0] == True: 
        proxCantVoces = p.get("cantVoces")[1]
    
    if p.get("stepsDiv")[0] == True: 
        stepsDiv = p.get("stepsDiv")[1]
    
    if p.get("stepDuracion")[0] == True: 
        stepDuracion = p.get("stepDuracion")[1]
    
    if p.get("stepsCant")[0] == True: 
        stepsCant = p.get("stepsCant")[1]
    
    if p.get("probMutacion")[0] == True: 
        probMutacion = p.get("probMutacion")[1]
    
    if p.get("ampOct")[0] == True: 
        proxAmpOct = p.get("ampOct")[1]
    
    if p.get("velRange")[0] == True: 
        velRange = p.get("velRange")[1]
    
    if p.get("delay")[0] == True: 
        delay = p.get("delay")[1]

def alternarControlesPreset(k):
    global presetPath, escala, secuencias, bpm, probabilidad, cantVoces, stepsDiv, stepDuracion, stepsCant, probMutacion, ampOct, velRange, delay, proxCantVoces, proxStepsCant, proxAmpOct, presetActual
        
    try: 
        presetFile = open(presetPath, "r")
    except:
        print("Archivo de presets inexistente")
        return

    lineas = presetFile.readlines()
    presetFile.close()

    if presetActual >= 1: 
        i = int(presetActual)
    else: 
        i = int(((presetActual + .1) * 10) + 10)

    if len(lineas) > i:
        try: 
            l = eval(lineas[i - 1])
        except:
            print("Preset invalido")
            return
    else:
        print("Preset inexistente")
        return
        
    if k == "z": 
        l["escala"] = (not l.get("escala")[0], l.get("escala")[1]) #revisar si este metodo es el mejor para asignar un valor en un tuple
    
    if k == "x": 
        l["secuencias"] = (not l.get("secuencias")[0], l.get("secuencias")[1])
    
    if k == "f1": 
        l["tempo"] = (not l.get("tempo")[0], l.get("tempo")[1])
    
    if k == "f2": 
        l["probabilidad"] = (not l.get("probabilidad")[0], l.get("probabilidad")[1])
    
    if k == "f3": 
        l["cantVoces"] = (not l.get("cantVoces")[0], l.get("cantVoces")[1])
    
    if k == "f4": 
        l["stepsDiv"] = (not l.get("stepsDiv")[0], l.get("stepsDiv")[1])
    
    if k == "f5": 
        l["stepDuracion"] = (not l.get("stepDuracion")[0], l.get("stepDuracion")[1])
    
    if k == "f6": 
        l["stepsCant"] = (not l.get("stepsCant")[0], l.get("stepsCant")[1])
    
    if k == "f7": 
        l["probMutacion"] = (not l.get("probMutacion")[0], l.get("probMutacion")[1])
    
    if k == "f8": 
        l["ampOct"] = (not l.get("ampOct")[0], l.get("ampOct")[1])
    
    if k == "f9": 
        l["velRange"] = (not l.get("velRange")[0], l.get("velRange")[1])
    
    if k == "f10": 
        l["delay"] = (not l.get("delay")[0], l.get("delay")[1])

    l = str(l)
    if len(lineas) <= i: 
        lineas[-1] += "\n"

    while len(lineas) <= i - 1: 
        lineas.append("\n")

    if len(lineas) > i: 
        l += "\n"

    lineas[i - 1] = l
    presetFile = open(presetPath, "w")
    presetFile.writelines(lineas)
    presetFile.close()

presionadas = []
def presionando(key):
    global controlando, controlCantVoces, cantVoces, proxCantVoces, controlBPM, proxBPM, bpm, controlProb, probabilidad, controlStepsDiv, stepsDiv, controlStepsDur, stepDuracion, controlStepsCant, stepsCant, proxStepsCant, controlProbMut, probMutacion, controlAmpOct, proxAmpOct, controlVelRange, velRange, controlDelay, delay, controlGuardarPreset, controlCargarPreset
    
    if key.name not in presionadas:
        presionadas.append(key.name)

        keyNum = mapKeyToNum(key)

        if mapKeyToMIDI(key.name) is not None and controlando == False:
            if ((holdMode == True) and (len(presionadas) == 1)):
                global escala
                escala.clear()
            
            escala.append(key.name)

        if keyNum is not None and controlando == True:
            if controlBPM == True: 
                proxBPM.append(int(keyNum % 10))

            if controlProb == True: 
                probabilidad = keyNum / 10.0
            
            if controlCantVoces == True: 
                proxCantVoces = int(keyNum)
            
            if controlStepsDiv == True:
                if keyNum >= 1.0:
                    stepsDiv = keyNum
                else:
                    stepsDiv = 1.0 / ((keyNum + 0.1) * 10.0)
            
            if controlStepsDur == True: 
                stepDuracion = keyNum
            
            if controlStepsCant == True: 
                proxStepsCant.append(int(keyNum % 10))
            
            if controlProbMut == True: 
                probMutacion = keyNum / 10.0
            
            if controlAmpOct == True: 
                proxAmpOct = int(min(keyNum, 5))
            
            if controlVelRange == True:
                if keyNum < 1.0:
                    v = int(translate(keyNum, 0.0, 0.9, 1, 127))
                    velRange = (v, max(velRange[1], v))
                else:
                    v = int(translate(keyNum, 1.0, 10.0, 1, 127))
                    velRange = (min(velRange[0], v), v)
            
            if controlDelay == True: 
                delay = keyNum / 10.0
            
            if controlGuardarPreset: 
                guardarPreset(keyNum)
            
            if controlCargarPreset: 
                cargarPreset(keyNum)
        
        alternarControlesPresetKeyName = alternarControlesPreset(key.name)

        if key.name == "f1":
            proxBPM = []
            controlBPM = True
            controlando = True

            if controlGuardarPreset: 
                alternarControlesPresetKeyName

        if key.name == "f2":
            controlProb = True
            controlando = True

            if controlGuardarPreset: 
                alternarControlesPresetKeyName

        if key.name == "f3":
            controlCantVoces = True
            controlando = True

            if controlGuardarPreset: 
                alternarControlesPresetKeyName

        if key.name == "f4":
            controlStepsDiv = True
            controlando = True

            if controlGuardarPreset: 
                alternarControlesPresetKeyName

        if key.name == "f5":
            controlStepsDur = True
            controlando = True

            if controlGuardarPreset: 
                alternarControlesPresetKeyName

        if key.name == "f6":
            proxStepsCant = []
            controlStepsCant = True
            controlando = True

            if controlGuardarPreset: 
                alternarControlesPresetKeyName

        if key.name == "f7":
            controlProbMut = True
            controlando = True

            if controlGuardarPreset: 
                alternarControlesPresetKeyName

        if key.name == "f8":
            controlAmpOct = True
            controlando = True

            if controlGuardarPreset: 
                alternarControlesPresetKeyName

        if key.name == "f9":
            controlVelRange = True
            controlando = True

            if controlGuardarPreset: 
                alternarControlesPresetKeyName

        if key.name == "f10":
            controlDelay = True
            controlando = True

            if controlGuardarPreset: 
                alternarControlesPresetKeyName

        if key.name == "f11":
            controlGuardarPreset = True
            controlando = True
        
        if key.name == "f12":
            controlCargarPreset = True
            controlando = True

        if key.name == "z" and controlGuardarPreset: 
            alternarControlesPresetKeyName

        if key.name == "x" and controlGuardarPreset: 
            alternarControlesPresetKeyName

def soltando(key):
    global controlando, controlCantVoces, cantVoces, proxCantVoces, controlBPM, proxBPM, bpm, controlProb, controlStepsDiv, controlStepsDur, controlStepsCant, proxStepsCant, stepsCant, controlProbMut, controlAmpOct, controlVelRange, controlDelay, controlGuardarPreset, controlCargarPreset
        
    if key.name in presionadas:
        presionadas.remove(key.name)

        if mapKeyToMIDI(key.name) and controlando == False:
            if not holdMode:
                for i in escala:
                    if i == key.name: escala.remove(key.name)

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
    """if secuenciar == True:
        resetearSecuencia(k)"""

def resetearSecuencia(k):
    global secuencias, stepActual
    stepActual = 0
    secuencias.clear()

    for v in range(maxVoces):
        secuencias.append(list())
        for i in range(stepsCant):
            if random.random() <= probabilidad: 
                s = True
            else: 
                s = False

            secuencias[v].append(((random.randint(0, 256)), s, random.randint(velRange[0], velRange[1])))

def mutar(step):
    if random.random() <= probMutacion:
        for v in range(maxVoces):
            if random.random() <= probabilidad: 
                s = True
            else: 
                s = False
            
            sec = secuencias[v]
            sec[step%len(sec)] = ((random.randint(0, 256)), s, random.randint(velRange[0], velRange[1]))

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
resetearSecuencia(None)

while (corriendo == True):
    cantVoces = proxCantVoces
    ampOct = proxAmpOct
    tiempoTemp = tiempo
    tiempo = time.time() % (60 / bpm / clockDiv)

    if tiempo < tiempoTemp:
        if len(escala) > 0 and tick == 0:
            for i in range(cantVoces):
                if secuenciar:
                    s = secuencias[i % len(secuencias)]
                    if s[stepActual % len(s)][1] == True:
                        n = s[stepActual % len(s)][0]
                        nota = (escala[n % len(escala)], octava + int(ampOct / cantVoces * i), s[stepActual % len(s)][2])
                        d = 60 / bpm / stepsDiv * delay / cantVoces * i
                        t = threading.Timer(d, programarOn, [nota])
                        t.start()
                else:
                    if random.random() <= probabilidad:
                        nota = (escala[random.randint(0, len(escala) - 1)], octava + int(ampOct / cantVoces * i), random.randint(velRange[0], velRange[1]))
                        d = 60 / bpm / stepsDiv * delay / cantVoces * i
                        t = threading.Timer(d, programarOn, [nota])
                        t.start()

            if secuenciar: 
                mutar(stepActual)

            stepActual += 1
            stepActual = stepActual % stepsCant

            if play == True:
                if start == True:
                    midiout.send_message([250])
                    start = False

        if play == True: 
            midiout.send_message([248])

        tick = tick + 1
        tick = tick % (clockDiv / stepsDiv)
        tick = math.floor(tick)

midiout.send_message([252])
curses.flushinp()
curses.nocbreak()
curses.echo()
curses.endwin()
exit()
