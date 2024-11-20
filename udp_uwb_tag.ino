/*
For ESP32 UWB or ESP32 UWB Pro
dstoilovski
*/

#include <SPI.h>
#include <DW1000Ranging.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include "link.h"

#define SPI_SCK 18
#define SPI_MISO 19
#define SPI_MOSI 23
#define DW_CS 4
#define PIN_RST 27
#define PIN_IRQ 34

/**
 * Gustav sein Code
*/
#define VIBRO1 12

TaskHandle_t Task1;

int counter = 0;


const char *ssid = "iPhone von Toma";
const char *password = "vaskoaki";
const char *host = "172.20.10.3"; // Python Server IP
const int udp_port = 8080;        // UDP Port für Kommunikation (Python auch auf diesen Port setzen)

WiFiUDP udp;
struct MyLink *uwb_data;
int index_num = 0;
long runtime = 0;
String all_json = "";

void setup()
{
    Serial.begin(115200);

    //Von G
    pinMode(VIBRO1, OUTPUT);

    // WiFi-Verbindung herstellen
    WiFi.mode(WIFI_STA);
    WiFi.setSleep(false);
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED)
    {
        delay(500);
        Serial.print(".");
    }
    Serial.println("Connected to WiFi");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());

    // SPI und UWB initialisieren
    SPI.begin(SPI_SCK, SPI_MISO, SPI_MOSI);
    DW1000Ranging.initCommunication(PIN_RST, DW_CS, PIN_IRQ);
    DW1000Ranging.attachNewRange(newRange);
    DW1000Ranging.attachNewDevice(newDevice);
    DW1000Ranging.attachInactiveDevice(inactiveDevice);

    // UWB als Tag starten
    DW1000Ranging.startAsTag("7D:00:22:EA:82:60:3B:9C", DW1000.MODE_LONGDATA_RANGE_LOWPOWER);

    // UWB-Daten initialisieren
    uwb_data = init_link();

    udp.begin(udp_port);
}

void loop()
{
    DW1000Ranging.loop();
    if ((millis() - runtime) > 1000)
    {
        make_link_json(uwb_data, &all_json);
        send_udp(&all_json);
        runtime = millis();
    }

    int packetSize = udp.parsePacket();
    if (packetSize) {
        char incomingPacket[255];
        int len = udp.read(incomingPacket, 255);
        incomingPacket[len] = 0;  // Null-terminate the packet

        String message = String(incomingPacket);
        Serial.println("Received: " + message);

        if(message == "draußen"){
          Serial.println("Du bist draußen");
          //Von G
          vibrieren(12, true);
        } else if(message == "drinnen"){
          Serial.println("Wieder Drinnen");
          vibrieren(12, false);
        } else {
          Serial.println("Unbekannte Nachricht");
        }
    }
}

void vibrieren(byte pin, boolean aktiv) {
  if(!Task1) {
    xTaskCreatePinnedToCore(
    codeVibrieren,
    "vibrieren1task",
    1000,
    NULL,
    1,
    &Task1,
    0);
    vTaskSuspend(Task1);
  }
  if(aktiv) {
    vTaskResume(Task1);
  } else {
    vTaskSuspend(Task1);
    digitalWrite(VIBRO1, LOW);
  }
}

void codeVibrieren( void * parameter )
{
  Serial.println("Vibration...");
  for(;;) {
    digitalWrite(VIBRO1, HIGH);
    delay(50);
  }

}

void newRange()
{
    Serial.print("from: ");
    Serial.print(DW1000Ranging.getDistantDevice()->getShortAddress(), HEX);
    Serial.print("\\t Range: ");
    Serial.print(DW1000Ranging.getDistantDevice()->getRange());
    Serial.print(" m");
    Serial.print("\\t RX power: ");
    Serial.print(DW1000Ranging.getDistantDevice()->getRXPower());
    Serial.println(" dBm");

    // Link-Daten aktualisieren
    fresh_link(uwb_data, DW1000Ranging.getDistantDevice()->getShortAddress(), DW1000Ranging.getDistantDevice()->getRange(), DW1000Ranging.getDistantDevice()->getRXPower());
}

void newDevice(DW1000Device *device)
{
    Serial.print("New device added! Short address: ");
    Serial.println(device->getShortAddress(), HEX);

    // Neues Gerät zum Link hinzufügen
    add_link(uwb_data, device->getShortAddress());
}

void inactiveDevice(DW1000Device *device)
{
    Serial.print("Inactive device removed: ");
    Serial.println(device->getShortAddress(), HEX);

    // Inaktives Gerät aus Link entfernen
    delete_link(uwb_data, device->getShortAddress());
}

// UDP-Daten senden
void send_udp(String *msg_json)
{
    udp.beginPacket(host, udp_port); // Senden an das Host-Gerät (Python-Server) über Port
    udp.print(*msg_json);            // Nachricht (JSON) senden
    udp.endPacket();                 // Paket abschließen
    Serial.println("UDP sent: " + *msg_json);
}