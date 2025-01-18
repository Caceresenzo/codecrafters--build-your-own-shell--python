import os
import sys
import termios
import tty
import typing

from . import command, parser


def _write_and_flush(data: str):
    sys.stdout.write(data)
    sys.stdout.flush()


def autocomplete(line: str):
    candidates = []

    for name in command.BUILTINS.keys():
        if name.startswith(line) and name != line:
            candidates.append(name[len(line):])

    if not candidates:
        return None

    if len(candidates) == 1:
        candidate = candidates[0]

        return f"{candidate} "

    raise NotImplementedError("TODO")


def read():
    line = ""

    stdin_fd = sys.stdin.fileno()
    previous = termios.tcgetattr(stdin_fd)

    tty.setcbreak(stdin_fd, termios.TCSANOW)

    sys.stdout.write("$ ")
    sys.stdout.flush()

    try:
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
                    autocompleted = autocomplete(line)

                    if autocompleted:
                        _write_and_flush(autocompleted)
                        line += autocompleted
                    else:
                        _write_and_flush("\a")

                case "\x7f":
                    if not line:
                        continue

                    line = line[:-1]
                    _write_and_flush("\b \b")

                case _:
                    line += character
                    _write_and_flush(character)
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
