x = '2f6170692f776174657273797374656d73'

length = len(x) // 2

j = 0
for i in range(length):
    char = int(x[j:j+2], 16)
    print(i, char, chr(char))
    j = i * 2
