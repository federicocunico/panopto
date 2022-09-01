from distutils.spawn import find_executable


def is_token_valid(token: str):
    if not token:
        return False
    valid = True
    for v in token:
        if not (v.isalpha() or v.isdigit()):
            valid = False
            break
    return valid


def is_tool(name):
    """Check whether `name` is on PATH."""

    return find_executable(name) is not None
