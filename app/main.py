import sys


def main():
    sys.stdout.write("$ ")
    sys.stdout.flush()

    line = input()
    arguments = line.split(" ")

    program = arguments[0]
    print(f"{program}: command not found")


if __name__ == "__main__":
    main()
