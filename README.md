# PepasMIDI
Secuenciador generativo de notas MIDI

## Introducción
Similar a su proyecto hermano mayor Pepas, Pepas MIDI es un script de Python que envía mensajes MIDI para que cualquier dispositivo los convierta en sonido.
Aún está en fase de desarrollo: si bien ya está desarrollada la mayoría de sus funciones finales, aún queda por desarrollar el modo de interactuar en vivo con el script.

## Mapa de botones
- Notas musicales: 34 notas posibles se distribuyen a lo largo de las botones de letras y números de la siguiente manera:
  - notas "blancas" (de un teclado musical tradicional) en las fila desde "Z" hasta "/" y desde "Q" hasta "P"
  - notas "negras" (de un teclado musical tradicional) en las filas desde "A" hasta ";" y desde "1" hasta "0" (excluyendo "A", "F", "K", "1", "4" y "8")
- " ' " (el botón a la izquierda del "1") alterna entre 2 modos de accionar notas:
  - uno en el que se accionan las notas que están siendo presionas
  - otro en el que se mantienen activas las notas que se presionaron desde que se presiona la primera nota hasta que ya no hay notas presionadas, luego de esto se reinicia el grupo de notas al presionar la primera de un nuevo grupo de notas.
- "ESPACIO" alterna entre el modo de secuencias aleatorias y secuencias fijas
- "BORRAR" resetea la secuencia (para el modo de secuencias fijas)

El resto de las variables por el momento se editan desde el script directamente.

## Requerimientos
- Python 3
- Librerías externas:
  - python-rtmidi https://pypi.org/project/python-rtmidi/
  - keyboard https://pypi.org/project/keyboard/
