import os
import sys
import zipfile

# Эмулятор командной строки UNIX
# Этап 4: команды ls, cd, whoami, tac
# с виртуальной файловой системой и отображением реального пути

class Emulator:
    def __init__(self, vfs_path=None):
        # Инициализация параметров
        self.vfs = {}  # словарь: путь → содержимое файла
        self.cwd = "/"  # текущая директория в VFS
        self.username = os.getenv("USER", "user")  # имя пользователя
        self.home = os.path.expanduser("~")  # домашняя директория
        if vfs_path:
            self.load_vfs(vfs_path)

    # Загрузка виртуальной файловой системы из ZIP
    def load_vfs(self, vfs_path):
        if not os.path.exists(vfs_path):
            print(f"Ошибка: файл VFS '{vfs_path}' не найден.")
            sys.exit(1)
        with zipfile.ZipFile(vfs_path, 'r') as z:
            for name in z.namelist():
                self.vfs[name] = z.read(name).decode("utf-8", errors="ignore")

    # Формирование строки приглашения (реальный путь)
    def get_prompt(self):
        # "/" в VFS отображается как домашняя директория
        if self.cwd == "/":
            path = self.home
        else:
            path = os.path.join(self.home, self.cwd.strip("/"))
        return f"{path} $ "

    # Команда ls — показать содержимое текущей папки
    def cmd_ls(self, args):
        found = set()
        prefix = self.cwd.strip("/") + "/"
        if prefix == "/":
            prefix = ""

        for name in self.vfs.keys():
            if name.startswith(prefix):
                rest = name[len(prefix):]
                if "/" in rest:
                    found.add(rest.split("/")[0] + "/")
                else:
                    found.add(rest)

        if found:
            for item in sorted(found):
                print(item)
        else:
            print("Пусто")

    # Команда cd — переход по папкам VFS
    def cmd_cd(self, args):
        if not args:
            print("Ошибка: не указана папка.")
            return
        target = args[0]
        if target == "..":
            if self.cwd != "/":
                self.cwd = "/" + "/".join(self.cwd.strip("/").split("/")[:-1])
                if self.cwd == "//" or self.cwd == "":
                    self.cwd = "/"
        else:
            new_path = (self.cwd.strip("/") + "/" + target).strip("/")
            if not new_path.endswith("/"):
                new_path += "/"
            exists = any(name.startswith(new_path) for name in self.vfs.keys())
            if exists:
                self.cwd = "/" + new_path.strip("/")
            else:
                print(f"Ошибка: папка '{target}' не найдена.")

    # Команда whoami — вывести имя пользователя
    def cmd_whoami(self, args):
        print(self.username)

    # Команда tac — вывести файл в обратном порядке
    def cmd_tac(self, args):
        if not args:
            print("Ошибка: не указан файл.")
            return
        path = args[0]
        if path.startswith("/"):
            path = path[1:]
        else:
            path = (self.cwd.strip("/") + "/" + path).strip("/")
        if path not in self.vfs:
            print(f"Ошибка: файл '{args[0]}' не найден.")
            return
        lines = self.vfs[path].splitlines()
        for line in reversed(lines):
            print(line)

    # Выполнение отдельной команды
    def execute(self, line):
        parts = line.strip().split()
        if not parts:
            return
        cmd = parts[0]
        args = parts[1:]
        if cmd == "ls":
            self.cmd_ls(args)
        elif cmd == "cd":
            self.cmd_cd(args)
        elif cmd == "whoami":
            self.cmd_whoami(args)
        elif cmd == "tac":
            self.cmd_tac(args)
        elif cmd == "exit":
            print("Выход.")
            sys.exit(0)
        else:
            print(f"Ошибка: неизвестная команда '{cmd}'")

    # Выполнение команд из скрипта
    def run_script(self, path):
        if not os.path.exists(path):
            print(f"Ошибка: скрипт '{path}' не найден.")
            return
        print(f"\n=== Выполнение скрипта {path} ===")
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                print(f"{self.get_prompt()}{line}")
                self.execute(line)
        print(f"=== Завершено выполнение скрипта {path} ===\n")

    # Интерактивный режим
    def repl(self):
        while True:
            try:
                line = input(self.get_prompt())
                self.execute(line)
            except KeyboardInterrupt:
                print()
            except EOFError:
                print()
                break


# Точка входа
if __name__ == "__main__":
    if len(sys.argv) > 1:
        vfs_path = sys.argv[1]
        script_path = sys.argv[2] if len(sys.argv) > 2 else None
    else:
        vfs_path = "vfs.zip"
        script_path = "script.txt"

    emulator = Emulator(vfs_path)

    print("=== Конфигурация эмулятора ===")
    print(f"VFS_PATH: {vfs_path}")
    print(f"SCRIPT_PATH: {script_path}")
    print("==============================")

    if script_path:
        emulator.run_script(script_path)

    emulator.repl()