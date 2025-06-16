#include <Wire.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include "MAX30105.h"

const char* ssid = "ELTX-2.4GHz_WiFi_3668";         // здесь нужно поставить свой  Wi-Fi
const char* password = "GP2F081696"; // здесь введите свой пароль
const char* serverName = "http://192.168.1.11:5000/pulse"; // замените <IP> на локальный IP адрес

MAX30105 sensor;

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");

  if (!sensor.begin(Wire, I2C_SPEED_STANDARD)) {
    Serial.println("MAX30102 not found");
    while (1);
  } else {
    Serial.println("MAX30102 found");
  }

  sensor.setup();
  Serial.println("Sensor ready");
}

void loop() {
  long ir = sensor.getIR();
  long red = sensor.getRed();
  int pulse = (int)(red / 1000);  // примерная конвертация

  Serial.print("Sending pulse: ");
  Serial.println(pulse);

  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverName);
    http.addHeader("Content-Type", "application/json");

    String json = "{\"pulse\":" + String(pulse) + "}";
    int httpResponseCode = http.POST(json);

    Serial.print("Response code: ");
    Serial.println(httpResponseCode);
    http.end();
  }

  delay(5000);
}
