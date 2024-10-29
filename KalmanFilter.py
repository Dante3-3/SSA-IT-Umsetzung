import numpy as np

# Definition der KalmanFilter-Klasse
class KalmanFilter:
    def __init__(self, process_variance, measurement_variance, estimation_error, initial_estimate):
        self.process_variance = process_variance
        self.measurement_variance = measurement_variance
        self.estimation_error = estimation_error
        self.estimate = initial_estimate

    def update(self, measurement):
        kalman_gain = self.estimation_error / (self.estimation_error + self.measurement_variance)
        self.estimate = self.estimate + kalman_gain * (measurement - self.estimate)
        self.estimation_error = (1 - kalman_gain) * self.estimation_error + abs(self.estimate) * self.process_variance
        return self.estimate

# Beispielhafte Parameter für den Kalman-Filter
process_variance = 1e-5
measurement_variance = 0.1
initial_estimate_x = 1.7
initial_estimate_y = 0.3

# Initialisierung der Kalman-Filter für X- und Y-Koordinaten
kalman_filter_x = KalmanFilter(process_variance, measurement_variance, 1.0, initial_estimate_x)
kalman_filter_y = KalmanFilter(process_variance, measurement_variance, 1.0, initial_estimate_y)

# Liste der gemessenen Tag-Positionen (X, Y)
positions = [
    (1.8, 0.6), (1.8, 0.6), (1.7, 0.6), (1.7, 0.5), (4.0, 0.5),
    (1.6, 0.5), (1.5, 0.7), (1.4, 1.0), (1.3, 1.0), (1.5, 0.8),
    (2.4, 0.72), (1.5, 0.8), (1.3, 0.5), (4.0, 0.4), (1.2, 0.2), (1.2, 0.2),
    (1.7, 0.7), (1.8, 0.9), (2.0, 1.0), (4.5, 0.2), (2.1, 1.2),
    (1.04, 1.2), (2.2, 1.3), (1.0, 1.0), (2.1, 1.2), (2.0, 1.9), (0.9, 0.5),
    (1.8, 0.7), (1.9, 0.6), (1.7, 0.7), (1.6, 0.4), (1.5, 0.7),
    (1.4, 0.9), (1.3, 0.8), (3.84, 0.48), (1.5, 0.9), (1.4, 0.7),
    (1.2, 0.3), (1.8, 0.8), (2.0, 1.1), (2.64, 1.56), (2.1, 1.3),
    (2.2, 1.4), (2.0, 1.8), (1.8, 0.5), (1.9, 0.5), (1.6, 0.6),
    (1.7, 0.8), (1.3, 0.4), (0.72, 0.4), (1.2, 0.4), (1.1, 0.6),
    (1.7, 0.9), (1.6, 0.6), (1.4, 0.6),
]

# Leere Liste, um die Ausreißer zu speichern
outliers = []
rolling_window = 10  # Erhöhtes Fenster für mehr Stabilität
recent_measurements_x = []
recent_measurements_y = []

# Schleife durch die gemessenen Positionsdaten
for pos in positions:
    measured_x, measured_y = pos

    # Aktualisiere die Schätzung für X- und Y-Position basierend auf der neuen Messung
    estimated_x = kalman_filter_x.update(measured_x)
    estimated_y = kalman_filter_y.update(measured_y)

    # Füge die aktuellen Messungen in die Listen ein und begrenze die Größe des Fensters
    recent_measurements_x.append(measured_x)
    recent_measurements_y.append(measured_y)
    if len(recent_measurements_x) > rolling_window:
        recent_measurements_x.pop(0)
        recent_measurements_y.pop(0)

    # Berechne den gleitenden Mittelwert und die Standardabweichung
    mean_x = np.mean(recent_measurements_x)
    std_x = np.std(recent_measurements_x)
    mean_y = np.mean(recent_measurements_y)
    std_y = np.std(recent_measurements_y)

    # Angepasste dynamische Schwellenwerte basierend auf der Standardabweichung und Schätzfehler
    threshold_x = max(1.5 * std_x, 1.5 * np.sqrt(kalman_filter_x.estimation_error), 0.4)
    threshold_y = max(1.5 * std_y, 1.5 * np.sqrt(kalman_filter_y.estimation_error), 0.4)

    # Überprüfung der Abweichung zur Identifikation von Ausreißern
    if abs(measured_x - estimated_x) > threshold_x or abs(measured_y - estimated_y) > threshold_y:
        outliers.append(pos)

# Ausgabe der identifizierten Ausreißer
print("Identifizierte Ausreißer:")
print(outliers)
