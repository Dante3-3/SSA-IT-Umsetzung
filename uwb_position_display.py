import time
import turtle
import cmath
import socket
import json
import math

import numpy

# UDP-Konfiguration
UDP_IP = "0.0.0.0"  # Hört auf allen Netzwerkschnittstellen
UDP_PORT = 8080      # Muss mit dem ESP32 UDP-Port übereinstimmen

# UDP-Socket erstellen und binden
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
print(f"Listening on {UDP_IP}:{UDP_PORT}")

distance_a1_a2 = 3.0
meter2pixel = 100
range_offset = 0.9

FIELD_WIDTH = 3.0
FIELD_HEIGHT = 5.0

def screen_init(width=1200, height=800, t=turtle):
    t.setup(width, height)
    t.tracer(False)
    t.hideturtle()
    t.speed(0)

def turtle_init(t=turtle):
    t.hideturtle()
    t.speed(0)

def draw_line(x0, y0, x1, y1, color="black", t=turtle):
    t.pencolor(color)
    t.up()
    t.goto(x0, y0)
    t.down()
    t.goto(x1, y1)
    t.up()

def draw_fastU(x, y, length, color="black", t=turtle):
    draw_line(x, y, x, y + length, color, t)

def draw_fastV(x, y, length, color="black", t=turtle):
    draw_line(x, y, x + length, y, color, t)

def draw_cycle(x, y, r, color="black", t=turtle):
    t.pencolor(color)
    t.up()
    t.goto(x, y - r)
    t.setheading(0)
    t.down()
    t.circle(r)
    t.up()

def fill_cycle(x, y, r, color="black", t=turtle):
    t.up()
    t.goto(x, y)
    t.down()
    t.dot(r, color)
    t.up()

def write_txt(x, y, txt, color="black", t=turtle, f=('Arial', 12, 'normal')):
    t.pencolor(color)
    t.up()
    t.goto(x, y)
    t.down()
    t.write(txt, move=False, align='left', font=f)
    t.up()

def draw_rect(x, y, w, h, color="black", t=turtle):
    t.pencolor(color)
    t.up()
    t.goto(x, y)
    t.down()
    t.goto(x + w, y)
    t.goto(x + w, y + h)
    t.goto(x, y + h)
    t.goto(x, y)
    t.up()

def fill_rect(x, y, w, h, color=("black", "black"), t=turtle):
    t.begin_fill()
    draw_rect(x, y, w, h, color, t)
    t.end_fill()

def clean(t=turtle):
    t.clear()

def draw_ui(t):
    write_txt(-300, 250, "UWB Position", "black", t, f=('Arial', 32, 'normal'))
    fill_rect(-400, 200, 800, 40, "black", t)
    write_txt(-50, 205, "WALL", "yellow", t, f=('Arial', 24, 'normal'))

def draw_uwb_anchor(x, y, txt, range, t):
    r = 20
    fill_cycle(x, y, r, "green", t)
    write_txt(x + r, y, f"{txt}: {range}M", "black", t, f=('Arial', 16, 'normal'))

def draw_uwb_tag(x, y, txt, t):
    pos_x = -250 + int(x * meter2pixel)
    pos_y = 150 - int(y * meter2pixel)
    r = 20
    fill_cycle(pos_x, pos_y, r, "blue", t)
    write_txt(pos_x, pos_y, f"{txt}: ({x},{y})", "black", t, f=('Arial', 16, 'normal'))

def read_data():
    try:
        data, addr = sock.recvfrom(1024)  # Maximale Empfangsgröße 1024 Bytes
        line = data.decode('utf-8')
        uwb_list = []

        try:
            uwb_data = json.loads(line)
            print(f"Received from {addr}: {uwb_data}")
            uwb_list = uwb_data.get("links", [])
        except json.JSONDecodeError:
            print(f"Received non-JSON data from {addr}: {line}")

        return uwb_list
    except Exception as e:
        print(f"Error receiving data: {e}")
        return []

