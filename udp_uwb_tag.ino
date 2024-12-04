#include <SPI.h>
#include <DW1000Ranging.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include "link.h"
#include <math.h>

#define SPI_SCK 18
#define SPI_MISO 19
#define SPI_MOSI 23
#define DW_CS 4
#define PIN_RST 27
#define PIN_IRQ 34

#define FIELD_WIDTH 3.0  // Spielfeldbreite in Metern
#define FIELD_HEIGHT 5.0 // Spielfeldhöhe in Metern
#define DISTANCE_A1_A2 3.0

#define VIBRO1 12

void setup() {
    Serial.begin(115200);

    pinMode(VIBRO1, OUTPUT);

    // SPI und UWB initialisieren
    SPI.begin(SPI_SCK, SPI_MISO, SPI_MOSI);
    DW1000Ranging.initCommunication(PIN_RST, DW_CS, PIN_IRQ);
    DW1000Ranging.attachNewRange(newRange);
    DW1000Ranging.attachNewDevice(newDevice);
    DW1000Ranging.attachInactiveDevice(inactiveDevice);

    // UWB als Tag starten
    DW1000Ranging.startAsTag("7D:00:22:EA:82:60:3B:9C", DW1000.MODE_LONGDATA_RANGE_LOWPOWER);
}

void loop() {
    DW1000Ranging.loop();
}

void newRange() {
    double a2_range = DW1000Ranging.getDistantDevice()->getRange();
    double a1_range = DISTANCE_A1_A2; // Der Abstand zum ersten Anker wird als Konstante festgelegt

    double tag_x = 0, tag_y = 0;

    if (a2_range > 0 && a1_range > 0) {
        calculateTagPosition(a2_range, a1_range, DISTANCE_A1_A2, &tag_x, &tag_y);

        Serial.print("Tag Position: x = ");
        Serial.print(tag_x);
        Serial.print(", y = ");
        Serial.println(tag_y);

        // Überprüfen, ob der Tag außerhalb des Spielfelds ist
        if (is_out_of_bounds(tag_x, tag_y)) {
            Serial.println("Der Tag ist außerhalb des Spielfelds.");
            vibrieren(VIBRO1, true);
        } else {
            Serial.println("Der Tag ist innerhalb des Spielfelds.");
            vibrieren(VIBRO1, false);
        }
    } else {
        Serial.println("Ungültige Entfernungsdaten, keine Berechnung der Position möglich.");
    }
}

void calculateTagPosition(double a, double b, double c, double *x, double *y) {
    if (b == 0 || c == 0) {
        Serial.println("Fehler: b oder c ist 0, Berechnung nicht möglich.");
        *x = 0;
        *y = 0;
        return;
    }

    double cos_a = (b * b + c * c - a * a) / (2 * b * c);
    cos_a = fmax(-1.0, fmin(1.0, cos_a)); // Begrenzen auf [-1, 1]

    *x = b * cos_a;
    *y = sqrt(fmax(0.0, b * b - (*x) * (*x))); // Sicherstellen, dass der Wurzelwert positiv ist
}

bool is_out_of_bounds(double tag_x, double tag_y) {
    return tag_x < 0 || tag_x > FIELD_WIDTH || tag_y < 0 || tag_y > FIELD_HEIGHT;
}

void vibrieren(byte pin, boolean aktiv) {
    if (aktiv) {
        digitalWrite(pin, HIGH);
        delay(50);
        digitalWrite(pin, LOW);
        delay(50);
    } else {
        digitalWrite(pin, LOW);
    }
}

void newDevice(DW1000Device *device) {
    Serial.print("New device added! Short address: ");
    Serial.println(device->getShortAddress(), HEX);
}

void inactiveDevice(DW1000Device *device) {
    Serial.print("Inactive device removed: ");
    Serial.println(device->getShortAddress(), HEX);
}
