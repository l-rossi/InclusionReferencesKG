from tika import parser


class PDFParser:

    @staticmethod
    def parse(file_location: str, auto_space=False) -> str:
        """
        Reads the content of a PDF file.

        :param file_location: The location of the file.
        :param auto_space: Configures Tika to use autos space. For some reason this seems to be necessary for \
        documents with a double column.
        :return: The text content of the file.
        """
        parsed = parser.from_file(file_location, headers={
            "X-Tika-PDFenableAutoSpace": "true" if auto_space else "false",
            "X-Tika-PDFsortByPosition": "false"
        })
        return parsed["content"]

    @staticmethod
    def parse_to_file(input_file: str, output_file: str, auto_space=False) -> None:
        inp = PDFParser.parse(input_file, auto_space)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(inp)
