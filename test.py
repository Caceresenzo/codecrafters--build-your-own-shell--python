import os


def spawn(fd_in: int, fd_out: int, command: list[str]) -> int:
    pid = os.fork()

    if pid == 0:
        os.dup2(fd_in, 0)
        os.dup2(fd_out, 1)

        os.execvp(command[0], command)
        os._exit(1)

    return pid


def pipeline(commands: list[list[str]]):
    fd_in = 0

    for command in commands[:-1]:
        pipe_fds = os.pipe()

        spawn(fd_in, pipe_fds[1], command)

        os.close(pipe_fds[1])

        fd_in = pipe_fds[0]

    os.dup2(fd_in, 0)

    os.execvp(commands[-1][0], commands[-1])
    os._exit(1)


pipeline([
    ["ls", "-l"],
    ["sort"],
    ["uniq"],
    ["cat", "-e"],
])
