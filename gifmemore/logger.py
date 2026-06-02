_verbose = False


def set_verbose(enabled: bool):
    global _verbose
    _verbose = enabled


def is_verbose() -> bool:
    return _verbose


def log(*args, **kwargs):
    if _verbose:
        print(*args, **kwargs)
