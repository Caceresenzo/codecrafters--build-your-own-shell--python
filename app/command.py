import io
import os
import sys
import typing

from . import completer, history, job, parser, variable


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

        if os.access(path, os.X_OK):
            return path

    return None


def builtin_exit(arguments: typing.List[str], __):
    code = int(arguments[1]) if len(arguments) > 1 else 0

    return code


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


def builtin_history(arguments: typing.List[str], redirect_streams: RedirectStreams):
    start = None

    argv1 = arguments[1] if len(arguments) > 1 else None
    if argv1 and argv1.isdigit():
        start = int(argv1)
    elif argv1 == "-r":
        history.read(arguments[2])
        return
    elif argv1 == "-w":
        history.write(arguments[2])
        return
    elif argv1 == "-a":
        history.write(arguments[2], append=True)
        return

    for number, line in history.iterate(start):
        print(f"{number:-5}  {line}", file=redirect_streams.output)


def builtin_complete(arguments: typing.List[str], redirect_streams: RedirectStreams):
    flag = arguments[1]

    if flag == "-C":
        completer_path = arguments[2]
        program_name = arguments[3]

        completer.register(program_name, completer_path)

    elif flag == "-p":
        program_name = arguments[2]

        handler_path = completer.get_handler(program_name)
        if handler_path:
            print(f"{arguments[0]} -C '{handler_path}' {program_name}", file=redirect_streams.output)
        else:
            print(f"{arguments[0]}: {program_name}: no completion specification", file=redirect_streams.error)

    elif flag == "-r":
        program_name = arguments[2]

        if not completer.unregister(program_name):
            print(f"{arguments[0]}: {program_name}: no completion specification", file=redirect_streams.error)

    else:
        print(f"{arguments[0]}: unknown flag: {flag}", file=redirect_streams.error)


def builtin_jobs(arguments: typing.List[str], redirect_streams: RedirectStreams):
    job.reap(print_running=True)


def builtin_declare(arguments: typing.List[str], redirect_streams: RedirectStreams):
    flag = arguments[1]

    if flag == "-p":
        name = arguments[2]

        value = variable.get(name)
        if value is not None:
            print(f"{arguments[0]} -- {name}=\"{value}\"", file=redirect_streams.output)
        else:
            print(f"{arguments[0]}: {name}: not found", file=redirect_streams.error)
    elif "-" not in flag:
        name, value = flag.split("=", 1)

        if not (name[0].isalpha() or name[0] == "_") and not all(character.isalnum() or character == "_" for character in name):
            print(f"{arguments[0]}: `{name}={value}': not a valid identifier", file=redirect_streams.error)
            return

        variable.set(name, value)


BUILTINS = {
    "exit": builtin_exit,
    "echo": builtin_echo,
    "type": builtin_type,
    "pwd": builtin_pwd,
    "cd": builtin_cd,
    "history": builtin_history,
    "complete": builtin_complete,
    "jobs": builtin_jobs,
    "declare": builtin_declare,
}
