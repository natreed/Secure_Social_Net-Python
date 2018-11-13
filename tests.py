from subprocess import call
import sys
import os

def first_test():
    os.write(sys.stdout, b'python3 SSN.py')


if __name__ == '__main__':
    first_test()