import sys
from parser import DocumentParser


class BillsParser(DocumentParser):
    BILL_FIRST_READ = 'first reading'
    BILL_READING = 'bill read'
    BILL_PASS = 'bill passed'
    BILL_CONSIDERATION = 'bill considered'
    BILL_AMENDMENT = 'bill amendment'
    SPEAKER = 'speaker'


    BILL_INTRODUCED = r'The following Bill was presented and read the first time'
    BILL_READ = '^\s*The (.* Bill,[0-9]{4}) (duly|accordingly) read the (.*) time'
    BILL_PASSED = r'xxx'
    CONSIDERATION_STAGE = r'^[0-9.]*(.*)\s*-\s*At the Consideration Stage'
    AMENDMENT_PROPOSED = r'^(.*)\s*-\s*Amendment proposed\s*-\s*(.*)'
    AMENDMENT_PROPOSER = r'^\s*\((.*)\)\s*$'

    CUSTOM_PATTERNS = (
        (BILL_FIRST_READ, BILL_INTRODUCED),
        (BILL_READING, BILL_READ),
        (BILL_PASS, BILL_PASSED),
        (BILL_CONSIDERATION, CONSIDERATION_STAGE),
        (BILL_AMENDMENT, AMENDMENT_PROPOSED),
        (SPEAKER, AMENDMENT_PROPOSER)
    )

    NORMALIZATIONS = [
    ]

    def __init__(self, content):
        super(BillsParser, self).__init__(content)

    @classmethod
    def parse_body(cls, lines):
        for line in lines:
            print line


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
