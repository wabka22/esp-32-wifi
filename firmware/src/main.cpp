#include <WiFi.h>

const char* ssid     = "MTSRouter_28F9";
const char* password = "66705895";

IPAddress serverIP(192, 168, 1, 169);
const uint16_t serverPort = 8888;

const int LED_PIN = 2;

WiFiClient client;

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println("\nWiFi connected!");
  Serial.print("ESP IP address: ");
  Serial.println(WiFi.localIP());
}

void printNetworkInfo() {
  Serial.println("=== Network Info ===");
  Serial.print("ESP32 IP: ");
  Serial.println(WiFi.localIP());
  Serial.print("Server IP: ");
  Serial.println(serverIP);
  Serial.print("Gateway: ");
  Serial.println(WiFi.gatewayIP());
  Serial.print("Subnet: ");
  Serial.println(WiFi.subnetMask());
  Serial.println("====================");
}

void loop() {
  if (!client.connected()) {
    Serial.println("Connecting to server...");
    
    if (client.connect(serverIP, serverPort)) {
      Serial.println("Connected to server!");
    } else {
      Serial.println("Connection failed!");
      delay(2000);
      return;
    }
  }

  String msg = "Toggle LED\n";
  client.print(msg);
  Serial.println("Sent: " + msg);

  unsigned long timeout = millis();
  while (client.available() == 0) {
    if (millis() - timeout > 3000) {
      Serial.println("Response timeout!");
      client.stop();
      return;
    }
    delay(100);
  }

  while (client.available()) {
    String response = client.readStringUntil('\n');
    Serial.println("Received: " + response);
    
    if (response.indexOf("ON") > 0) {
      digitalWrite(LED_PIN, HIGH);
      Serial.println("LED turned ON");
    } else if (response.indexOf("OFF") > 0) {
      digitalWrite(LED_PIN, LOW);
      Serial.println("LED turned OFF");
    }
  }

  delay(5000);
}