# -*- encoding: utf-8


class bcolors:
    info = '\033[0;34m'
    success = '\033[0;32m'
    ENDC = '\033[0m'


def _print(color, message, args):
    msg = message % args
    print('[' + getattr(bcolors, color) + color + bcolors.ENDC + '] ' + msg)


def info(message, *args):
    _print(color='info', message=message, args=args)


def success(message, *args):
    _print(color='success', message=message, args=args)
