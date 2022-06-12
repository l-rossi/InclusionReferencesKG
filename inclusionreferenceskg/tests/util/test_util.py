from inclusionreferenceskg.src.util.util import rom_to_dec


def test_rom_to_dec():
    test_set = [
        (1, "I"),
        (2, "II"),
        (3, "III"),
        (4, "IV"),
        (5, "V"),
        (6, "VI"),
        (7, "VII"),
        (8, "VIII"),
        (9, "IX"),
        (10, "X"),
        (11, "XI"),
        (12, "XII"),
        (1498, "MCDXCVIII"),
        (2573, "MMDLXXIII"),
        (132, "CXXXII"),
    ]

    for expected, inp in test_set:
        assert rom_to_dec(inp) == expected

