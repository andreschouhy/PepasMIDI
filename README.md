# PepasMIDI
Secuenciador generativo de notas MIDI

## Introducción
Similar a su proyecto hermano mayor [Pepas](https://github.com/andreschouhy/Pepas), Pepas MIDI es un script de Python que envía mensajes MIDI para que cualquier dispositivo los convierta en sonido.
Aún está en fase de desarrollo: si bien ya está desarrollada la mayoría de sus funciones finales, aún queda por desarrollar el modo de interactuar en vivo con el script.

## Mapa de botones
###### No está soportado el teclado numérico por el momento. Siempre que se mencionan botones de números, se refiere a los que están sobre las letras.

- Notas musicales: 34 notas posibles se distribuyen a lo largo de las botones de letras y números de la siguiente manera:
  - notas "blancas" (de un teclado musical tradicional) en las fila desde "Z" hasta "/" y desde "Q" hasta "P"
  - notas "negras" (de un teclado musical tradicional) en las filas desde "A" hasta ";" y desde "1" hasta "0" (excluyendo "A", "F", "K", "1", "4" y "8")
- " ' " (el botón a la izquierda del "1") alterna entre 2 modos de accionar notas:
  - Hold Off: se accionan las notas que están siendo presionas
  - Hold On: se mantienen activas las notas que se presionaron desde que se presiona la primera nota hasta que ya no hay notas presionadas, luego de esto se reinicia el grupo de notas al presionar la primera de un nuevo grupo de notas.
- "ESPACIO" alterna entre el modo de secuencias aleatorias y secuencias fijas
- "BORRAR" resetea la secuencia (para el modo de secuencias fijas)
- "F1" Tempo en BPM. Mientras se presiona F1 entrar BPM usando los numeros, el cambio se efectiviza al soltar F1.
- "F2" Probabilidad de ejecucion de nota, 0: nunca, 1: siempre. Botones "1" al "0" para asignar valores de 0.1 a 1.0 y botones "Q" a la "P" para asignar valores de 0.0 a 0.09.
- "F3" Cantidad de voces simultaneas. Botones "1" al "0" para asignar valores de 1 a 10.
- "F4" Cantidad de steps por beat. Mientras se presiona F4 entrar cantidad usando los numeros, el cambio se efectiviza al soltar F4.
- "F5" Duracion de la nota relativa a la duracion del step. Botones "1" al "0" para asignar valores de 1.0 a 10.0 y botones "Q" a la "P" para asignar valores de 0.0 a 0.9.
- "F6" Cantidad de steps en las secuencias fijas. Mientras se presiona F6 entrar cantidad usando los numeros, el cambio se efectiviza al soltar F6.
- "F7" Probabilidad de mutacion de secuencias fijas, 0: no muta, 1: muta completamente. Botones "1" al "0" para asignar valores de 0.1 a 1.0 y botones "Q" a la "P" para asignar valores de 0.0 a 0.09.
- "F8" Amplitud de octavas, las voces se distribuyen a lo largo de esta cantidad de octavas, valores aceptados 1-5. Botones "1" a "5".
- "F9" Rango de variacion en la intensidad de ejecucion de las notas, valores aceptados 1-127. Botones "1" al "0" para asignar el valor máximo entre 1 y 127, botones "Q" a la "P" para asignar el valor mínimo entre 1 y 127.
- "F10" Retraso relativo de tiempo entre cada voz, esto genera que 2 o mas notas simultaneas se ejecuten con una minima diferencia de tiempo. Botones "1" al "0" para asignar valores de 0.1 a 1.0 y botones "Q" a la "P" para asignar valores de 0.0 a 0.09.
- (Bonus track) Debido a un descuido del programador, cuando estamos en modo hold on y ya esta definida la escala (es decir que presionamos varias notas y soltamos todo) podemos seguir agregando notas a la escala actual si lo hacemos manteniendo botones que no hagan nada, por ej.: SHIFT, CTRL, ALT, ENTER, etc.

## Requerimientos
- Python 3
- Librerías externas:
  - [python-rtmidi](https://pypi.org/project/python-rtmidi/)
  - [keyboard](https://pypi.org/project/keyboard/)
  - [windows-curses](https://pypi.org/project/windows-curses/) (sólo en Windows)
- [loopMIDI](https://www.tobias-erichsen.de/software/loopmidi.html)  (sólo en Windows). [Acá](https://github.com/AhmadMoussa/Python-Midi-Ableton/blob/master/Readme.md) hay un tutorial de cómo usarlo: 
- Teclado en inglés (no es excluyente el idioma, porque se puede alterar el mapa de caracteres dentro del script)
