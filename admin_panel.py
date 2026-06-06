import subprocess
import shutil
import os
import time
import threading
import json
from datetime import datetime
from colorama import init, Fore

rapper_bot = None
aura_bot = None

init(autoreset=True)

def current_time():
    return datetime.now().strftime("%H:%M:%S")

def start_bot():
    global rapper_bot, aura_bot

    if rapper_bot is None or rapper_bot.poll() is not None:
        rapper_log = open("logs.txt", "a", encoding="utf-8")

        rapper_bot = subprocess.Popen(
            ["python", "rapbot.py"],
            stdout=rapper_log,
            stderr=rapper_log
        )

    if aura_bot is None or aura_bot.poll() is not None:
        aura_log = open("aura_logs.txt", "a", encoding="utf-8")

        aura_bot = subprocess.Popen(
            [
                "python",
                r"D:\Sizay programs\AURABOT\aurabot.py"
            ],
            stdout=aura_log,
            stderr=aura_log
        )

    print(Fore.GREEN + f"\n[{current_time()}] Боты запущены!\n")


def stop_bot():
    global rapper_bot, aura_bot

    if rapper_bot and rapper_bot.poll() is None:
        rapper_bot.terminate()
        rapper_bot.wait()

    if aura_bot and aura_bot.poll() is None:
        aura_bot.terminate()
        aura_bot.wait()

    print(Fore.RED + f"\n[{current_time()}] Боты остановлены!\n")


def restart_bot():
    print(Fore.YELLOW + f"\n[{current_time()}] Перезапуск бота...\n")
    stop_bot()
    time.sleep(2)
    start_bot()


def backup_db():
    if not os.path.exists("backup"):
        os.makedirs("backup")

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    source = "bjt.db"
    destination = f"backup/bjt_backup_{timestamp}.db"

    shutil.copy(source, destination)

    print(f"\n[{current_time()}] Backup создан:\n{destination}\n")


def bot_status():

    rapper_status = (
        "Работает"
        if rapper_bot and rapper_bot.poll() is None
        else "Выключен"
    )

    aura_status = (
        "Работает"
        if aura_bot and aura_bot.poll() is None
        else "Выключен"
    )

    print(
        f"\n[{current_time()}]\n"
        f"RapperBot: {rapper_status}\n"
        f"AuraBot: {aura_status}\n"
    )

def show_logs():
    if os.path.exists("logs.txt"):
        with open("logs.txt", "r", encoding="utf-8") as f:
            logs = f.readlines()
        print("\n===== Последние логи ======\n")
        for line in logs[-10:]:
            print(line.strip())
    else:
        print("\nЛогов пока нет!\n")

def clear_logs():
    open("logs.txt", "w").close()
    print(Fore.YELLOW + f"\n[{current_time()}] Логи были очищены!\n")

def auto_restart():
    global rapper_bot, aura_bot

    while True:
        time.sleep(30)

        if rapper_bot and rapper_bot.poll() is not None:
            print(Fore.RED + f"\n[{current_time()}] RapperBot упал! Перезапуск...\n")

            rapper_log = open("logs.txt", "a", encoding="utf-8")

            rapper_bot = subprocess.Popen(
                ["python", "rapbot.py"],
                stdout=rapper_log,
                stderr=rapper_log
            )

        if aura_bot and aura_bot.poll() is not None:
            print(Fore.RED + f"\n[{current_time()}] AuraBot упал! Перезапуск...\n")

            aura_log = open("aura_logs.txt", "a", encoding="utf-8")

            aura_bot = subprocess.Popen(
                [
                    "python",
                    r"D:\Sizay programs\AURABOT\aurabot.py"
                ],
                stdout=aura_log,
                stderr=aura_log
            )

def scheduled_restart():
    while True:
        time.sleep(10800)

        if (
            (rapper_bot and rapper_bot.poll() is None)
            or
            (aura_bot and aura_bot.poll() is None)
        ):
            print(
                Fore.YELLOW
                + f"\n[{current_time()}] Плановый перезапуск ботов...\n"
            )

            restart_bot()

def user_count():
    import sqlite3

    conn = sqlite3.connect("bjt.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")

    count = cursor.fetchone()[0]

    conn.close()

    print(Fore.CYAN + f"\n[{current_time()}] Пользователей: {count}\n")

def promo_status():
    if not os.path.exists("promo.json"):
        print(Fore.RED + "\npromo.json не найден!\n")
        return

    with open("promo.json", "r", encoding='utf-8') as f:
        promos = json.load(f)

    active_promos = [promo for promo in promos if promo.get("uses", 0) > 0]

    if not active_promos:
        print(Fore.RED + "\nНет активных промокодов!\n")

    print(Fore.CYAN + "\nАктивные промокоды:\n")

    for promo in active_promos:
        code = promo.get("code")
        uses = promo.get("uses", 0)

        print(f"{code} - {uses} активаций\n")

threading.Thread(target=auto_restart, daemon=True).start()
threading.Thread(target=scheduled_restart, daemon=True).start()
while True:
    print("======== RapperBot Admin ========")
    print("1.  Запустить бота")
    print("2.  Остановить бота")
    print("3.  Перезапустить бота")
    print("4.  Backup БД")
    print("5.  Статус")
    print("6.  Логи")
    print("7.  Очистить логи")
    print("8.  Колл-во пользователей")
    print("9.  Активные промокоды")
    print("10.  Выход")

    choice = input("\nВыбор: ")

    if choice == "1":
        start_bot()

    elif choice == "2":
        stop_bot()

    elif choice == "3":
        restart_bot()

    elif choice == "4":
        backup_db()

    elif choice == "5":
        bot_status()

    elif choice == "6":
        show_logs()

    elif choice == "7":
        clear_logs()

    elif choice == "8":
        user_count()

    elif choice == "9":
        promo_status()

    elif choice == "10":
        stop_bot()
        print("\n Выход...")
        break

    else:
        print(Fore.RED + "\n Неверный выбор!\n")