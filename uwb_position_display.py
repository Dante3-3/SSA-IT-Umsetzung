import time
import turtle
import cmath
import socket
import json

import numpy as np

# UDP-Konfiguration
UDP_IP = "0.0.0.0"  # Hört auf allen Netzwerkschnittstellen
UDP_PORT = 8080      # Muss mit dem ESP32 UDP-Port übereinstimmen

# UDP-Socket erstellen und binden
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
print(f"Listening on {UDP_IP}:{UDP_PORT}")

distance_a1_a2 = 3.0
distance_a1_a3 = 5.0  # Distance to the new anchor
meter2pixel = 100
range_offset = 0.9

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


def detect_outliers_median_std(data, threshold=2):
    median = np.median(data)
    std_dev = np.std(data)
    inliers = [x for x in data if abs(x - median) <= threshold * std_dev]
    return inliers


def read_data():
    try:
        data, addr = sock.recvfrom(1024)  # Maximale Empfangsgröße 1024 Bytes
        line = data.decode('utf-8')

        uwb_list = []
        try:
            uwb_data = json.loads(line)
            print(f"Received from {addr}: {uwb_data}")
            # Extrahiere die Positionen, wenn sie im JSON-Datenformat "links" existieren
            uwb_list = uwb_data.get("links", [])

            # Extrahiere x- und y-Werte separat
            x_values = [pos[0] for pos in uwb_list]
            y_values = [pos[1] for pos in uwb_list]

            # Filtere die Werte basierend auf Median und Standardabweichung
            x_inliers = detect_outliers_median_std(x_values)
            y_inliers = detect_outliers_median_std(y_values)

            # Filtere Positionen basierend auf den gefilterten x- und y-Werten
            filtered_uwb_list = [
                pos for pos in uwb_list if pos[0] in x_inliers and pos[1] in y_inliers
            ]
        except json.JSONDecodeError:
            print(f"Received non-JSON data from {addr}: {line}")
            return []

        return filtered_uwb_list
    except Exception as e:
        print(f"Error receiving data: {e}")
        return []

def tag_pos(a, b, c):
    if b == 0 or c == 0:
        print("Fehler: b oder c ist 0, Berechnung kann nicht durchgeführt werden.")
        return 0, 0

    cos_a = (b**2 + c**2 - a**2) / (2 * b * c)
    cos_a = min(1, max(-1, cos_a))
    x = b * cos_a
    y = b * cmath.sqrt(1 - cos_a**2)
    return round(x.real, 1), round(y.real, 1)

def uwb_range_offset(uwb_range):
    return uwb_range  # Placeholder für eventuelle Offset-Berechnungen


def main():
    t_ui = turtle.Turtle()
    t_a1 = turtle.Turtle()
    t_a2 = turtle.Turtle()
    t_a3 = turtle.Turtle()

    # Initialisiere alle Turtles
    turtle_init(t_ui)
    turtle_init(t_a1)
    turtle_init(t_a2)
    turtle_init(t_a3)

    a1_range = 0.0
    a2_range = 0.0
    a3_range = distance_a1_a3  # Konstante Distanz für die Begrenzungs-Anker

    # UI zeichnen
    draw_ui(t_ui)

    while True:
        # Empfangene Daten lesen und filtern
        uwb_list = read_data()

        if not uwb_list:  # Überprüfe, ob die Liste leer ist
            continue  # Keine Daten zum Verarbeiten, also überspringe die Schleife

        node_count = 0

        # Verarbeitung der gefilterten Daten
        for one in uwb_list:
            if one.get("A") == "1781":
                clean(t_a1)
                a1_range = uwb_range_offset(float(one.get("R", 0)))
                draw_uwb_anchor(-250, 150, "A1781(0,0)", a1_range, t_a1)
                node_count += 1

            elif one.get("A") == "1782":
                clean(t_a2)
                a2_range = uwb_range_offset(float(one.get("R", 0)))
                draw_uwb_anchor(-250 + meter2pixel * distance_a1_a2,
                                150, f"A1782({distance_a1_a2})", a2_range, t_a2)
                node_count += 1

        # Zeichne den dritten Anker als Begrenzungsreferenz
        clean(t_a3)
        draw_uwb_anchor(-250, 150 - meter2pixel * distance_a1_a3, "A1783(0,5)", a3_range, t_a3)

        # Wenn zwei Anker erkannt wurden, berechne die Position des Tags
        if node_count == 2:
            x, y = tag_pos(a2_range, a1_range, distance_a1_a2)
            print(f"Tag Position: ({x}, {y})")
            draw_uwb_tag(x, y, "TAG", t_a3)

        time.sleep(0.1)  # Pause, um die Schleife nicht zu oft auszuführen

    turtle.mainloop()

if __name__ == '__main__':
    main()