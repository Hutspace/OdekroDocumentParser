import sys
from parser import DocumentParser


class BillsParser(DocumentParser):
    BILL_FIRST_READ = 'first reading'
    BILL_READING = 'bill read'
    BILL_PASS = 'bill passed'

    BILL_INTRODUCED = r'The following Bill was presented and read the first time'
    BILL_READ = '^\s*The (.* Bill,[0-9]{4}) (duly|accordingly) read the (.*) time (and passed) '
    BILL_PASSED = r''

    CUSTOM_PATTERNS = (
        (BILL_FIRST_READ, BILL_INTRODUCED),
        (BILL_READING, BILL_READ),
        (BILL_PASS, BILL_PASSED),
    )

    NORMALIZATIONS = [
    ]

    def __init__(self, content):
        super(BillsParser, self).__init__(content)

    @classmethod
    def parse_body(cls, lines):
        pass


def main(argv):
    for filename in sys.stdin:
        handle = open(filename.strip(), 'r')
        content = handle.read()
        handle.close()

        p = BillsParser(content)
        p.parse()
        print p.output()


if __name__ == "__main__":
    main(sys.argv)
