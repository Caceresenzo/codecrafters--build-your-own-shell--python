import os

from .parser import Command
from .command import RedirectStreams, BUILTINS, which


def _exec(command: Command):
    redirected_streams = RedirectStreams.open(command.redirects)

    builtin = BUILTINS.get(command.program)
    if builtin:
        builtin(command.arguments, redirected_streams)
        redirected_streams.close()
        return

    path = which(command.program)
    if not path:
        print(f"{command.program}: command not found")
        redirected_streams.close()
        return

    os.dup2(redirected_streams.output_fd, 1)
    os.dup2(redirected_streams.error_fd, 2)
    redirected_streams.close()

    os.execv(path, command.arguments)
    os._exit(1)


def _spawn(fd_in: int, fd_out: int, command: list[Command]) -> int:
    pid = os.fork()

    if pid == 0:
        os.dup2(fd_in, 0)
        os.dup2(fd_out, 1)

        _exec(command)

    return pid


def pipeline(commands: list[Command]):
    pid = os.fork()

    if pid == 0:
        fd_in = 0

        for command in commands[:-1]:
            pipe_fds = os.pipe()

            _spawn(fd_in, pipe_fds[1], command)

            os.close(pipe_fds[1])

            fd_in = pipe_fds[0]

        os.dup2(fd_in, 0)

        _exec(commands[-1])

    os.waitpid(pid, 0)
    return pid


def single(command: Command):
    redirected_streams = RedirectStreams.open(command.redirects)

    builtin = BUILTINS.get(command.program)
    if builtin:
        builtin(command.arguments, redirected_streams)
        redirected_streams.close()
        return

    path = which(command.program)
    if not path:
        print(f"{command.program}: command not found")
        redirected_streams.close()
        return

    pid = os.fork()

    if pid == 0:
        os.dup2(redirected_streams.output_fd, 1)
        os.dup2(redirected_streams.error_fd, 2)
        redirected_streams.close()

        os.execv(path, command.arguments)
        os._exit(1)

    os.waitpid(pid, 0)
    redirected_streams.close()
