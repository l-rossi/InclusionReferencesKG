import os

from inclusionreferenceskg.src.document_parsing.preprocessing.pdf_parser import PDFParser

if __name__ == "__main__":
    root = "./resources/eu_documents"
    for file_name in os.listdir(root):
        file = os.path.join(root, file_name)

        if not os.path.isfile(file):
            continue

        if not file.endswith(".pdf"):
            continue

        out_file = ".".join(file.split(".")[:-1]) + ".txt"
        if os.path.exists(out_file):
            continue

        PDFParser.parse_to_file(file, out_file)
