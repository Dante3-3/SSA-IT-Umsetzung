#include <WiFi.h>
#include <esp_now.h>
#include <SPI.h>
#include "DW1000Ranging.h"

#define ANCHOR_ADD "84:17:5B:D5:A9:9A:E2:9C"

#define SPI_SCK 18
#define SPI_MISO 19
#define SPI_MOSI 23
#define DW_CS 4

const uint8_t PIN_RST = 27;
const uint8_t PIN_IRQ = 2;  // Ändere auf GPIO 2
const uint8_t BUTTON_PIN = 1; // Taster-Pin

uint8_t broadcastAddress[] = {0xC8, 0x2E, 0x18, 0xAC, 0xE0, 0x2C};

typedef struct struct_message {
  int b;
} struct_message;

struct_message myData;

esp_now_peer_info_t peerInfo;
SPIClass hspi(HSPI); // HSPI für DW1000

void OnDataSent(const uint8_t *mac_addr, esp_now_send_status_t status) {
    Serial.println(status == ESP_NOW_SEND_SUCCESS ? "Delivery Success" : "Delivery Fail");
}

void setup() {
    Serial.begin(115200);
    pinMode(BUTTON_PIN, INPUT_PULLUP);

    WiFi.mode(WIFI_STA);
    WiFi.setSleep(false);
    WiFi.setChannel(1);

    if (esp_now_init() != ESP_OK) {
        Serial.println("Error initializing ESP-NOW");
        return;
    }

    esp_now_register_send_cb(OnDataSent);
    memcpy(peerInfo.peer_addr, broadcastAddress, 6);
    peerInfo.channel = 0;
    peerInfo.encrypt = false;

    if (esp_now_add_peer(&peerInfo) != ESP_OK) {
        Serial.println("Failed to add peer");
        return;
    }

    hspi.begin(SPI_SCK, SPI_MISO, SPI_MOSI, DW_CS);
    DW1000Ranging.initCommunication(PIN_RST, DW_CS, PIN_IRQ);
    DW1000Ranging.attachNewRange(newRange);
    DW1000Ranging.attachBlinkDevice(newBlink);
    DW1000Ranging.attachInactiveDevice(inactiveDevice);
    DW1000Ranging.startAsAnchor(ANCHOR_ADD, DW1000.MODE_LONGDATA_RANGE_LOWPOWER, false);
}

void loop() {
    DW1000Ranging.loop();

    if (digitalRead(BUTTON_PIN) == LOW) {
        Serial.println("Button Pressed! Sending Message...");
        myData.b = 1;

        esp_err_t result = esp_now_send(broadcastAddress, (uint8_t *)&myData, sizeof(myData));
        Serial.println(result == ESP_OK ? "Message Sent" : "Message Sending Failed");

        delay(500);
    }
}

void newRange() {
    hspi.beginTransaction(SPISettings(16000000, MSBFIRST, SPI_MODE0));
    Serial.print("from: ");
    Serial.print(DW1000Ranging.getDistantDevice()->getShortAddress(), HEX);
    Serial.print("\t Range: ");
    Serial.print(DW1000Ranging.getDistantDevice()->getRange());
    Serial.println(" m");
    hspi.endTransaction();
}

void newBlink(DW1000Device *device) {
    Serial.print("blink; 1 device added! -> short: ");
    Serial.println(device->getShortAddress(), HEX);
}

void inactiveDevice(DW1000Device *device) {
    Serial.print("delete inactive device: ");
    Serial.println(device->getShortAddress(), HEX);
}
