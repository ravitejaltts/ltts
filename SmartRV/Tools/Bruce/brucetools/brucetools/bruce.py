
"""brucetools.bruce: provides entry point main()."""

__version__ = "0.1.13"

def bruce():
    print("My module")

import sys

def main():
    print("Executing bruce version %s." % __version__)
    print("List of argument strings: %s" % sys.argv[1:])
    bruce()

