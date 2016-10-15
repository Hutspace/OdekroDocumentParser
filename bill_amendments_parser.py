import sys
from datetime import datetime, date
from parser import DocumentParser


class BillAmendmentsParser(DocumentParser):
    BILL_CONSIDERATION = 'bill considered'
    BILL_AMENDMENT = 'bill amendment'
    SPEAKER = 'speaker'
    QUESTION_PUT = 'question put'
    DEFERRED = 'debate deferred'
    WITHDRAWN = 'withdrawn'

    CONSIDERATION_STAGE = r'^[0-9.]*(.*)\s*\n*.*\s*At (.*) Consideration Stage'
    AMENDMENT_PROPOSED = r'^(.*)\s*-\s*Amendment proposed\s*-\s*(.*)'
    AMENDMENT_PROPOSER = r'^\s*\((.*)\)\s*$'
    QUESTION_AMENDMENT = r'.*Question put and amendment (.*) to\s*'
    DEBATE_DEFERRED = r'Debate deferred'
    AMENDMENT_WITHDRAWN = r'.*Amendment withdrawn'

    CUSTOM_PATTERNS = (
        (BILL_CONSIDERATION, CONSIDERATION_STAGE),
        (BILL_AMENDMENT, AMENDMENT_PROPOSED),
        (SPEAKER, AMENDMENT_PROPOSER),
        (QUESTION_PUT, QUESTION_AMENDMENT),
        (DEFERRED, DEBATE_DEFERRED),
        (WITHDRAWN, AMENDMENT_WITHDRAWN),
    )

    NORMALIZATIONS = []

    def __init__(self, content):
        super(BillsAmendmentParser, self).__init__(content)

    @classmethod
    def parse_body(cls, lines):
        entries = []
        kind, line, match = None, None, None
        timestamp = None
        bill, target, change, person, resolution = None, None, None, None, None
        wrapup = False

        while len(lines):
            kind, line, match = lines.pop(0)

            if (kind == cls.DATE):
                timestamp = date(int(match.group(4)),
                                 cls.MONTHS[match.group(3).lower()[:3]],
                                 int(match.group(2)))
                timestamp = datetime.combine(timestamp, datetime.min.time())

            if timestamp is None:
                continue

            # print kind, line
            if kind == cls.BILL_CONSIDERATION:
                bill = match.group(1)
                # reset amendments
                # print bill
                target, change, person = None, None, None
                wrapup = False

            if kind == cls.BILL_AMENDMENT:
                target = match.group(1)
                change = match.group(2)
                kind, line, match = lines.pop(0)
                while(kind != cls.SPEAKER):
                    if (kind == cls.LINE):
                        change += ' %s' % line
                    if (len(lines) > 0):
                        kind, line, match = lines.pop(0)
                    else:
                        break
                # print '%s -- %s' % (target, change)
                # continue

            if kind == cls.SPEAKER:
                person = match.group(1)
                # print person

            if kind == cls.QUESTION_PUT:
                resolution = match.group(1)
                # print resolution
                wrapup = True

            if kind == cls.DEBATE_DEFERRED:
                resolution = 'debate deferred'
                # print resolution
                wrapup = True

            if wrapup:
                entries.append(dict(sitting=timestamp,
                                    bill=bill,
                                    change=target,
                                    change_to=change,
                                    speaker=person,
                                    vote=resolution)
                               )
                target, change, person, resolution = None, None, None, None
                wrapup = False

        return entries


def main(argv):
    for filename in sys.stdin:
        handle = open(filename.strip(), 'r')
        content = handle.read()
        handle.close()

        p = BillAmendmentsParser(content)
        p.parse()
        data = p.output()
        for row in data:
            print '%s|%s|%s|%s|%s|%s' % (row['sitting'],
                                         row['bill'],
                                         row['change'],
                                         row['change_to'],
                                         row['speaker'],
                                         row['vote'])

if __name__ == "__main__":
    main(sys.argv)
