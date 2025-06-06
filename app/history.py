import os

FILE_ENVVAR = "HISTFILE"

previous_lines = []
last_append_index = 0


def add_line(line):
    previous_lines.append(line)


def iterate(start=0):
    lines = previous_lines[-start:]

    for index, line in enumerate(lines, start):
        yield (index + 1, line)


def read(path: str):
    with open(path, "r") as fd:
        for line in fd:
            line = line.strip("\n")

            if line:
                add_line(line)


def write(path: str, append=False):
    global last_append_index

    mode = "a" if append else "w"

    with open(path, mode) as fd:
        for line in previous_lines[last_append_index:]:
            fd.write(line + "\n")

    last_append_index = len(previous_lines)


def initialize():
    path = os.environ.get(FILE_ENVVAR)
    if not path:
        return

    if not os.path.isfile(path):
        return

    read(path)


def destroy():
    path = os.environ.get(FILE_ENVVAR)
    if not path:
        return

    write(path)
