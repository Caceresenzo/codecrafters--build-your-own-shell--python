import os
import sys
import typing

from . import command, parser


def read():
    sys.stdout.write("$ ")
    sys.stdout.flush()

    try:
        line = input()

        if not len(line):
            return [], []

        return parser.LineParser(line).parse()
    except EOFError:
        return None, None
    except KeyboardInterrupt:
        sys.stdout.write("\n")
        sys.stdout.flush()
        return [], []


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
