import io
import os
import sys
import typing

from . import parser


class RedirectStreams:
    _output: io.TextIOWrapper
    _error: io.TextIOWrapper

    def __init__(
        self,
        output: typing.Optional[io.TextIOWrapper],
        error: typing.Optional[io.TextIOWrapper]
    ):
        self._output = output
        self._error = error

    @property
    def output(self):
        return self._output or sys.stdout

    @property
    def output_fd(self):
        return self._find_fd(self.output)

    @property
    def error(self):
        return self._error or sys.stderr

    @property
    def error_fd(self):
        return self._find_fd(self.error)

    def close(self):
        if self._output:
            self._output.close()

        if self._error:
            self._error.close()

    def _find_fd(self, x):
        if isinstance(x, io.TextIOWrapper):
            x = x.buffer

        if isinstance(x, io.BufferedWriter):
            x = x.raw

        if isinstance(x, io.FileIO):
            return x.fileno()

        raise ValueError(f"cannot find fd for: {x}")

    @staticmethod
    def open(redirects: typing.List[parser.Redirect]):
        output = None
        error = None

        for redirect in redirects:
            stream = open(redirect.path, "a" if redirect.append else "w")

            if redirect.stream_name == parser.StandardNamedStream.OUTPUT:
                if output:
                    output.close()

                output = stream
            elif redirect.stream_name == parser.StandardNamedStream.ERROR:
                if error:
                    error.close()

                error = stream
            else:
                stream.close()

        return RedirectStreams(
            output,
            error,
        )


def which(program: str):
    paths = os.environ.get("PATH", "").split(":")

    for path in paths:
        path = os.path.join(path, program)

        if os.path.exists(path):
            return path

    return None


def builtin_exit(_, __):
    exit(0)


def builtin_echo(arguments: typing.List[str], redirect_streams: RedirectStreams):
    print(" ".join(arguments[1:]), file=redirect_streams.output)


def builtin_type(arguments: typing.List[str], redirect_streams: RedirectStreams):
    program = arguments[1]

    builtin = BUILTINS.get(program)
    if builtin:
        print(f"{program} is a shell builtin", file=redirect_streams.output)
        return

    path = which(program)
    if path:
        print(f"{program} is {path}", file=redirect_streams.output)
        return

    print(f"{program}: not found", file=redirect_streams.output)


def builtin_pwd(_, redirect_streams: RedirectStreams):
    print(os.getcwd(), file=redirect_streams.output)


def builtin_cd(arguments: typing.List[str], redirect_streams: RedirectStreams):
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
                print(f"{path}: $HOME not set", file=redirect_streams.output)
        else:
            print(f"{path}: unsupported path", file=redirect_streams.output)

        if absolute:
            absolute = os.path.normpath(absolute)
            os.chdir(absolute)
    except FileNotFoundError:
        # print(f"cd: {path}: No such file or directory")
        print(f"{path}: No such file or directory", file=redirect_streams.error)
    except PermissionError:
        # print(f"cd: {path}: Permission denied")
        print(f"{path}: Permission denied", file=redirect_streams.error)


BUILTINS = {
    "exit": builtin_exit,
    "echo": builtin_echo,
    "type": builtin_type,
    "pwd": builtin_pwd,
    "cd": builtin_cd,
}