def tag_pos(a, b, c):
    # Überprüfen, ob b oder c gleich 0 sind, um Division durch 0 zu vermeiden
    if b == 0 or c == 0:
        print("Fehler: b oder c ist 0, Berechnung kann nicht durchgeführt werden.")
        return 0, 0  # Rückgabewerte, falls die Berechnung nicht möglich ist

    # Berechnung des Cosinus des Winkels
    cos_a = (b**2 + c**2 - a**2) / (2 * b * c)

    # Überprüfen, ob cos_a einen gültigen Bereich hat (-1 <= cos_a <= 1)
    cos_a = min(1, max(-1, cos_a))

    # Berechnung der x- und y-Koordinaten
    x = b * cos_a
    y = b * cmath.sqrt(1 - cos_a**2)

    return round(x.real, 1), round(y.real, 1)


def uwb_range_offset(uwb_range):
    return uwb_range  # Placeholder für eventuelle Offset-Berechnungen

def is_out_of_bounds(x, y):
    return x >= FIELD_WIDTH and y >= FIELD_HEIGHT


def is_within_field(tag_x, tag_y):
    # Berechnung der diagonalen Entfernungen zur oberen linken Ecke (0, FIELD_HEIGHT)
    dist_to_top_left = math.sqrt(tag_x ** 2 + (tag_y - FIELD_HEIGHT) ** 2)

    # Berechnung der diagonalen Entfernungen zur oberen rechten Ecke (FIELD_WIDTH, FIELD_HEIGHT)
    dist_to_top_right = math.sqrt((tag_x - FIELD_WIDTH) ** 2 + (tag_y - FIELD_HEIGHT) ** 2)

    # Berechnung der maximalen zulässigen Distanz innerhalb des Spielfelds
    max_dist_to_top_left = math.sqrt(FIELD_WIDTH ** 2 + FIELD_HEIGHT ** 2)
    max_dist_to_top_right = max_dist_to_top_left  # Gleiche Diagonale für beide Ecken

    # Überprüfen, ob der Tag innerhalb der Spielfeldgrenzen liegt
    within_field = dist_to_top_left <= max_dist_to_top_left and dist_to_top_right <= max_dist_to_top_right

    return within_field


import numpy as np


def aus_vorne(x, y):
    # Berechnung von cos(beta) und Begrenzung des Wertes auf den Bereich [-1, 1]
    try:
        cos_beta = (-x ** 2 + y ** 2 + FIELD_WIDTH ** 2) / (2 * y * FIELD_WIDTH)
    except:
        return False
    cos_beta = np.clip(cos_beta, -1.0, 1.0)  # Sicherstellen, dass der Wert im Bereich [-1, 1] liegt

    # Berechnung des Winkels beta in Radiant
    betaWinkel = np.arccos(cos_beta)

    # Berechnung der Höhe hc
    hc = x * np.sin(betaWinkel)

    # Überprüfung, ob hc größer als die Spielfeldhöhe ist
    return hc > FIELD_HEIGHT

def sendArduinoMessage(value):
    sock.sendto(value.encode(), ("172.20.10.2", UDP_PORT))


def main():
    # Initialisierung der Turtle-Turtles
    t_ui = turtle.Turtle()
    t_a1 = turtle.Turtle()
    t_a2 = turtle.Turtle()
    t_a3 = turtle.Turtle()
    turtle_init(t_ui)
    turtle_init(t_a1)
    turtle_init(t_a2)
    turtle_init(t_a3)

    a1_range = 0.0
    a2_range = 0.0

    draw_ui(t_ui)

    while True:
        uwb_list = read_data()
        node_count = 0

        for one in uwb_list:
            if one.get("A") == "1781":
                clean(t_a1)
                a1_range = uwb_range_offset(float(one.get("R", 0)))
                draw_uwb_anchor(-250, 150, "A1782(0,0)", a1_range, t_a1)
                node_count += 1

            elif one.get("A") == "1782":
                clean(t_a2)
                a2_range = uwb_range_offset(float(one.get("R", 0)))
                draw_uwb_anchor(-250 + meter2pixel * distance_a1_a2,
                                150, f"A1783({distance_a1_a2})", a2_range, t_a2)
                node_count += 1

        if node_count == 2:
            x, y = tag_pos(a2_range, a1_range, distance_a1_a2)
            if is_out_of_bounds(a1_range, a2_range) or is_within_field(a1_range, a2_range):
                sendArduinoMessage("draußen")
            else:
                sendArduinoMessage("drinnen")
            clean(t_a3)
            draw_uwb_tag(x, y, "TAG", t_a3)

        time.sleep(0.1)  # Kurze Pause, um CPU-Auslastung zu reduzieren

    turtle.mainloop()

if __name__ == '__main__':
    main()