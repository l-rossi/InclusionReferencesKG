from inclusionreferenceskg.src.reference_detection.regex_reference_detector import RegexReferenceDetector

if __name__ == "__main__":

    detector = RegexReferenceDetector()

    with open("./resources/eu_documents/gdpr.txt") as f:
        references = detector.detect(f.read())

    print("\n".join(ref.text_content + ";" + str(ref.start) for ref in references))
