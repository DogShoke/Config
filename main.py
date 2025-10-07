import os
import sys
import getpass
import socket
import shlex
import zipfile
import base64

# Глобальные переменные для конфигурации
VFS_PATH = None
CUSTOM_PROMPT = None
SCRIPT_PATH = None

# Глобальные переменные VFS
VFS = {}
VFS_CWD = []  # текущая папка внутри VFS


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


def load_vfs(zip_path):
    """Загрузить ZIP VFS в память"""
    global VFS
    if not os.path.exists(zip_path):
        print(f"Ошибка: VFS файл '{zip_path}' не найден.")
        return False
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            VFS = {}
            for name in zf.namelist():
                if name.endswith("/"):
                    continue  # пропускаем пустые папки
                parts = name.strip("/").split("/")
                current = VFS
                for p in parts[:-1]:
                    current = current.setdefault(p, {})
                data = zf.read(name)
                try:
                    current[parts[-1]] = data.decode('utf-8')
                except UnicodeDecodeError:
                    current[parts[-1]] = base64.b64encode(data).decode('utf-8')
        return True
    except zipfile.BadZipFile:
        print(f"Ошибка: VFS файл '{zip_path}' не является корректным ZIP архивом.")
        return False


def get_vfs_node(path_list):
    """Вернуть объект (папка или файл) по пути внутри VFS"""
    current = VFS
    for p in path_list:
        if isinstance(current, dict) and p in current:
            current = current[p]
        else:
            return None
    return current


def cmd_ls(args):
    """Вывод содержимого текущей папки VFS"""
    node = get_vfs_node(VFS_CWD)
    if node is None:
        print("Ошибка: путь не найден в VFS")
        return
    if not isinstance(node, dict):
        print("Ошибка: текущий путь не является директорией.")
        return
    for name, value in node.items():
        if isinstance(value, dict):
            print(f"{name}/")
        else:
            print(name)


def cmd_cd(args):
    """Переход по папкам VFS"""
    global VFS_CWD
    if len(args) != 1:
        print("Ошибка: cd принимает ровно один аргумент.")
        return
    target = args[0]
    if target == "..":
        if VFS_CWD:
            VFS_CWD.pop()
    else:
        node = get_vfs_node(VFS_CWD + [target])
        if node is None or not isinstance(node, dict):
            print(f"Ошибка: папка '{target}' не найдена.")
        else:
            VFS_CWD.append(target)


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

    # Загрузка VFS
    if not load_vfs(VFS_PATH):
        sys.exit(1)

    # Если указан стартовый скрипт — выполнить его
    if SCRIPT_PATH:
        run_script(SCRIPT_PATH)

    # Запуск REPL
    repl()