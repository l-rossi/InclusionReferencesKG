
class RegexUtil:
    number = r"(?:[1-9][0-9]*)"
    alpha = r"(?:\((?:[a-z]|ii)\))"
    paragraph = fr"(?:\({number}\))"
    ordinal = "(?:first|second|third|fourth|fifth|sixth)"
    roman = r"(?-i:[IXV]+)"  # This is a really bad pattern and only matches the first few roman numerals and also alot of illegal ones.


    # limited conjunctions, "as well as" is present in the GDPR
    conjunction = fr"(?:and|or)"
