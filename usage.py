# -*- coding: utf-8 -*-

"""
MIT License

Copyright (c) 2020 devsecurity.io <dns-tools@devsecurity.io>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import sys
import glob

def rchop(string, suffix):
    if string.endswith(suffix):
        return string[:-len(suffix)]
    
    return string


def main():
    sys.stderr.write("Usage: docker run --rm -i -v <local volume>:<container volume> devsecurity/dns-tools:<tag> <command> <command parameters>\n\n")
    sys.stderr.write("Tags:\n")
    sys.stderr.write("\tlatest\n\n")

    sys.stderr.write("Commands:\n")

    command_files = glob.glob("*.py")
    command_files.remove("usage.py")
    commands = [ rchop(x, ".py") for x in command_files ]

    for command in commands:
        sys.stderr.write("\t%s\n" % command)

if __name__ == "__main__":
    main()
