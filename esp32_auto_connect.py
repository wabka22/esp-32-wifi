import os
import sys
import socket
import subprocess
import time

SSID = "karch_eeg_88005553535"
PASSWORD = "12345678"
ESP_IP = "192.168.4.1"
PORT = 8888


def scan_networks():
    """Сканирует доступные Wi-Fi сети и возвращает список SSID"""
    if sys.platform.startswith("linux"):
        result = subprocess.run(["nmcli", "-t", "-f", "SSID", "dev", "wifi"], capture_output=True, text=True)
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]
    elif sys.platform.startswith("win"):
        result = subprocess.run(["netsh", "wlan", "show", "networks"], capture_output=True, text=True)
        networks = []
        for line in result.stdout.splitlines():
            if "SSID" in line:
                parts = line.split(":", 1)
                if len(parts) == 2:
                    networks.append(parts[1].strip())
        return networks
    else:
        print("Unsupported OS.")
        return []


def connect_to_wifi():
    """Подключается к ESP Wi-Fi"""
    if sys.platform.startswith("linux"):
        print(f"🔍 Подключаемся к {SSID}...")
        subprocess.run(["nmcli", "dev", "wifi", "connect", SSID, "password", PASSWORD])
    elif sys.platform.startswith("win"):
        print(f"⚙️ Подключаемся к {SSID} (Windows)...")
        profile_xml = f"""
        <WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
            <name>{SSID}</name>
            <SSIDConfig>
                <SSID>
                    <name>{SSID}</name>
                </SSID>
            </SSIDConfig>
            <connectionType>ESS</connectionType>
            <connectionMode>manual</connectionMode>
            <MSM>
                <security>
                    <authEncryption>
                        <authentication>WPA2PSK</authentication>
                        <encryption>AES</encryption>
                        <useOneX>false</useOneX>
                    </authEncryption>
                    <sharedKey>
                        <keyType>passPhrase</keyType>
                        <protected>false</protected>
                        <keyMaterial>{PASSWORD}</keyMaterial>
                    </sharedKey>
                </security>
            </MSM>
        </WLANProfile>
        """.strip()

        with open(f"{SSID}.xml", "w") as f:
            f.write(profile_xml)

        subprocess.run(["netsh", "wlan", "add", "profile", f"filename={SSID}.xml", "user=all"], stdout=subprocess.DEVNULL)
        subprocess.run(["netsh", "wlan", "connect", f"name={SSID}"], stdout=subprocess.DEVNULL)
    else:
        print("❌ Unsupported OS.")
        return

    print("⏳ Ожидаем подключение к сети...")
    for i in range(10):
        time.sleep(1)
        print(f"⏱️  Проверка соединения... ({i+1}/10)")
        if check_connected():
            print("✅ Wi-Fi подключен!")
            return
    print("⚠️  Не удалось убедиться в подключении. Продолжаем...")


def check_connected():
    """Проверяет, получен ли IP от ESP (проверка ping)"""
    try:
        if sys.platform.startswith("win"):
            result = subprocess.run(["ping", "-n", "1", ESP_IP], stdout=subprocess.DEVNULL)
        else:
            result = subprocess.run(["ping", "-c", "1", ESP_IP], stdout=subprocess.DEVNULL)
        return result.returncode == 0
    except Exception:
        return False


def connect_to_esp():
    """Подключается к ESP по TCP"""
    try:
        print(f"🔌 Пытаемся подключиться к ESP32 по адресу {ESP_IP}:{PORT}...")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect((ESP_IP, PORT))
        print("✅ Успешное соединение с ESP32!")
        s.sendall(b"STATUS\n")
        data = s.recv(1024).decode("utf-8")
        print("Ответ ESP:", data)
        s.close()
    except Exception as e:
        print("❌ Не удалось подключиться к ESP32:", e)


def main():
    print("=== ESP32 Auto-Connector ===")
    networks = scan_networks()

    if SSID in networks:
        print(f"✅ Найдена сеть ESP32: {SSID}")
        connect_to_wifi()
        connect_to_esp()
    else:
        print(f"❌ Сеть '{SSID}' не найдена. Попробуйте приблизиться к ESP32 или перезапустить её.")


if __name__ == "__main__":
    main()
