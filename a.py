def getpass(prompt="Password: "):
    old = termios.tcgetattr(fd)
    new = termios.tcgetattr(fd)
    new[3] = new[3] & ~termios.ECHO          # lflags
    try:
        termios.tcsetattr(fd, termios.TCSADRAIN, new)
        passwd = input(prompt)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
    return passwd

import termios, sys, tty

stdin_fd = sys.stdin.fileno()
previous = termios.tcgetattr(stdin_fd)
print(previous)

tty.setcbreak(stdin_fd, termios.TCSANOW)

try:
    while True:
        character = sys.stdin.read(1)
        print(character, ord(character))
        # if s in ("\t", "\n"):
        #     if s == "\t":
        #         res = autocomplete(buf, trie)
        #         buf += res[0]
        #         sys.stdout.write(res[0])
        #         sys.stdout.flush()
        #         sys.stdout.write(" ")
        #         sys.stdout.flush()
        #         continue
        #     break
        # elif ord(s) == 27:
        #     s = sys.stdin.read(1)
        #     if s == "[":
        #         s = sys.stdin.read(1)
        # elif ord(s) != 127:
        #     sys.stdout.write(s)
        #     sys.stdout.flush()
        #     buf += s
        # else:
        #     is_size_one = len(buf) == 1
        #     buf = buf[:-1]
        #     if buf or is_size_one:
        #         sys.stdout.write("\b \b")
        #         sys.stdout.flush()
finally:
    termios.tcsetattr(stdin_fd, termios.TCSANOW, previous)
