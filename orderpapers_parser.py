import sys
import re
from datetime import datetime
from datetime import date
from parser import DocumentParser


class OrderPaperParser(DocumentParser):
    KIND_COMMITEE_NAME = 'commitee'
    KIND_MEETING_TIME = 'meeting time'
    KIND_MEETING_DATE = 'meeting date'
    KIND_MEETING_VENUE = 'meeting venue'
    KIND_MEETING_AGENDA = 'meeting agenda'
    KIND_ALL_INFO = 'meeting info'

    DATE = r'Date:\s*(.*)'
    TIME = r'Time:\s*(.*)'
    AGENDA = r'Agenda:\s*(.*)'
    VENUE = r'Venue:\s*(.*)'
    ONE_LINE_INFO = r'%s\s*%s\s*%s\s*%s' % (DATE, TIME, VENUE, AGENDA)
    COMMITEE = r'\s*([A-Z]* COMMITTEE|COMMITTEE\s*(TO|OF|ON).*)'

    CUSTOM_PATTERNS = (
        (KIND_COMMITEE_NAME, COMMITEE),
        (KIND_ALL_INFO, ONE_LINE_INFO),
        (KIND_MEETING_DATE, DATE),
        (KIND_MEETING_TIME, TIME),
        (KIND_MEETING_VENUE, VENUE),
        (KIND_MEETING_AGENDA, AGENDA),
    )


    NORMALIZATIONS = [
            (r'([0-9]*)\s*(st|ST|nd|ND|rd|RD|th|TH)\n{1,2}', r'\1\2 ')
    ]

    SELECTION_MARKER = 'NOTICE OF COMMITTEE SITTINGS'
    COMMITTEE_NAME_FORMAT = r"[A-Z]* COMMITTEE" # eg. BUSINESS COMMITTEE

    def __init__(self, content):
        super(OrderPaperParser, self).__init__(content)

    @classmethod
    def format_committee_date(self, date_passed):
        date_actual= date_passed.split(',')[1].strip()
        date_parts = date_actual.split(' ')

        if len(date_parts)>=3:
            day_date =  date_parts[0].strip()
            month_date = date_parts[1]
            year_date = date_parts[2]
            day_date = day_date[:-2]
            #day_date = "O%s" %  day_date if int(day_date) <= 9 else day_date
            if re.match(r"\-", month_date ):
                date_as_timestamp = "No date"
            else:
                if len(day_date)!=0 and len(year_date)!=0 and len(month_date)>2:
                    date_full = "%s-%s" % ( day_date, year_date)
                    date_as_timestamp = datetime.strptime( date_full , "%d-%Y" ).strftime("%Y-%m-%d")
                elif len(day_date)==0 and len(month_date)>2 and len(year_date)==0:
                    date_full = "%s-%s-%s" % ( day_date, month_date, year_date)
                    date_as_timestamp = datetime.strptime( date_full , "%d-%B-%Y" ).strftime("%Y-%m-%d")
                elif len(day_date)==0 and len(month_date)>2 and len(year_date)==0:
                    date_full = "%s" % ( day_date )
                    date_as_timestamp = datetime.strptime( date_full , "%d" ).strftime("%Y-%m-%d")
                else:

                    if len(year_date) > 4:
                        date_full = "%s-%s" % ( day_date, month_date)
                        if len(day_date)==0 and len(month_date)>2:
                            date_as_timestamp = datetime.strptime( month_date , "%m" ).strftime("%Y-%m-%d")
                        elif len(day_date)!=0 and len(month_date)>2:
                            date_as_timestamp = datetime.strptime( date_full , "%d-%m" ).strftime("%Y-%m-%d")
                        elif re.match( r"[0-9]*[-][0-9]*",day_date):
                            date_as_timestamp = "No date"
                        else:
                            date_as_timestamp = "No date"
                    else:
                        date_full = "%s-%s-%s" % ( day_date, month_date, year_date)
                        date_as_timestamp = datetime.strptime( date_full , "%d-%B-%Y" ).strftime("%Y-%m-%d")

        else:
            day_date =  date_parts[0].strip()
            month_date = date_parts[1]
            year_date = datetime.now().year
            day_date = day_date[:-2]
            #day_date = "O%s" %  day_date if int(day_date) <= 9 else day_date
            date_full = "%s-%s" % ( day_date, month_date)

            date_as_timestamp = datetime.strptime( date_full , "%d-%B" ).strftime("%Y-%m-%d")

        if date_as_timestamp!="No date":
            dt_format = date_as_timestamp.split("-")
            string_to_use_as_timestamp = "datetime.datetime(%s, %s, %s )"  % ( dt_format[0] , dt_format[1],dt_format[2] )
            return  string_to_use_as_timestamp
        else:
            return date_as_timestamp

    @classmethod
    def parse_committee_info(cls, lines):
        thekind, line, match = None, None, None
        comittees = []
        valid = False

        committee_name  = ''
        committee_date = ''
        committee_time = ''

        while len(lines):
            thekind, line, match = lines.pop(0)
            line_content = line.strip()

            if (thekind == cls.BLANK ):
                continue

            if (line_content == cls.SELECTION_MARKER):
                # START PARSING SECTION
                valid = True
                continue


            if valid:
                matchObjectForCommitteeName = re.match( cls.COMMITTEE_NAME_FORMAT , line_content)
                matchObjectForCommitteeDateTimeVenueAndAgenda = re.match( r"Date: *" , line_content)

                if matchObjectForCommitteeName:
                    committee_name = line_content.split(' ',1)[0]


                if matchObjectForCommitteeDateTimeVenueAndAgenda:
                    committee_date_part = line_content.split('Time',1)[0]
                    committee_date =   committee_date_part.split('Date:',1)[1]
                    committee_date = cls.format_committee_date(committee_date)


                    committee_time_part_array = line_content.split('Venue',1)
                    if len(committee_time_part_array)>=1:
                        committee_time_part = committee_time_part_array[0]
                        committee_time_part =  committee_time_part.split('Time:',1)
                        if len(committee_time_part)>=2:
                            committee_time = committee_time_part[1].strip()
                        else:
                            committee_time = ''


                    committee_venue_part_array = line_content.split('Agenda:',1)
                    len_committee_venue = len(committee_venue_part_array)
                    if len_committee_venue > 1:
                        committee_venue_part_array1 = committee_venue_part_array[0]
                        committee_venue_array  = committee_venue_part_array1.split('Venue:',1)

                        if len(committee_venue_array)>1:
                            committee_venue = committee_venue_array[1].strip()
                        else:
                            committee_venue = ''

                    else:
                        committee_venue = ''

                    committee_agenda_array = line_content.split('Agenda:',1)
                    len_of_committee_agenda = len(committee_agenda_array)
                    if len_of_committee_agenda > 1:
                        committee_agenda = committee_agenda_array[1].replace(',','')
                    else:
                        committee_agenda = ''

                if (thekind == cls.LINE or thekind == cls.BLANK or thekind == cls.PAGE_HEADER):
                    continue

            else:
                # fallout
                pass


            if len(comittees)==0:
                continue

        if committee_name!='' and  committee_date!='':
            comittees.append(dict(committee_name=committee_name,
                            date=committee_date,
                            time=committee_time,
                            agenda=committee_agenda,
                            venue=committee_venue
                            ))

        return comittees


    @classmethod
    def parse_committee_meetings(cls, lines):
        thekind, line, match = None, None, None
        committees = []
        valid = False

        committee_name  = None
        committee_date = None
        committee_time = None
        committee_agenda = None
        committee_venue = None

        while len(lines):
            thekind, line, match = lines.pop(0)
            line_content = line.strip()

            if (thekind == cls.BLANK ):
                continue

            if (line_content == cls.SELECTION_MARKER):
                valid = True
                continue

            if valid:
                if thekind == cls.KIND_COMMITEE_NAME:
                    committee_name = match.group(1)

                if thekind == cls.KIND_MEETING_DATE:
                    committee_date = match.group(1)

                if thekind == cls.KIND_MEETING_TIME:
                    committee_time = match.group(1)

                if thekind == cls.KIND_MEETING_VENUE:
                    committee_venue = match.group(1)

                if thekind == cls.KIND_MEETING_AGENDA:
                    committee_agenda = match.group(1)
                    #handle multiline here - should go into own function
                    in_agenda = True
                    while (len(lines) > 0 and in_agenda):
                        thekind, line, match = lines.pop(0)
                        # print thekind, line
                        if thekind == cls.LINE:
                            committee_agenda += line
                        if thekind == cls.PAGE_HEADER or thekind == cls.HEADING:
                            in_agenda = False
                        if thekind == cls.KIND_COMMITEE_NAME:
                            in_agenda = False


                if thekind == cls.KIND_ALL_INFO:
                    # print thekind, line
                    committee_date = match.group(1)
                    committee_time = match.group(2)
                    committee_venue = match.group(3)
                    committee_agenda = match.group(4)
                    in_agenda = True
                    while (len(lines) > 0 and in_agenda):
                        thekind, line, match = lines.pop(0)
                        # print thekind, line
                        if thekind == cls.LINE:
                            committee_agenda += line
                        if thekind == cls.HEADING:
                            in_agenda = False
                        if thekind == cls.KIND_COMMITEE_NAME or thekind == cls.KIND_ALL_INFO:
                            lines.insert(0, (thekind, line, match))
                            in_agenda = False

                if committee_name is not None and \
                   committee_date is not None and \
                   committee_time is not None and \
                   committee_venue is not None and \
                   committee_agenda is not None:
                    committees.append(dict(committee_name=committee_name,
                                          date=committee_date,
                                          time=committee_time,
                                          agenda=committee_agenda,
                                          venue=committee_venue))
                    #reset
                    committee_date = None
                    committee_venue = None
                    committee_agenda = None
                    committee_time = None
                    committee_name = None

        return committees


    @classmethod
    def parse_body(cls, lines):
        entries = []
        entries = cls.parse_committee_meetings(lines)
        ###committee name
        #committee_all = cls.parse_committee_info( list(lines) )
        #for committee in committee_all:

        #    if len(committee)>2:
        #        entries.append(committee)

        return entries


def main(argv):
    print 'committee|date|time|venue|agenda'
    for filename in sys.stdin:
        handle = open(filename.strip(), 'r')
        content = handle.read()
        handle.close()

        p = OrderPaperParser(content)
        p.parse()
        data = p.output()
        for row in data:
            print '|'.join([row['committee_name'],
                            row['date'],
                            row['time'],
                            row['venue'],
                            row['agenda']
                            ])


if __name__ == "__main__":
    main(sys.argv)
