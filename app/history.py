previous_lines = []


def add_line(line):
    previous_lines.append(line)


def iterate(start=0):
    lines = previous_lines[-start:]

    for index, line in enumerate(lines, start):
        yield (index + 1, line)
