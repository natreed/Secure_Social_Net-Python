import sys

from pip._vendor.html5lib.constants import EOF


def flush_input():
    c = ""
    while c != EOF:
        c = sys.stdin.read()


