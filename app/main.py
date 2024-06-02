import typing
import sys
import os


def read():
    sys.stdout.write("$ ")
    sys.stdout.flush()

    try:
        line = input()

        if not len(line):
            return []

        return line.split(" ")
    except EOFError:
        return None
    except KeyboardInterrupt:
        sys.stdout.write("\n")
        sys.stdout.flush()
        return []


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
    
    builtin = builtins.get(program)
    if builtin:
        print(f"{program} is a shell builtin")
        return

    path = which(program)
    if path:
        print(f"{program} is {path}")
        return

    print(f"{program} not found")


def builtin_pwd(_):
    print(os.getcwd())


def builtin_cd(arguments: typing.List[str]):
    path = arguments[1]

    if path.startswith("/"):
        os.chdir(path)
    else:
        print(f"{path}: unsupported path")


builtins = {
    "exit": builtin_exit,
    "echo": builtin_echo,
    "type": builtin_type,
    "pwd": builtin_pwd,
    "cd": builtin_cd,
}


def eval(arguments: typing.List[str]):
    program = arguments[0]

    builtin = builtins.get(program)
    if builtin:
        builtin(arguments)
        return

    path = which(program)
    if path:
        pid = os.fork()

        if not pid:
            os.execv(path, arguments)
            exit(1)

        os.waitpid(pid, 0)
        return

    print(f"{program}: command not found")


def main():
    while True:
        arguments = read()

        if arguments is None:
            break

        if not len(arguments):
            continue

        eval(arguments)


if __name__ == "__main__":
    main()
