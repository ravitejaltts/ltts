class bitShifter():
    """Initializes with byte data and keeps a binary string representation"""
    def __init__(self, bytedata):
        self.lsb0 = True
        self.bitspopped = 0
        self.bitsremoved = 0
        self.bitstring = self.create_bits(bytedata)

    def __repr__(self):
        return self.bitstring

    def __getitem__(self, index):
        return self.bitstring[index]

    def __unicode__(self):
        return self.bitstring

    def __str__(self):
        return self.bitstring

    def __int__(self):
        if not self.bitstring:
            return 0
        else:
            return int("0b" + self.bitstring, 2)

    def __len__(self):
        return len(self.bitstring)

    def hexArray(self):
        bits = len(self.bitstring)
        hexbytes = []

        if not bits%8 == 0:
            raise IndexError("Bits length need to be dividable by 8 to get complete bytes")

        for i in range(bits/8):
            hexbytes.append(int("0b" + self.bitstring[8*i:8*i+8], 2))

        return hexbytes

    def create_bits(self, data):
        """Creates a bitstring based on different input and stores it as a class value for later processing"""
        if not data:
            return ""

        # Create header bit to pad 0 as needed
        bits = 1
        for byte in data:
            bits = bits << 8
            if self.lsb0 is True:
                bits += int('{:08b}'.format(byte)[::-1], 2)
            else:
                # Add regular
                bits += byte
        
        bits = "%s" % bin(bits)

        #Exclude 0b1 from string
        return bits[3:]

    def pop(self, bitstopop):
        """Pops the amount bitstopop bits and returns either an integer/long, or a raw string without 0b prefix, bitstopop is taken off the beginning of the held bitstring"""
        if len(self.bitstring) < bitstopop:
            raise IndexError("Bits to pop exceed available bit count\n%i bits to pop exceed %i available bits\nRemaining bitstring: %s" % (bitstopop, self.__len__(), self.bitstring))

        if bitstopop == 0:
            return None

        if self.lsb0:
            bits_out = int("0b" + self.bitstring[:bitstopop], 2)
            bits_out = int('{:{width}b}'.format(bits_out, width=bitstopop)[::-1], 2)
        else:
            pass

        self.bitstring = self.bitstring[bitstopop:]
        self.bitspopped += bitstopop
        return bits_out

    def remove(self, bitstoremove, raw=False):
        if len(self.bitstring) < bitstoremove:
            raise IndexError("Bits to remove exceed available bit count\n%i bits to remove exceed %i available bits\nRemaining bitstring: %s" % (bitstoremove, self.__len__(), self.bitstring))

        if raw:
            bits_out = self.bitstring[-bitstoremove:]
        else:
            bits_out = int("0b" + self.bitstring[-bitstoremove:], 2)

        self.bitstring = self.bitstring[:-bitstoremove]
        self.bitsremoved += bitstoremove
        return bits_out

    def get(self, bitstoget, raw=False):
        """Gets the amount bitstoget bits and returns either an integer/long, or a raw string without 0b prefix, does not substract from the held bitstring"""
        if len(self.bitstring) < bitstoget:
            raise IndexError("Bits to get exceed available bit count\n%i bits to get exceed %i available bits\nRemaining bitstring: %s" % (bitstoget, self.__len__(), self.bitstring))

        if raw:
            bits_out = self.bitstring[:bitstoget]
        else:
            bits_out = int("0b" + self.bitstring[:bitstoget], 2)

        return bits_out

    def push(self, bitstopush):
        if type(bitstopush) != type("String"):
            raise TypeError("Unsupported type: %s, a string containing 0 and 1 is needed" % type(bitstopush))

        if bitstopush:
            self.bitstring = bitstopush + self.bitstring

    def append(self, bitstoappend):
        if type(bitstoappend) != type("String"):
            raise TypeError("Unsupported type: %s, a string containing 0 and 1 is needed" % type(bitstoappend))

        if bitstoappend:
            self.bitstring = self.bitstring + bitstoappend

    def toggle(self, index):
        pass

    def enable(self, index):
        if index > len(self.bitstring):
            raise IndexError("Flag index out of bounds")

        pre = self.bitstring[:index-1]
        flag = self.bitstring[index-1]
        post = self.bitstring[index:]

        self.bitstring = pre+"1"+post
        return 1

    def disable(self, index):
        if index > len(self.bitstring):
            raise IndexError("Flag index out of bounds")

        pre = self.bitstring[:index-1]
        flag = self.bitstring[index-1]
        post = self.bitstring[index:]

        self.bitstring = pre+"0"+post
        return 1


if __name__ == '__main__':
    print(0x0300000000FFFFD0)
    print(bin(0x0300000000FFFFD0))
    x = bitShifter(b'\x03\x00\x00\x11\x11\xff\xff\xd0')
    print('Value of:', x)

    op_mode = x.pop(8)

    print(x)
    
    j1 = x.pop(2)
    j2 = x.pop(2)
    j3 = x.pop(2)
    j4 = x.pop(2)

    dummy = x.pop(8)

    jrlr = x.pop(2)
    jelr = x.pop(2)
    jrrf = x.pop(2)
    jerf = x.pop(2)

    jrrr = x.pop(2)
    jerr = x.pop(2)
    jrlf = x.pop(2)
    jelf = x.pop(2)

    print(x)

    x.pop(16)

    print(x)
    print(str(x).split().reverse())

    park_brake = x.pop(2)
    ignition = x.pop(2)
    low_voltage = x.pop(2)
    other = x.pop(2)

    print(
        op_mode, 
        j1, 
        j2, 
        j3, 
        j4, 
        '-', 
        jrlr, 
        jelr, 
        jrrf, 
        jerf,
        jrrr,
        jerr,
        jrlf,
        jelf,
        park_brake,
        ignition,
        low_voltage,
        other
    )