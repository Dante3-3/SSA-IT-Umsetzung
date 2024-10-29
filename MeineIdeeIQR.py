import numpy as np

# Dynamische Liste für Positionsdaten
positions = [(1.8, 0.6), (1.8, 0.6), (1.7, 0.6), (1.7, 0.5), (4.0, 0.5),
    (1.6, 0.5), (1.5, 0.7), (1.4, 1.0), (1.3, 1.0), (1.5, 0.8),
    (2.4, 0.72), (1.5, 0.8), (1.3, 0.5), (4.0, 0.4), (1.2, 0.2), (1.2, 0.2),
    (1.7, 0.7), (1.8, 0.9), (2.0, 1.0), (4.5, 0.2), (2.1, 1.2),
    (1.04, 1.2), (2.2, 1.3), (1.0, 1.0), (2.1, 1.2), (2.0, 1.9), (0.9, 0.5),
    (1.8, 0.7), (1.9, 0.6), (1.7, 0.7), (1.6, 0.4), (1.5, 0.7),
    (1.4, 0.9), (1.3, 0.8), (3.84, 0.48), (1.5, 0.9), (1.4, 0.7),
    (1.2, 0.3), (1.8, 0.8), (2.0, 1.1), (2.64, 1.56), (2.1, 1.3),
    (2.2, 1.4), (2.0, 1.8), (1.8, 0.5), (1.9, 0.5), (1.6, 0.6),
    (1.7, 0.8), (1.3, 0.4), (0.72, 0.4), (1.2, 0.4), (1.1, 0.6),
    (1.7, 0.9), (1.6, 0.6), (1.4, 0.6)]

# Extrahiere die x-Werte und y-Werte separat
x_values = [pos[0] for pos in positions]
y_values = [pos[1] for pos in positions]


# Funktion zur Identifikation von Ausreißern basierend auf dem IQR
def detect_outliers(data):
    q1 = np.percentile(data, 25)
    q3 = np.percentile(data, 75)
    iqr = q3 - q1

    # Definiere Grenzen für akzeptable Werte
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    # Identifiziere die Ausreißer und akzeptablen Werte
    outliers = [x for x in data if x < lower_bound or x > upper_bound]
    inliers = [x for x in data if lower_bound <= x <= upper_bound]

    return outliers, inliers


# Identifiziere Ausreißer für x- und y-Werte
x_outliers, x_inliers = detect_outliers(x_values)
y_outliers, y_inliers = detect_outliers(y_values)

# Filtere die Positionsdaten basierend auf den inliers von x- und y-Werten
filtered_positions = [pos for pos in positions if pos[0] in x_inliers and pos[1] in y_inliers]

print("Originale Positionsdaten:", positions)
print("Gefundene Ausreißer:", [(pos[0], pos[1]) for pos in positions if pos[0] in x_outliers or pos[1] in y_outliers])
print("Gefilterte Positionsdaten:", filtered_positions)
