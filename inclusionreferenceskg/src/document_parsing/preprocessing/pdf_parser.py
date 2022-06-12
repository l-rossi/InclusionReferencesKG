import tika.tika
from tika import parser


class PDFParser:
    tika.tika.TikaClientOnly = True

    def __init__(self):
        pass

    @staticmethod
    def parse(file_location: str) -> str:
        parsed = parser.from_file(file_location, headers={
            "X-Tika-PDFenableAutoSpace": "false"
        })
        return parsed["content"]

    @staticmethod
    def parse_to_file(input_file: str, output_file: str) -> None:
        inp = PDFParser.parse(input_file)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(inp)
