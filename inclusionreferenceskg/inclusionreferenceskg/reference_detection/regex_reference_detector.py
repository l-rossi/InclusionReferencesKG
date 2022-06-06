import re


class RegexReferenceDetector:
    """
    Reference detector based on regular expressions.
    """

    def detect(self):
        articles_pattern = re.compile(r"Articles ([1-9][0-9]*)(?:(?:, ([1-9][0-9]*))* and ([1-9][0-9]*))?")
        article_pattern = re.compile(r"Article ([1-9][0-9]*)")

        para_pattern = re.compile(article_pattern.pattern + r"\(([1-9][0-9]*)\)")
        paras_pattern = re.compile(article_pattern.pattern + r"(\([1-9][0-9]*\))(?:(?:, (\([1-9][0-9]*\)))* and (\([1-9][0-9]*\)))?")

        point_pattern = re.compile(r"Point \(([a-z])\) of" + para_pattern.pattern)
        points_pattern = re.compile(r"Point \(([a-z])\) of" + para_pattern.pattern)




        paragraph_number = re.compile(r"\(([1-9][0-9]*)\)")
        article_number = re.compile(r"([1-9][0-9]*)")

        single_article_specifier = re.compile(r"Article " + article_number.pattern)
        single_paragraph_specifier = re.compile(single_article_specifier.pattern + paragraph_number.pattern)
        multi_paragraph_specifier = re.compile(
            single_paragraph_specifier.pattern + r"\(\(, " + paragraph_number.pattern + r"\)* and " + paragraph_number.pattern + r"\)?")

        article_specifier = re.compile(
            single_article_specifier.pattern + r"(?:"
            + r", " + article_number.pattern + r"*"
            + r" and" + article_number.pattern + r")?")

        print(article_specifier.pattern)

        print(re.match(single_article_specifier, "Article 1"))
        print(re.match(article_specifier, "Article 1, 2"))
        print(re.match(article_specifier, "Article 1 and 2"))
        print(re.match(article_specifier, "Article 1, 2 and 3"))
        print(re.match(article_specifier, "Article 1(1) and (2)"))


if __name__ == "__main__":
    RegexReferenceDetector().detect()
