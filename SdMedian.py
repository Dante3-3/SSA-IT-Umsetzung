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

# Funktion zur Identifikation von Ausreißern basierend auf Median und Standardabweichung
def detect_outliers_median_std(data, threshold=2):
    median = np.median(data)
    std_dev = np.std(data)

    # Identifiziere die Ausreißer und akzeptablen Werte
    outliers = [x for x in data if abs(x - median) > threshold * std_dev]
    inliers = [x for x in data if abs(x - median) <= threshold * std_dev]

    return outliers, inliers

# Identifiziere Ausreißer für x- und y-Werte
x_outliers_median, x_inliers_median = detect_outliers_median_std(x_values)
y_outliers_median, y_inliers_median = detect_outliers_median_std(y_values)

# Filtere die Positionsdaten basierend auf den Inliers von x- und y-Werten
filtered_positions_median = [
    pos for pos in positions
    if pos[0] in x_inliers_median and pos[1] in y_inliers_median
]

print("Originale Positionsdaten:", positions)
print("Gefundene Ausreißer mit Median und Standardabweichung:",
      [(pos[0], pos[1]) for pos in positions if pos[0] in x_outliers_median or pos[1] in y_outliers_median])
print("Gefilterte Positionsdaten mit Median und Standardabweichung:", filtered_positions_median)
