import sys
import re
from datetime import datetime
from datetime import date
from parser import DocumentParser


class MotionsParser(DocumentParser):
    KIND_MOTION_TITLE = 'motion'
    KIND_MOTION_PROPOSERS = 'proposers'
    KIND_MOTION_PROPOSERS_PARTIAL = 'proposers partial'
    KIND_MOTION_RESOLUTION = 'resolution'
    KIND_MOTION_RESOLUTION2 = 'resolution2'

    MOTION = r'^\d+\.\s*MOTION'
    MOTION_MOVED_BY = r'\(Moved\s*(?:on|by)\s*(.*)\s*and\s*seconded\s*by\s*(.*)\)'
    MOTION_MOVER = r'\s*\(((?:Minister|Chairman).* )\)'
    MOTION_MOVED_PARTIAL = r'\(Moved\s*(?:on|by).*'
    RESOLUTION = r'\d+\.\s*The\s*House\s*accordingly\s*(.*)'
    RESOLUTION2 = r'\s*THIS HONOURABLE HOUSE HEREBY RESOLVE AS FOLLOWS:\s*'
    MOTION_AGREED = r'.*Question put and (motion .*)'

    CUSTOM_PATTERNS = (
        (KIND_MOTION_TITLE, MOTION),
        (KIND_MOTION_PROPOSERS, MOTION_MOVED_BY),
        (KIND_MOTION_PROPOSERS, MOTION_MOVER),
        (KIND_MOTION_PROPOSERS_PARTIAL, MOTION_MOVED_PARTIAL),
        (KIND_MOTION_RESOLUTION, RESOLUTION),
        (KIND_MOTION_RESOLUTION2, RESOLUTION2),
        (KIND_MOTION_RESOLUTION, MOTION_AGREED),
    )

    NORMALIZATIONS = []

    def __init__(self, content):
        super(MotionsParser, self).__init__(content)

    @classmethod
    def adjust_parsed(cls, motion):

        pass

    @classmethod
    def parse_motions(cls, lines):
        thekind, line, match = None, None, None
        motions = []
        valid = False
        timestamp = None
        motion = None
        pastProposers = True

        while len(lines):
            thekind, line, match = lines.pop(0)
            # print thekind, line
            if timestamp is None and thekind == cls.DATE:
                timestamp = date(int(match.group(4)),
                                 cls.MONTHS[match.group(3).lower()[:3]],
                                 int(match.group(2)))
                timestamp = datetime.combine(timestamp, datetime.min.time())

            if thekind == cls.KIND_MOTION_TITLE:
                # print 'MOTION'
                if valid:
                    cls.adjust_parsed(motion)
                    motions.append(motion)

                motion = dict(date=timestamp,
                              motion='',
                              moved_by='',
                              seconded_by='',
                              resolution='')
                valid = True
                pastProposers = False
                continue

            if valid:
                if thekind == cls.LINE and not pastProposers:
                    # print thekind, line
                    motion['motion'] = ' '.join([motion['motion'], line])

                if thekind == cls.KIND_MOTION_PROPOSERS:
                    motion['moved_by'] = match.group(1)
                    motion['seconded_by'] = match.group(2)
                    pastProposers = True

                if thekind == cls.KIND_MOTION_RESOLUTION:
                    # print thekind, line
                    motion['resolution'] = match.group(1)
                    # DONE PARSING MOION
                    motions.append(motion)
                    pastProposers = False
                    valid = False

        return motions

    @classmethod
    def parse_body(cls, lines):
        return cls.parse_motions(lines)


def main(argv):
    fields = ['date',
              'motion',
              'moved_by',
              'seconded_by',
              'resolution'
              ]
    print '|'.join(fields)
    for filename in sys.stdin:
        # print filename
        handle = open(filename.strip(), 'r')
        content = handle.read()
        handle.close()

        p = MotionsParser(content)
        p.parse()
        data = p.output()
        for row in data:
            print '|'.join([str(row[label]) for label in fields])


if __name__ == "__main__":
    main(sys.argv)
