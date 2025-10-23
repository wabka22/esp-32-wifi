#include <WiFi.h>
#include <WiFiClient.h>
#include <WiFiAP.h>
#include <Preferences.h>

Preferences prefs;
WiFiServer server(8888);

// Переменные для управления подключением
unsigned long lastConnectionAttempt = 0;
const unsigned long CONNECTION_RETRY_INTERVAL = 30000; // 30 секунд между попытками
bool isConnecting = false;
String savedSSID = "";
String savedPass = "";

void connectToWiFi();
void printNetworkStatus(WiFiClient& client);

void setup() {
  Serial.begin(115200);
  prefs.begin("wifi", false);

  // Считываем сохранённые данные Wi-Fi
  savedSSID = prefs.getString("ssid", "");
  savedPass = prefs.getString("pass", "");

  // Включаем оба режима: STA + AP
  WiFi.mode(WIFI_AP_STA);
  WiFi.softAP("karch_eeg_88005553535", "12345678"); // постоянная точка доступа ESP

  Serial.print("Access Point started. AP IP: ");
  Serial.println(WiFi.softAPIP());

  // Начинаем первую попытку подключения, если есть сохраненные данные
  if (savedSSID != "") {
    connectToWiFi();
  } else {
    Serial.println("No saved Wi-Fi credentials. Waiting for setup...");
  }

  server.begin();
}

void connectToWiFi() {
  if (savedSSID == "" || isConnecting) {
    return;
  }
  
  Serial.printf("Attempting to connect to Wi-Fi: %s\n", savedSSID.c_str());
  isConnecting = true;
  
  WiFi.begin(savedSSID.c_str(), savedPass.c_str());
  lastConnectionAttempt = millis();
}

void handleWiFiReconnection() {
  // Если не подключены и прошло достаточно времени с последней попытки
  if (WiFi.status() != WL_CONNECTED && !isConnecting) {
    if (millis() - lastConnectionAttempt >= CONNECTION_RETRY_INTERVAL) {
      if (savedSSID != "") {
        Serial.println("Reconnecting to Wi-Fi...");
        connectToWiFi();
      }
    }
  }
  
  // Проверяем статус текущего подключения
  if (isConnecting) {
    if (WiFi.status() == WL_CONNECTED) {
      Serial.println("\n✅ Connected to Wi-Fi!");
      Serial.print("Local IP: ");
      Serial.println(WiFi.localIP());
      isConnecting = false;
    } else if (millis() - lastConnectionAttempt > 15000) { // 15 секунд таймаут
      Serial.println("\n❌ Failed to connect to Wi-Fi. Will retry in 30 seconds.");
      isConnecting = false;
    }
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
    client.print("RSSI: "); client.println(WiFi.RSSI());
  } else {
    client.print("Connection status: ");
    switch (WiFi.status()) {
      case WL_IDLE_STATUS: client.println("IDLE"); break;
      case WL_NO_SSID_AVAIL: client.println("SSID not available"); break;
      case WL_SCAN_COMPLETED: client.println("Scan completed"); break;
      case WL_CONNECT_FAILED: client.println("Connect failed"); break;
      case WL_CONNECTION_LOST: client.println("Connection lost"); break;
      case WL_DISCONNECTED: client.println("Disconnected"); break;
      default: client.println("Unknown"); break;
    }
    
    if (savedSSID != "") {
      client.print("Saved SSID: "); client.println(savedSSID);
      client.print("Next retry in: "); 
      client.print((CONNECTION_RETRY_INTERVAL - (millis() - lastConnectionAttempt)) / 1000);
      client.println(" seconds");
    }
  }
  client.println("=============================");
}

void loop() {
  // Постоянно проверяем и переподключаемся к Wi-Fi
  handleWiFiReconnection();
  
  // Обрабатываем клиентские подключения
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
        
        // Сохраняем новые учетные данные
        prefs.putString("ssid", ssid);
        prefs.putString("pass", pass);
        savedSSID = ssid;
        savedPass = pass;
        
        client.println("Credentials saved. Connecting...");
        
        // Немедленно начинаем попытку подключения
        connectToWiFi();
        
      } else {
        client.println("Invalid credentials format.");
      }
    } else if (command == "STATUS") {
      printNetworkStatus(client);
    } else if (command == "FORCE_RECONNECT") {
      client.println("Forcing reconnection...");
      connectToWiFi();
    } else {
      client.println("Unknown command. Use SET, STATUS or FORCE_RECONNECT.");
    }

    client.stop();
    Serial.println("Client disconnected.\n");
  }

  // Периодически выводим статус в Serial
  static unsigned long lastStatusPrint = 0;
  if (millis() - lastStatusPrint > 10000) { // Каждые 10 секунд
    lastStatusPrint = millis();
    
    if (savedSSID != "" && WiFi.status() != WL_CONNECTED && !isConnecting) {
      Serial.print("Wi-Fi disconnected. Next retry in: ");
      Serial.print((CONNECTION_RETRY_INTERVAL - (millis() - lastConnectionAttempt)) / 1000);
      Serial.println(" seconds");
    }
  }
}