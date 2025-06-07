previous_lines = []


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


def write(path: str):
    with open(path, "w") as fd:
        for line in previous_lines:
            fd.write(line + "\n")
