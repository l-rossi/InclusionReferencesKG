from inclusionreferenceskg.src.reference_detection.regex_reference_detector import RegexReferenceDetector


def test_detect():
    test_cases = [
        ("awd Article 1 dw", ["Article 1"]),
        ("dw Article 1(1) dwa", ["Article 1(1)"]),
        ("af Articles 1, 2 and 3 dwa", ["Articles 1, 2 and 3"]),
        ("d Articles 8, 11, 25 to 39 and 42 and 43 d", ["Articles 8, 11, 25 to 39 and 42 and 43"]),
        ("The obligation laid down in paragraph 1 of this Article shall not apply ", ["paragraph 1 of this Article"]),
        ("by the Member States when carrying out activities which fall within the scope of Chapter 2 of Title V of the TEU", ["Chapter 2 of Title V of the TEU"]),
        ("subsidiarity as set out in Article 5 of the Treaty on European Union (TEU)", ["Article 5 of the Treaty on European Union (TEU)"]),
        ("This Regulation shall be without prejudice to the application of Directive 2000/31/EC, in particular of the liability rules of intermediary service providers in Articles 12 to 15 of that Directive.", ["This Regulation", "Directive 2000/31/EC", "Articles 12 to 15 of that Directive"]),
        ("Regulation (EC) No 45/2001 applies. Regulation (EC) No 45/2001 and other Union legal acts applicable to such processing of personal data shall be adapted to the principles and rules of this Regulation in accordance with Article 98", ["Regulation (EC) No 45/2001", "Regulation (EC) No 45/2001", "this Regulation", "Article 98"]),
        ("ipursuant to Article 45(3) of this Regulation and decisions adopted on the basis of Article 25(6) of Directive 95/46/EC;", ["Article 45(3) of this Regulation", "Article 25(6) of Directive 95/46/EC"]),
    ]

    matcher = RegexReferenceDetector()

    for text, result in test_cases:
        assert matcher.detect(text) == result
