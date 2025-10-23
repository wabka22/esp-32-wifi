import subprocess
import platform
import time
import json
import sys
from datetime import datetime

CONFIG_FILE = "config.json"

def log(msg, level="INFO"):
    ts = datetime.now().strftime("%H:%M:%S")
    colors = {
        "INFO": "\033[94m",
        "SUCCESS": "\033[92m",
        "WARN": "\033[93m",
        "ERROR": "\033[91m"
    }
    color = colors.get(level, "\033[0m")
    print(f"{color}[{ts}] [{level}] {msg}\033[0m")


def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        log(f"Файл {CONFIG_FILE} не найден. Создайте его с нужными Wi-Fi данными.", "ERROR")
        sys.exit(1)


def scan_networks():
    """Сканирует сети Wi-Fi и возвращает список SSID"""
    os_name = platform.system()
    try:
        if os_name == "Windows":
            result = subprocess.run(["netsh", "wlan", "show", "networks", "mode=Bssid"],
                                    capture_output=True, text=True, encoding="cp866")
        else:
            result = subprocess.run(["nmcli", "-t", "-f", "SSID", "dev", "wifi"],
                                    capture_output=True, text=True)

        if result.returncode != 0 or not result.stdout:
            return []

        networks = []
        for line in result.stdout.splitlines():
            if os_name == "Windows":
                if "SSID" in line:
                    ssid = line.split(":", 1)[1].strip()
                    if ssid:
                        networks.append(ssid)
            else:
                if line.strip():
                    networks.append(line.strip())
        return list(set(networks))
    except Exception as e:
        log(f"Ошибка при сканировании Wi-Fi: {e}", "ERROR")
        return []


def connect_to_network(ssid, password):
    os_name = platform.system()
    log(f"Подключение к сети {ssid}...", "INFO")

    try:
        if os_name == "Windows":
            subprocess.run(["netsh", "wlan", "connect", f"name={ssid}"], check=False)
        else:
            subprocess.run(["nmcli", "d", "wifi", "connect", ssid, "password", password], check=False)
        time.sleep(5)
        log(f"Подключение к {ssid} выполнено (или в процессе)...", "SUCCESS")
    except Exception as e:
        log(f"Ошибка подключения: {e}", "ERROR")


def send_wifi_credentials_to_esp(pc_ssid, pc_password):
    """Имитирует отправку данных на ESP (позже можно будет сделать через сокет или HTTP)."""
    log(f"Отправка данных на ESP...", "INFO")
    log(f"SSID ПК: {pc_ssid}, пароль: {pc_password}", "SUCCESS")
    time.sleep(2)
    log("Данные успешно переданы ESP ✅", "SUCCESS")


def main():
    config = load_config()
    esp_name = config["esp_network_name"]
    esp_pass = config["esp_network_password"]
    pc_ssid = config["pc_wifi_ssid"]
    pc_pass = config["pc_wifi_password"]

    log("=== ESP32 Auto-Connector ===", "INFO")

    while True:
        networks = scan_networks()
        if not networks:
            log("Нет доступных сетей. Повтор через 5 секунд...", "WARN")
            time.sleep(5)
            continue

        if esp_name in networks:
            log(f"Обнаружена ESP-сеть: {esp_name}", "SUCCESS")
            connect_to_network(esp_name, esp_pass)
            send_wifi_credentials_to_esp(pc_ssid, pc_pass)
            log("Ожидание 10 секунд перед повторной проверкой...", "INFO")
            time.sleep(10)
        else:
            log(f"ESP-сеть '{esp_name}' не найдена. Повтор через 5 секунд...", "WARN")
            time.sleep(5)


if __name__ == "__main__":
    main()
