#include <WiFi.h>
#include <WiFiClient.h>
#include <WiFiAP.h>
#include <Preferences.h>

Preferences prefs;
WiFiServer server(8888);

void connectToWiFi(const char* ssid, const char* password);
void printNetworkStatus(WiFiClient& client);

void setup() {
  Serial.begin(115200);
  prefs.begin("wifi", false);

  // Считываем сохранённые данные Wi-Fi
  String ssid = prefs.getString("ssid", "");
  String pass = prefs.getString("pass", "");

  // Включаем оба режима: STA + AP
  WiFi.mode(WIFI_AP_STA);
  WiFi.softAP("karch_eeg_88005553535", "12345678"); // постоянная точка доступа ESP

  Serial.print("Access Point started. AP IP: ");
  Serial.println(WiFi.softAPIP());

  if (ssid != "") {
    connectToWiFi(ssid.c_str(), pass.c_str());
  } else {
    Serial.println("No saved Wi-Fi credentials. Waiting for setup...");
  }

  server.begin();
}

void connectToWiFi(const char* ssid, const char* password) {
  Serial.printf("Connecting to Wi-Fi: %s\n", ssid);
  WiFi.begin(ssid, password);

  unsigned long startAttemptTime = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - startAttemptTime < 15000) {
    Serial.print(".");
    delay(500);
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nConnected to Wi-Fi!");
    Serial.print("Local IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\nFailed to connect to Wi-Fi.");
  }
}

void printNetworkStatus(WiFiClient& client) {
  client.println("=== ESP32 Network Status ===");
  client.print("AP SSID: "); client.println("karch_eeg_88005553535");
  client.print("AP IP: "); client.println(WiFi.softAPIP());
  client.print("Station connected: ");
  client.println(WiFi.status() == WL_CONNECTED ? "YES" : "NO");
  if (WiFi.status() == WL_CONNECTED) {
    client.print("Wi-Fi SSID: "); client.println(WiFi.SSID());
    client.print("Wi-Fi IP: "); client.println(WiFi.localIP());
    client.print("Gateway: "); client.println(WiFi.gatewayIP());
  }
  client.println("=============================");
}

void loop() {
  WiFiClient client = server.available();
  if (client) {
    Serial.println("Client connected.");

    String command = client.readStringUntil('\n');
    command.trim();

    if (command.startsWith("SET")) {
      // Формат: SET\nSSID\nPASS\n
      String ssid = client.readStringUntil('\n');
      String pass = client.readStringUntil('\n');
      ssid.trim();
      pass.trim();

      if (ssid.length() > 0 && pass.length() > 0) {
        Serial.printf("Received credentials:\nSSID: %s\nPASS: %s\n", ssid.c_str(), pass.c_str());
        prefs.putString("ssid", ssid);
        prefs.putString("pass", pass);
        client.println("Credentials saved. Connecting...");
        connectToWiFi(ssid.c_str(), pass.c_str());
      } else {
        client.println("Invalid credentials format.");
      }
    } else if (command == "STATUS") {
      printNetworkStatus(client);
    } else {
      client.println("Unknown command. Use SET or STATUS.");
    }

    client.stop();
    Serial.println("Client disconnected.\n");
  }
}
