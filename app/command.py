import os
import typing


def which(program: str):
    paths = os.environ.get("PATH", "").split(":")

    for path in paths:
        path = os.path.join(path, program)

        if os.path.exists(path):
            return path

    return None


def builtin_exit(_):
    exit(0)


def builtin_echo(arguments: typing.List[str]):
    print(" ".join(arguments[1:]))


def builtin_type(arguments: typing.List[str]):
    program = arguments[1]

    builtin = BUILTINS.get(program)
    if builtin:
        print(f"{program} is a shell builtin")
        return

    path = which(program)
    if path:
        print(f"{program} is {path}")
        return

    print(f"{program}: not found")


def builtin_pwd(_):
    print(os.getcwd())


def builtin_cd(arguments: typing.List[str]):
    path = arguments[1]

    try:
        absolute = None

        if path.startswith("/"):
            absolute = path
        elif path.startswith("."):
            absolute = os.path.join(os.getcwd(), path)
        elif path.startswith("~"):
            home = os.environ.get("HOME")
            if home:
                absolute = os.path.join(home, path[1:])
            else:
                print(f"{path}: $HOME not set")
        else:
            print(f"{path}: unsupported path")

        if absolute:
            absolute = os.path.normpath(absolute)
            os.chdir(absolute)
    except FileNotFoundError:
        # print(f"cd: {path}: No such file or directory")
        print(f"{path}: No such file or directory")
    except PermissionError:
        # print(f"cd: {path}: Permission denied")
        print(f"{path}: Permission denied")


BUILTINS = {
    "exit": builtin_exit,
    "echo": builtin_echo,
    "type": builtin_type,
    "pwd": builtin_pwd,
    "cd": builtin_cd,
}
