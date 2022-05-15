import signal

def handler(signum, frame):
    pass


def set_sigint_ignore():
    signal.signal(signal.SIGINT, signal.SIG_IGN)

def set_sigint_allowed():
    signal.signal(signal.SIGINT, signal.default_int_handler)