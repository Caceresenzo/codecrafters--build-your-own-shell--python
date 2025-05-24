import os
import sys
import termios
import tty
import typing

from . import history, parser, run
from .command import BUILTINS


UP = "A"
DOWN = "B"


def _write_and_flush(data: str):
    sys.stdout.write(data)
    sys.stdout.flush()


def _find_shared_prefix(candidates: typing.List[str]):
    candidates = sorted(candidates, key=lambda x: (len(x), x))

    first, *others = candidates

    end = 0
    for end in range(1, len(first) + 1):
        for other in others:
            other = other[:end]

            if not first.startswith(other):
                break
        else:
            continue

        end -= 1
        break

    return first[:end] or None


def autocomplete(line: str, bell_rang: bool):
    if not line:
        return ""

    candidates = set()

    for name in BUILTINS.keys():
        if name.startswith(line):
            candidates.add(name[len(line):])

    paths = os.environ.get("PATH", "").split(":")
    for path in paths:
        if not os.path.isdir(path):
            continue

        for file_name in os.listdir(path):
            if not file_name.startswith(line):
                continue

            file_path = os.path.join(path, file_name)
            if not os.path.isfile(file_path) or not os.access(file_path, os.X_OK):
                continue

            candidates.add(file_name[len(line):])

    candidates = sorted(candidates)
    if not candidates:
        return None  # trigger the bell by mistake, but that fine

    if len(candidates) == 1:
        candidate = candidates[0]
        return f"{candidate} "

    shared_prefix = _find_shared_prefix(candidates)
    if shared_prefix is not None:
        return shared_prefix

    if bell_rang:
        sys.stdout.write("\n")

        for index, candidate in enumerate(sorted(candidates)):
            if index != 0:
                sys.stdout.write("  ")

            sys.stdout.write(line)
            sys.stdout.write(candidate)

        sys.stdout.write("\n")

        prompt()

        _write_and_flush(line)

    return None


def prompt():
    _write_and_flush("$ ")


def read():
    line = ""

    history_length = len(history.previous_lines)
    history_position = history_length

    def change_line(new_line: str):
        nonlocal line
        _write_and_flush("\r" + " " * (len(line) + 2) + "\r")

        prompt()

        line = new_line
        _write_and_flush(line)

    def up_history():
        nonlocal history_position
        if history_position != 0:
            history_position -= 1
            change_line(history.previous_lines[history_position])

    def down_history():
        nonlocal history_position
        if history_position < history_length:
            history_position += 1

            if history_position == history_length:
                change_line("")
            else:
                change_line(history.previous_lines[history_position])

    prompt()

    stdin_fd = sys.stdin.fileno()
    previous = termios.tcgetattr(stdin_fd)
    tty.setcbreak(stdin_fd, termios.TCSANOW)

    try:
        bell_rang = False

        while True:
            character = sys.stdin.read(1)

            match character:
                case "\x04":
                    if line:
                        continue

                    return None

                case "\n":
                    _write_and_flush("\n")
                    break

                case "\t":
                    autocompleted = autocomplete(line, bell_rang)

                    if autocompleted:
                        line += autocompleted
                        _write_and_flush(autocompleted)
                    else:
                        _write_and_flush("\a")
                        bell_rang = True

                case "\x1b":
                    sys.stdin.read(1)  # '['
                    direction = sys.stdin.read(1)  # 'A' or 'B' or 'C' or 'D'

                    if direction == UP and history_position != 0:
                        up_history()
                    elif direction == DOWN:
                        down_history()

                case "\x7f":
                    if not line:
                        continue

                    line = line[:-1]
                    _write_and_flush("\b \b")

                    bell_rang = False

                case _:
                    line += character
                    _write_and_flush(character)
    except KeyboardInterrupt:
        _write_and_flush("\n")
        return []
    finally:
        termios.tcsetattr(stdin_fd, termios.TCSANOW, previous)

    if not len(line):
        return []

    history.add_line(line)
    return parser.LineParser(line).parse()


def eval(
    commands: typing.List[parser.Command]
):
    if len(commands) == 1:
        run.single(commands[0])
    else:
        run.pipeline(commands)


def main():
    while True:
        commands = read()

        if commands is None:
            break

        if not len(commands):
            continue

        eval(commands)


if __name__ == "__main__":
    main()
