import sys
import re
from datetime import datetime
from datetime import date
from parser import DocumentParser


class OrderPaperParser(DocumentParser):
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
            day_date = "O%s" %  day_date if int(day_date) <= 9 else day_date
            date_full = "%s-%s-%s" % ( day_date, month_date, year_date)             
        else:
            day_date =  date_parts[0].strip()
            month_date = date_parts[1]
            year_date = datetime.now().year             
            day_date = day_date[:-2]
            day_date = "O%s" %  day_date if int(day_date) <= 9 else day_date
            date_full = "%s-%s" % ( day_date, month_date) 



        return date_full    

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
    def parse_body(cls, lines):
        entries = []
        ###committee name 
        committee_all = cls.parse_committee_info( list(lines) )
        for committee in committee_all:

            if len(committee)>2:
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
