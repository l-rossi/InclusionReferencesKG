from inclusionreferenceskg.src.reference_detection.regex_reference_detector import RegexReferenceDetector


def test_detect():
    test_cases = [
        ("awd Article 1 dw", ["Article 1"]),
        ("dw Article 1(1) dwa", ["Article 1(1)"]),
        ("af Articles 1, 2 and 3 dwa", ["Articles 1, 2 and 3"]),
        ("d Articles 8, 11, 25 to 39 and 42 and 43 d", ["Articles 8, 11, 25 to 39 and 42 and 43"]),
    ]

    matcher = RegexReferenceDetector()

    for text, result in test_cases:
        assert matcher.detect(text) == result
