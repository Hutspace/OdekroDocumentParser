import sys
import re
from datetime import datetime
from datetime import date
from parser import DocumentParser


class AttendanceParser(DocumentParser):
    ROLLCALL_PRESENT = 'present'
    ROLLCALL_ABSENT = 'absent'
    ROLLCALL_ABSENTP = 'absent with permission'
    ROLLCALL_PERSON = 'rollcall person'

    VP_PRESENT = r'^\s*[0-9.]*\s*The following Hon. Members were present:\s*$'
    VP_ABSENT = r'^\s*[0-9.]*\s*The following Hon. Members were absent:\s*$'
    VP_ABSENT_W_PERM = r'^\s*[0-9.]*\s*The following Hon. Members were absent with permission:\s*$'
    VP_CONSTITUENCY = r'\([A-Za-z,\-\s\/]*\)'
    VP_MEMBER = r'^\s*[0-9.]*\s*([^0-9\*:;{}"]{2,80})\s*$'
    VP_MEMBER2 = r'^\s*([^0-9\*:;{}"]{2,80})\s*(%s)$' % VP_CONSTITUENCY

    CUSTOM_PATTERNS = (
        (ROLLCALL_PRESENT, VP_PRESENT),
        (ROLLCALL_ABSENT, VP_ABSENT),
        (ROLLCALL_ABSENTP, VP_ABSENT_W_PERM),
        (ROLLCALL_PERSON, VP_MEMBER2)
    )

    NORMALIZATIONS = [
        (r'\n\n(%s)' % VP_CONSTITUENCY, r'\1')
    ]

    def __init__(self, content):
        super(AttendanceParser, self).__init__(content)

    @classmethod
    def parse_rollcall(cls, kind, lines):
        thekind, line, match = None, None, None
        members = []
        valid = False
        timestamp = None

        while len(lines):
            thekind, line, match = lines.pop(0)

            if (thekind == cls.DATE):
                timestamp = date(int(match.group(4)),
                                 cls.MONTHS[match.group(3).lower()[:3]],
                                 int(match.group(2)))
                timestamp = datetime.combine(timestamp, datetime.min.time())

            if not valid and (thekind == cls.BLANK or thekind == cls.PAGE_HEADER):
                continue

            if thekind == kind:
                # print "#### PARSING SECTION %s"%kind
                valid = True
                continue

            if valid:
                print thekind
                print line.encode("utf-8")

                if thekind == cls.ROLLCALL_PERSON:
                    member = re.sub('[0-9.]', '', line[: line.rfind('(')]).strip()
                    constituency = line[line.rfind('('):]
                    name_slug = re.sub('[,.\(\)\[\]]', ' ', member).split()
                    # print '{0} : {1} : {2} '.format(member, constituency, name_slug)
                    members.append(dict(mp=member,
                                    constituency=constituency,
                                    name_slug=name_slug,
                                    timestamp=timestamp))

                if (thekind == cls.LINE or thekind == cls.BLANK or thekind == cls.PAGE_HEADER):
                    # print 'LOG %s:: %s'%(kind, line)
                    pass

                if thekind != cls.BLANK and thekind != cls.ROLLCALL_PERSON:
                    # print 'END Kind: {0} - {1}'.format(thekind, line)
                    # print "#### DONE PARSING SECTION %s"%kind
                    valid = False
                    break
            else:
                # print 'FELLOUT Kind: {0} - {1}'.format(thekind,line)
                pass

        return timestamp, members

    @classmethod
    def parse_body(cls, lines):
        entries = []
        timestamp, present = cls.parse_rollcall(cls.ROLLCALL_PRESENT, lines)
        for member in present:
            member['status'] = 'P'
            entries.append(member)
        print 'Present: %d' % (len(present))
        timestamp, absent = cls.parse_rollcall(cls.ROLLCALL_ABSENT, lines)
        for member in absent:
            member['status'] = 'A'
            entries.append(member)
        timestamp, permission = cls.parse_rollcall(cls.ROLLCALL_ABSENTP, lines)
        for member in permission:
            member['status'] = 'AP'
            entries.apend(member)
        print 'Present: %d Absent: %d Absent With Permision: %d Total: %d' % (len(present), len(absent), len(permission), len(present + absent + permission))
        return entries


def main(argv):
    for filename in sys.stdin:
        print filename
        handle = open(filename.strip(), 'r')
        content = handle.read()
        handle.close()

        p = AttendanceParser(content)
        p.parse()
        #print p.output()


if __name__ == "__main__":
    main(sys.argv)
