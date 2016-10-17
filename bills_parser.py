import sys
from datetime import datetime, date
from parser import DocumentParser


class BillsParser(DocumentParser):
    KIND_BILL_FIRST_READ = 'first reading'
    KIND_BILL_READING = 'bill read'
    KIND_BILL_PASS = 'bill passed'
    KIND_BILL_PRESENTER = 'presenter'
    KIND_BILL = 'bill'
    KIND_BILL_REFERRED = 'referred'

    BILL_NAME = r'(.*Bill,\s*[0-9]{4})'
    BILL_INTRODUCED = r'[0-9.]*\s*The following Bill[s]* (was|were) presented and read the first time.'
    BILL_READ = r'[0-9.]*\s*\s*The\s*(.*Bill,\s*[0-9]{4})\s*(duly|accordingly) (read (a|the) .* time)'
    BILL_PASSED = r'%s\s*and passed' % BILL_READ
    PRESENTER = r'^By the (.*) on behalf of (.*)$'
    REFERRAL = r'.* referred the Bill to (.*) for consideration and report'

    CUSTOM_PATTERNS = (
        (KIND_BILL_FIRST_READ, BILL_INTRODUCED),
        (KIND_BILL_PASS, BILL_PASSED),
        (KIND_BILL_READING, BILL_READ),
        (KIND_BILL_PRESENTER, PRESENTER),
        (KIND_BILL, BILL_NAME),
        (KIND_BILL_REFERRED, REFERRAL)
    )

    NORMALIZATIONS = []

    def __init__(self, content):
        super(BillsParser, self).__init__(content)

    @classmethod
    def parse_body(cls, lines):
        entries = []
        thekind, line, match = None, None, None
        timestamp = None

        while len(lines):
            thekind, line, match = lines.pop(0)
            if (thekind == cls.DATE):
                timestamp = date(int(match.group(4)),
                                 cls.MONTHS[match.group(3).lower()[:3]],
                                 int(match.group(2)))
                timestamp = datetime.combine(timestamp, datetime.min.time())

            if timestamp is None:
                continue

            if thekind == cls.KIND_BILL_FIRST_READ:
                presenter = None
                on_behalf = None
                bill = None
                multiple_bills = match.group(1) == 'were'

                first_read = True
                while (first_read):
                    if (len(lines) > 0):
                        thekind, line, match = lines.pop(0)
                    else:
                        break

                    if thekind == cls.KIND_BILL_PRESENTER:
                        presenter = match.group(1)
                        on_behalf = match.group(2)

                    if thekind == cls.KIND_BILL:
                        bill = match.group(1)

                    if bill is not None and presenter is not None:
                        entries.append(dict(sitting=timestamp,
                                            bill=bill,
                                            activity="first read",
                                            presenter=presenter,
                                            behalf=on_behalf))

                        if multiple_bills:
                            bill, presenter, on_behalf = None, None, None
                        else:
                            first_read = False

                    if multiple_bills and thekind == cls.LINE:
                        first_read = False

            if thekind == cls.KIND_BILL_READING:
                entries.append(dict(sitting=timestamp,
                                    bill=match.group(1),
                                    activity=match.group(3),
                                    presenter='',
                                    behalf=''))

            if thekind == cls.KIND_BILL_PASS:
                entries.append(dict(sitting=timestamp,
                                    bill=match.group(1),
                                    activity='%s and passed' % match.group(3),
                                    presenter='',
                                    behalf=''))

        return entries


def main(argv):
    print 'date|bill|activity|presenter|on behalf of'
    for filename in sys.stdin:
        handle = open(filename.strip(), 'r')
        content = handle.read()
        handle.close()

        p = BillsParser(content)
        p.parse()
        data = p.output()
        for row in data:
            print '%s|%s|%s|%s|%s' % (row['sitting'],
                                      row['bill'],
                                      row['activity'],
                                      row['presenter'],
                                      row['behalf'])

if __name__ == "__main__":
    main(sys.argv)
