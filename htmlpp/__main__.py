# -*- coding:utf-8 -*-
if __name__ == "__main__":
    from htmlpp.cli import render
    import sys

    class args:
        directory = "."
        file = sys.argv[1]
    render(args)
