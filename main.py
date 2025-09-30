import os
import sys
import getpass
import socket
import shlex

# Глобальные переменные для конфигурации
VFS_PATH = None
CUSTOM_PROMPT = None
SCRIPT_PATH = None


def make_prompt() -> str:
    """Формируем приглашение для ввода."""
    if CUSTOM_PROMPT:
        return CUSTOM_PROMPT + " "
    user = getpass.getuser()
    host = socket.gethostname().split('.')[0]
    cwd = os.getcwd()
    home = os.path.expanduser("~")
    if cwd == home:
        short = "~"
    elif cwd.startswith(home + os.sep):
        short = "~" + cwd[len(home):]
    else:
        short = cwd
    return f"{user}@{host}:{short}$ "


def cmd_ls(args):
    print("ls ", *args)


def cmd_cd(args):
    if len(args) > 1:
        print("Ошибка: cd принимает не более одного аргумента.")
        return
    print("cd ", *args)


def execute_command(cmd: str, args: list):
    if cmd == "":
        return
    if cmd == "exit":
        print("Выход.")
        sys.exit(0)
    elif cmd == "ls":
        cmd_ls(args)
    elif cmd == "cd":
        cmd_cd(args)
    else:
        print(f"Ошибка: неизвестная команда '{cmd}'")


def run_script(path: str):
    """Выполнение стартового скрипта"""
    if not os.path.exists(path):
        print(f"Ошибка: стартовый скрипт '{path}' не найден.")
        return

    print(f"\n=== Выполнение скрипта {path} ===")
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, start=1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue  # комментарий или пустая строка

                print(f"{make_prompt()}{line}")  # имитируем ввод

                try:
                    parts = shlex.split(line)
                except ValueError as e:
                    print(f"Ошибка парсинга (строка {line_num}): {e}")
                    continue

                cmd = parts[0]
                args = parts[1:]
                try:
                    execute_command(cmd, args)
                except Exception as e:
                    print(f"Ошибка выполнения команды (строка {line_num}): {e}")
    except Exception as e:
        print(f"Ошибка при работе со скриптом: {e}")
    print(f"=== Завершено выполнение скрипта {path} ===\n")


def repl():
    """Основной цикл REPL"""
    while True:
        try:
            line = input(make_prompt())
        except EOFError:
            print()
            break
        except KeyboardInterrupt:
            print()
            continue
        line = line.strip()
        if not line:
            continue

        try:
            parts = shlex.split(line)
        except ValueError as e:
            print("Ошибка парсинга:", e)
            continue

        cmd = parts[0]
        args = parts[1:]
        execute_command(cmd, args)


if __name__ == "__main__":
    # Читаем аргументы командной строки
    if len(sys.argv) < 2:
        print("Использование: python emulator.py <VFS_PATH> [PROMPT] [SCRIPT_PATH]")
        sys.exit(1)

    VFS_PATH = sys.argv[1]
    if len(sys.argv) > 2:
        CUSTOM_PROMPT = sys.argv[2]
    if len(sys.argv) > 3:
        SCRIPT_PATH = sys.argv[3]

    # Отладочный вывод
    print("=== Конфигурация эмулятора ===")
    print(f"VFS_PATH     : {VFS_PATH}")
    print(f"CUSTOM_PROMPT: {CUSTOM_PROMPT}")
    print(f"SCRIPT_PATH  : {SCRIPT_PATH}")
    print("==============================")

    # Если указан стартовый скрипт — выполнить его
    if SCRIPT_PATH:
        run_script(SCRIPT_PATH)

    # Запуск REPL
    repl()