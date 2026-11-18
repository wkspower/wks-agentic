"""Validation shared by the units of the pet shop."""


def is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def positive_int(value, what):
    if not is_int(value) or value <= 0:
        raise ValueError(f"{what} must be an integer greater than 0")
    return value


def non_empty_str(value, what):
    if not isinstance(value, str) or value == "":
        raise ValueError(f"{what} must be a non-empty string")
    return value
