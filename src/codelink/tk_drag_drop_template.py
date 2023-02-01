#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Scriptname: move_graphic_object_02.py (wuf 23.07.2008)

# Funktion: Verschieben von Canvas-Objekten mit der Maus bei
#           Gebrauch der 'Drag and Drop' Philosophie

import tkinter as tk

def mouse_button1(mouse,object):
    """Maus fasst das Grafik-Objekt"""

    cv.drag_drop_flag = True

    #~~ Hebt das selektierte Objekt über die anderen
    cv.tag_raise(object,None)

    #~~ Drag-Koordinaten
    cv.mouse_x  = mouse.x
    cv.mouse_y  = mouse.y
    print(cv.mouse_x,cv.mouse_y)

def mouse_release1():
    """Maus lässt Grafik-Objekt fallen"""

    cv.drag_drop_flag = False

def mouse_move(mouse,object):
    """Maus bewegt sich über das Grafik-Objekt"""

    if cv.drag_drop_flag == True:
        #~~ Ermittle den Koordinaten-Offset
        xoff = mouse.x - cv.mouse_x
        yoff = mouse.y - cv.mouse_y

        #~~ Verschiebe das Grafik Objekt
        cv.move(object,xoff,yoff)

        #~~ Aktuelle Koordinaten
        cv.mouse_x = mouse.x
        cv.mouse_y = mouse.y

def mouse_enter(event):
    """Mause bewegt sich ins grafische Objekt"""

    cv.temp_cursor = cv['cursor']
    cv['cursor'] = 'hand1'

def mouse_leave(event):
    """Mause bewegt sich aus dem grafische Objekt"""

    cv['cursor'] = cv.temp_cursor

def event_bindings(object):
    """Binde Mausereignisse an das Grafik-Objekt"""

    # Event für linke Maustaste
    cv.tag_bind(object,"<Button-1>", lambda e,obj=object:mouse_button1(e,obj))
    # Event für loslassen der linken Maustaste
    cv.tag_bind(object,"<ButtonRelease 1>", lambda e,obj=object:mouse_release1())
    # Event für Mausbewegung
    cv.tag_bind(object,"<Motion>", lambda e,obj=object:mouse_move(e,obj))
    # Maus bewegt sich ins Grafik-Objekt
    cv.tag_bind(object,"<Enter>", lambda e:mouse_enter(e))
    # Maus bewegt sich aus dem Grafik-Objekt
    cv.tag_bind(object,"<Leave>", lambda e:mouse_leave(e))

#*** MODUL-TEST: CANVAS-OBJECT-MOVE WITH MOUSE ***
if __name__ == '__main__':

    root = tk.Tk()
    root.title("Drag&Drop Canvas-Object-Move")

    #~~ Erzeugt Canvasfläche für die Aufnahme von Canvas-Objekten
    cv = tk.Canvas(root,height=430,width=450,bd=0,relief='raised',bg='khaki2')
    cv.pack()

    #~~ Folgende Variablen werden dem cv.objekt angehängt
    cv.drag_drop_flag = False
    cv.mouse_x = None
    cv.mouse_y = None

    #~~~Eckkoordinaten für das Objekt gefüllter Kreis
    x0 = 50
    y0 = 50
    x1 = 200
    y1 = 200

    #~~ Zeichnet ein gefüllter Kreis
    object = cv.create_oval(x0,y0,x1,y1,fill='green',outline='darkgreen')
    event_bindings(object)

    #~~~Eckkoordinaten für das Objekt gefülltes Rechteck
    x0 = 150
    y0 = 150
    x1 = 300
    y1 = 300

    #~~ Zeichne ein gefülltes Rechteck
    object = cv.create_rectangle(x0,y0,x1,y1,fill='steelblue3',outline='darkblue')
    event_bindings(object)

    x0 = 100
    x1 = 100
    #~~ Start-Koordinaten für eine Raute
    object = cv.create_polygon(0+x0,50+y0,100+x0,0+y0,
                200+x0,50+y0,100+x0,100+y0,width=3,outline="black",
                activeoutline="green",fill="white")
    event_bindings(object)

    root.mainloop()