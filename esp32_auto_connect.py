import subprocess
import sys
import time

def scan_networks():
    """Сканирует доступные Wi-Fi сети и возвращает список SSID"""
    if sys.platform.startswith("linux"):
        result = subprocess.run(
            ["nmcli", "-t", "-f", "SSID", "dev", "wifi"],
            capture_output=True, text=True
        )
        networks = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    
    elif sys.platform.startswith("win"):
        print("🔍 Сканируем сети Wi-Fi...")
        try:
            # Первый способ - стандартная команда
            result = subprocess.run(
                ["netsh", "wlan", "show", "networks"],
                capture_output=True, text=True, encoding='cp866', timeout=30
            )
            
            networks = []
            for line in result.stdout.splitlines():
                line = line.strip()
                if line.startswith("SSID") and "BSSID" not in line:
                    parts = line.split(':', 1)
                    if len(parts) > 1:
                        ssid = parts[1].strip()
                        if ssid and ssid not in networks:
                            networks.append(ssid)
            
            # Если не нашли сеть, пробуем альтернативный метод
            if not networks:
                print("Пробуем альтернативный метод сканирования...")
                networks = scan_networks_alternative()
                
        except Exception as e:
            print(f"❌ Ошибка сканирования: {e}")
            networks = []
    
    else:
        print("❌ Unsupported OS.")
        networks = []
    
    return networks

def scan_networks_alternative():
    """Альтернативный метод сканирования для Windows"""
    try:
        result = subprocess.run(
            ["netsh", "wlan", "show", "all"],
            capture_output=True, text=True, encoding='cp866', timeout=30
        )
        
        networks = []
        in_network_section = False
        
        for line in result.stdout.splitlines():
            line = line.strip()
            if "Сетевые параметры" in line or "Network parameters" in line:
                in_network_section = True
            elif line.startswith("====") and in_network_section:
                in_network_section = False
            elif in_network_section and "SSID" in line and "BSSID" not in line:
                parts = line.split(':', 1)
                if len(parts) > 1:
                    ssid = parts[1].strip()
                    if ssid and ssid not in networks:
                        networks.append(ssid)
        
        return networks
        
    except Exception as e:
        print(f"❌ Ошибка альтернативного сканирования: {e}")
        return []

def check_specific_network(target_ssid="karch_eeg_88005553535"):
    """Проверяет наличие конкретной сети"""
    print(f"🔎 Ищем сеть: '{target_ssid}'")
    networks = scan_networks()
    
    print(f"📶 Всего найдено сетей: {len(networks)}")
    for i, network in enumerate(networks, 1):
        print(f"   {i}. '{network}'")
    
    if target_ssid in networks:
        print(f"✅ СЕТЬ '{target_ssid}' НАЙДЕНА!")
        return True
    else:
        print(f"❌ СЕТЬ '{target_ssid}' НЕ НАЙДЕНА!")
        return False

def test_wifi_adapter():
    """Проверяет состояние Wi-Fi адаптера"""
    print("\n🔧 Проверяем Wi-Fi адаптер...")
    try:
        result = subprocess.run(
            ["netsh", "wlan", "show", "interfaces"],
            capture_output=True, text=True, encoding='cp866'
        )
        print("Состояние Wi-Fi адаптера:")
        for line in result.stdout.splitlines()[:10]:  # Показываем первые 10 строк
            print(f"   {line.strip()}")
    except Exception as e:
        print(f"❌ Ошибка проверки адаптера: {e}")

def continuous_scan(target_ssid="karch_eeg_88005553535", max_attempts=20, delay=5):
    """Постоянно сканирует сети в поисках целевой сети"""
    print(f"\n🔄 Начинаем непрерывный поиск сети '{target_ssid}'")
    print(f"⏰ Интервал сканирования: {delay} секунд")
    print(f"🔢 Максимальное количество попыток: {max_attempts}")
    print("Нажмите Ctrl+C для остановки\n")
    
    found = False
    attempt = 0
    
    while attempt < max_attempts and not found:
        attempt += 1
        print(f"\n--- Попытка {attempt}/{max_attempts} ---")
        
        try:
            found = check_specific_network(target_ssid)
            
            if found:
                print(f"\n🎉 УСПЕХ! Сеть '{target_ssid}' найдена на попытке {attempt}!")
                break
            else:
                if attempt < max_attempts:
                    print(f"⏳ Ждем {delay} секунд до следующей попытки...")
                    time.sleep(delay)
                else:
                    print(f"\n💥 Достигнуто максимальное количество попыток ({max_attempts})")
                    
        except KeyboardInterrupt:
            print(f"\n⏹️ Сканирование прервано пользователем после {attempt} попыток")
            break
        except Exception as e:
            print(f"❌ Ошибка при сканировании: {e}")
            if attempt < max_attempts:
                print(f"⏳ Ждем {delay} секунд до следующей попытки...")
                time.sleep(delay)
    
    return found

def quick_connect_test(target_ssid="karch_eeg_88005553535"):
    """Быстрая попытка подключения к найденной сети"""
    if check_specific_network(target_ssid):
        print(f"\n🔗 Пытаемся подключиться к сети '{target_ssid}'...")
        try:
            # Пробуем подключиться к сети (для Windows)
            if sys.platform.startswith("win"):
                result = subprocess.run(
                    ["netsh", "wlan", "connect", f"name={target_ssid}"],
                    capture_output=True, text=True, encoding='cp866'
                )
                if result.returncode == 0:
                    print("✅ Команда подключения отправлена успешно")
                else:
                    print("❌ Ошибка при отправке команды подключения")
        except Exception as e:
            print(f"❌ Ошибка подключения: {e}")

if __name__ == "__main__":
    print("=== НЕПРЕРЫВНЫЙ СКАНЕР WI-FI СЕТЕЙ ===\n")
    
    # Проверяем Wi-Fi адаптер
    test_wifi_adapter()
    
    print("\n" + "="*50)
    
    # Запускаем непрерывный поиск
    target_network = "karch_eeg_88005553535"
    found = continuous_scan(target_network, max_attempts=20, delay=5)
    
    if found:
        print("\n" + "="*50)
        print("🎯 СЕТЬ НАЙДЕНА! Дальнейшие действия:")
        print("1. Подключитесь к сети 'karch_eeg_88005553535' с паролем '12345678'")
        print("2. Откройте браузер и перейдите по адресу: 192.168.4.1")
        print("3. Или используйте Python-скрипт для подключения к порту 8888")
        
        # Предлагаем быструю попытку подключения
        response = input("\nПопробовать автоматически подключиться? (y/n): ")
        if response.lower() in ['y', 'yes', 'д', 'да']:
            quick_connect_test(target_network)
    else:
        print("\n" + "="*50)
        print("💡 СОВЕТЫ ПО РЕШЕНИЮ ПРОБЛЕМ:")
        print("1. Убедитесь, что ESP32 включена и мигает светодиод")
        print("2. Проверьте, что на ESP32 запущен код с WiFi.softAP()")
        print("3. Перезагрузите ESP32")
        print("4. Поднесите компьютер ближе к ESP32")
        print("5. Проверьте питание ESP32")
        print("6. Попробуйте подключиться к сети с телефона")
        print("7. Убедитесь, что Wi-Fi адаптер компьютера включен")
    
    print("\n" + "="*50)
    print("📝 Статистика:")
    print(f"Целевая сеть: {target_network}")
    print(f"Результат: {'НАЙДЕНА' if found else 'НЕ НАЙДЕНА'}")