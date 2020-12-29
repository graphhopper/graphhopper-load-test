def green_bg(text):
    return _color("green_bg", text)


def red_bg(text):
    return _color("red_bg", text)


def red(text):
    return _color("red", text)


def green(text):
    return _color("green", text)


def _color(color, text):
    mapping = {
        "red": "0;31;40",
        "green": "0;32;40",
        "green_bg": "6;30;42",
        "red_bg": "6;30;41",
    }
    code = mapping[color]
    return "\x1b[" + code + "m" + text + "\x1b[0m"
