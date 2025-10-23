# ⚡ ESP32 ↔ PC Wi-Fi Communication

Проект для обмена данными между **ESP32** и **ПК** по Wi-Fi.  
ESP32 создаёт собственную точку доступа или подключается к роутеру, а ПК находит её и обменивается данными через TCP.

---

## 📁 Структура проекта

- `firmware/src/main.cpp` — код прошивки ESP32 (PlatformIO, C++)  
- `pc/esp32_auto_connect.py` — Python-скрипт для поиска и подключения к ESP32  

---

## ⚙️ Настройка ESP32

В файле `firmware/src/main.cpp` можно указать ваши параметры:

```cpp
const char* ssid     = "Ваш_SSID";      // Wi-Fi сеть
const char* password = "Ваш_PASSWORD";  // Пароль
IPAddress serverIP(192, 168, 1, 100);   // IP ПК с сервером
const uint16_t serverPort = 8888;       // Порт сервера
```

По умолчанию ESP32 поднимает точку доступа:

```
SSID: karch_eeg_88005553535  
Пароль: 12345678  
IP: 192.168.4.1
```

---

## 🚀 Сборка и прошивка

```bash
cd firmware
platformio run                   # сборка
platformio run --target upload   # прошивка
platformio device monitor -b 115200   # мониторинг
```

---

## 🐍 Подключение с ПК

На ПК используется скрипт `esp32_auto_connect.py`:
- Сканирует Wi-Fi сети  
- Находит ESP32 (`karch_eeg_88005553535`)  
- Подключается к ней по паролю `12345678`  
- Устанавливает TCP-соединение по адресу `192.168.4.1:8888`

Запуск:

```bash
cd pc
python esp32_auto_connect.py
```

---

## 🔧 Обновление параметров прошивки (bash-утилита)

```bash
#!/usr/bin/env bash
# usage: ./set_creds.sh "MySSID" "MyPass" "192.168.1.50" "8888"

SSID="$1"
PASS="$2"
IP="$3"
PORT="$4"
FILE="firmware/src/main.cpp"

sed -i "s/const char\* ssid.*/const char* ssid = \"$SSID\";/" "$FILE"
sed -i "s/const char\* password.*/const char* password = \"$PASS\";/" "$FILE"
sed -i "s/IPAddress serverIP.*/IPAddress serverIP($(echo $IP | sed 's/\./, /g'));/" "$FILE"
sed -i "s/const uint16_t serverPort.*/const uint16_t serverPort = $PORT;/" "$FILE"

echo "✅ Обновлено в $FILE"
```

Использование:

```bash
chmod +x set_creds.sh
./set_creds.sh "MyWiFi" "12345678" "192.168.1.50" "8888"
```

---

## 🧩 Примечания

- Если ESP32 в режиме **точки доступа**, её IP всегда `192.168.4.1`.  
- При работе через роутер укажи IP ПК вручную.  
- TCP-порт `8888` должен быть открыт.  

---
