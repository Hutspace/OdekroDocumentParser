import sys
import re
from datetime import datetime
from datetime import date
from parser import DocumentParser


class OrderPaperParser(DocumentParser):
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
        super(OrderPaperParser, self).__init__(content)

    @classmethod
    def parse_rollcall(cls, kind, lines):
        thekind, line, match = None, None, None
        members = []
        valid = False
        timestamp = None

        while len(lines):
            thekind, line, match = lines.pop(0)
            line = line.encode("utf-8")
            if (thekind == cls.DATE):
                timestamp = date(int(match.group(4)),
                                 cls.MONTHS[match.group(3).lower()[:3]],
                                 int(match.group(2)))
                timestamp = datetime.combine(timestamp, datetime.min.time())

            if not valid and thekind != kind:
                continue

            if not valid and thekind == kind:
                # START PARSING SECTION
                valid = True
                continue

            if valid:
                if thekind == cls.ROLLCALL_PERSON:
                    member = re.sub('[0-9.]', '', line[: line.rfind('(')]).strip()
                    constituency = line[line.rfind('('):]
                    name_slug = re.sub('[,.\(\)\[\]]', ' ', member).split()
                    members.append(dict(mp=member,
                                    constituency=constituency,
                                    name_slug=name_slug,
                                    timestamp=timestamp))

                if (thekind == cls.LINE or thekind == cls.BLANK or thekind == cls.PAGE_HEADER):
                    continue

                if thekind != cls.BLANK and thekind != cls.ROLLCALL_PERSON:
                    # DONE PARSING SECTION
                    valid = False
                    break
            else:
                # fallout
                pass

        return timestamp, members


    @classmethod
    def parse_committee_info(cls, lines):
        thekind, line, match = None, None, None
        comittees = []
        valid = False
        timestamp = None

        while len(lines):
            thekind, line, match = lines.pop(0)
            line = line.encode("utf-8")
            print "start here "
            print "line here %s " % line 
            print "kind here %s " % thekind 
            print "match here %s " % match 

        return comittees

    @classmethod
    def parse_body(cls, lines):
        entries = []
        ###committee name 
        committee_all = cls.parse_committee_info( list(lines) )
        for committee in committee_all:
            entries.append(committee)

        """
        timestamp, present = cls.parse_rollcall(cls.ROLLCALL_PRESENT, list(lines))
        for member in present:
            member['status'] = 'P'
            entries.append(member)          
        timestamp, absent = cls.parse_rollcall(cls.ROLLCALL_ABSENT, list(lines))
        for member in absent:
            member['status'] = 'A'
            entries.append(member)
        timestamp, permission = cls.parse_rollcall(cls.ROLLCALL_ABSENTP, list(lines))
        for member in permission:
            member['status'] = 'AP'
            entries.append(member)
        """    
        return entries


def main(argv):
    for filename in sys.stdin:
        handle = open(filename.strip(), 'r')
        content = handle.read()
        handle.close()

        p = OrderPaperParser(content)
        p.parse()
        print p.output()


if __name__ == "__main__":
    main(sys.argv)
