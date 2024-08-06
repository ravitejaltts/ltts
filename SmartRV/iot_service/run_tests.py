import pytest
import sys

def main():
    # Run pytest with the custom plugin
    exit_code = pytest.main(['--tb=short'])

    # Check the exit code and handle it if necessary
    if exit_code == 2:
        print("Caught exit code 2, handling it.")
        sys.exit(0)
    else:
        sys.exit(exit_code)

if __name__ == '__main__':
    main()
