import os
import sys
import termios
import tty
import typing

from . import command, parser


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

# print(_find_shared_prefix([
#     "xyz_foo",
#     "xyz_foo_bar",
#     "xyz_foo_bar_baz",
#     "a"
# ]))
# exit()


def autocomplete(line: str, bell_rang: bool):
    if not line:
        return ""

    candidates = set()

    for name in command.BUILTINS.keys():
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

    import termios
    print(termios.ECHO)

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

                    return None, None

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
                    sys.stdin.read(1)  # 'A' or 'B' or 'C' or 'D'

                case "\x7f":
                    if not line:
                        continue

                    line = line[:-1]
                    _write_and_flush("\b \b")

                    bell_rang = False

                case _:
                    line += character
                    _write_and_flush(character.upper())
    except KeyboardInterrupt:
        _write_and_flush("\n")
        return [], []
    finally:
        termios.tcsetattr(stdin_fd, termios.TCSANOW, previous)

    if not len(line):
        return [], []

    return parser.LineParser(line).parse()


def eval(
    arguments: typing.List[str],
    redirects: typing.List[parser.Redirect]
):
    redirected_streams = command.RedirectStreams.open(redirects)

    program = arguments[0]

    builtin = command.BUILTINS.get(program)
    if builtin:
        builtin(arguments, redirected_streams)
        redirected_streams.close()
        return

    path = command.which(program)
    if path:
        pid = os.fork()

        if not pid:
            os.dup2(redirected_streams.output_fd, 1)
            os.dup2(redirected_streams.error_fd, 2)
            redirected_streams.close()

            os.execv(path, arguments)
            exit(1)

        os.waitpid(pid, 0)
    else:
        print(f"{program}: command not found")

    redirected_streams.close()


def main():
    while True:
        arguments, redirects = read()

        if arguments is None:
            break

        if not len(arguments):
            continue

        eval(arguments, redirects)


if __name__ == "__main__":
    main()
