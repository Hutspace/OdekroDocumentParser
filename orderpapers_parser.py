import sys
import re
from datetime import datetime
from datetime import date
from parser import DocumentParser


class OrderPaperParser(DocumentParser):
    SELECTION_MARKER = 'NOTICE OF COMMITTEE SITTINGS'

    COMMITTEE_NAME_FORMAT = r"[A-Z]* COMMITTEE" # eg. BUSINESS COMMITTEE
    COMMITTEE_DATE_FORMAT = r"Date: ^[A-Za-z0-9,]* Time" # eg. Date:   Thursday, 6th June 2013
    COMMITTEE_TIME_FORMAT = r'Time:  ^[A-Za-z,0-9\-\s\/]*' #eg. Time:   9:00 a.m.
    COMMITTEE_VENUE_FORMAT = r'Venue:  ^[A-Za-z,0-9\-\s\/]*' #eg. Venue:  Committee Room 6
    COMMITTEE_AGENDA_FORMAT = r'Agenda: ^[A-Za-z,0-9\-\s\/]*' #eg. Agenda: To determine .....



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

        committee_name  = ''
        committee_date = ''
        committee_time = ''

        while len(lines):
            thekind, line, match = lines.pop(0)
            line_content = line.encode("utf-8")
            line_content = line_content.strip()

            if (thekind == cls.BLANK ):
                continue

            print "line content: %s " % line_content 

            if (line_content == cls.SELECTION_MARKER):
                # START PARSING SECTION
                valid = True
                continue


            if valid:

                matchObjectForCommitteeName = re.match( cls.COMMITTEE_NAME_FORMAT , line_content)
                matchObjectForCommitteeDateTimeVenueAndAgenda = re.match( r"Date: *" , line_content)

                if matchObjectForCommitteeName:   
                    committee_name = line_content.split(' ',1)[0]
                    print "name... %s " % committee_name


                if matchObjectForCommitteeDateTimeVenueAndAgenda:
                    committee_date_part = line_content.split('Time',1)[0]    
                    committee_date =   committee_date_part.split('Date:',1)[1]             

                    committee_time_part_array = line_content.split('Venue',1)
                    if len(committee_time_part_array)>1:
                        print committee_time_part_array
                        committee_time_part = committee_time_part_array[0]
                        committee_time_part =  committee_time_part.split('Time:',1)
                        if len(committee_time_part)>1:
                            committee_time = committee_time_part[0]
                        else:
                            committee_time = ''


                    committee_venue_part_array = line_content.split('Agenda:',1)
                    len_committee_venue = len(committee_venue_part_array)
                    if len_committee_venue > 1:
                        print len_committee_venue
                        committee_venue_part_array1 = committee_venue_part_array[0]
                        committee_venue_array  = committee_venue_part_array1.split('Venue:',1)

                        if len(committee_venue_array)>1:
                            committee_venue = committee_venue_array[1]
                        else:
                            committee_venue = ''

                    else:
                        committee_venue = ''

                    committee_agenda_array = line_content.split('Agenda:',1)
                    len_of_committee_agenda = len(committee_agenda_array) 
                    if len_of_committee_agenda > 1:
                        committee_agenda = committee_agenda_array[1]
                    else:
                        committee_agenda = ''

                if (thekind == cls.LINE or thekind == cls.BLANK or thekind == cls.PAGE_HEADER):
                    continue

                                                    
            else:
                # fallout
                pass

        if committee_name!='' and  committee_date!='':
            comittees.append(dict(committee_name=committee_name,
                            date=committee_date,
                            time=committee_time,
                            agenda=committee_agenda,
                            venue=committee_venue 
                            ))


        return comittees

    @classmethod
    def parse_body(cls, lines):
        entries = []
        ###committee name 
        committee_all = cls.parse_committee_info( list(lines) )
        for committee in committee_all:
            entries.append(committee)

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
