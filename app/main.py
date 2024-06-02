import typing
import sys


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


def eval(arguments: typing.List[str]):
    program = arguments[0]

    if program == "exit":
        exit(0)
    else:
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
