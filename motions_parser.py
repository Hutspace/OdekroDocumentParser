import sys
import re
from datetime import datetime
from datetime import date
from parser import DocumentParser


class MotionsParser(DocumentParser):
    KIND_MOTION_TITLE = 'motion'
    KIND_MOTION_PROPOSERS = 'proposers'
    KIND_MOTION_RESOLUTION = 'resolution'

    MOTION = r'^\d+\.\s*MOTION'
    MOTION_MOVED_BY = r'\(Moved\s*by\s*(.*)\s*and\s*seconded\s*by\s*(.*)\)'
    RESOLUTION = r'\d+\.\s*The\s*House\s*accordingly\s*(.*)'

    CUSTOM_PATTERNS = (
        (KIND_MOTION_TITLE, MOTION),
        (KIND_MOTION_PROPOSERS, MOTION_MOVED_BY),
        (KIND_MOTION_RESOLUTION, RESOLUTION),
    )

    NORMALIZATIONS = []

    def __init__(self, content):
        super(MotionsParser, self).__init__(content)

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
            if timestamp is None and thekind == cls.DATE:
                timestamp = date(int(match.group(4)),
                                 cls.MONTHS[match.group(3).lower()[:3]],
                                 int(match.group(2)))
                timestamp = datetime.combine(timestamp, datetime.min.time())

            if thekind == cls.KIND_MOTION_TITLE:
                if valid:
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
                # print thekind, line
                if thekind == cls.LINE and not pastProposers:
                    motion['motion'] = ' '.join([motion['motion'], line])

                if thekind == cls.KIND_MOTION_PROPOSERS:
                    motion['moved_by'] = match.group(1)
                    motion['seconded_by'] = match.group(2)
                    pastProposers = True

                if thekind == cls.KIND_MOTION_RESOLUTION:
                    motion['resolution'] = match.group(1)
                    # DONE PARSING MOION
                    motions.append(motion)
                    pastProposers = False
                    valid = False

        return motions

    @classmethod
    def parse_body(cls, lines):
        return cls.parse_motions(lines)

    @classmethod
    def normalise_line_breaks(cls, content):
        return content


def main(argv):
    fields = ['date',
              'motion',
              'moved_by',
              'seconded_by',
              'resolution'
              ]
    print '|'.join(fields)
    for filename in sys.stdin:
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
