with open('/dev/input/event1', 'rb') as touch:
    for line in touch:
        print(line)
