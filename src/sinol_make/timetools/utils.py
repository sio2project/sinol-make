class noquote(str):
    pass


def _argquote(s):
    if isinstance(s, noquote):
        return str(s)
    if isinstance(s, list):
        s = ' '.join(map(_argquote, s))
    return "'" + s.replace("'", "'\\''") + "'"


def shellquote(s):
    if isinstance(s, list):
        return " ".join(map(_argquote, s))
    else:
        return s
