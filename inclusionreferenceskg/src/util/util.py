from __future__ import annotations


def rom_to_dec(num: str) -> int:
    """
    Converts a roman numeral to a number. This function has undefined
    behaviour if the roman numeral is malformed.
    :param num: The roman numeral.
    :return: The integer representation of the roman numeral.
    """

    prim_con = {
        None: 0,
        "I": 1,
        "V": 5,
        "X": 10,
        "L": 50,
        "C": 100,
        "D": 500,
        "M": 1000,
    }

    acc = 0
    last_prim = None
    for c in num[::-1]:
        if prim_con[last_prim] > prim_con[c]:
            acc -= prim_con[c]
        else:
            acc += prim_con[c]
        last_prim = c

    return acc


def alph_to_dec(alph):
    """
    Translates an alphabetic numbering to its number representation.

    :param alph: The alphabetic numbering.
    :return: The corresponding int.
    """

    if alph == "ii":
        return 10

    if len(alph) != 1:
        raise ValueError(f"Expected alphanumeric numbering to be 'ii' or have length 1. Was: '{alph}'.")

    return ord(alph) - 96
