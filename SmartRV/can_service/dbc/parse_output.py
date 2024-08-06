import sys


grep = sys.argv[1]

line = []
while True:
    char = sys.stdin.read(1)
    if char == '\n':
        pr_line = ''.join(line)
        if grep in pr_line:
            print(pr_line, flush=True)
        line = []
    else:
        line.append(char)
