import os
import sys
import getpass
import socket
import shlex

def make_prompt() -> str:
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

def repl():
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
    repl()